import pandas as pd
import joblib
import shap
import random
import argparse
import matplotlib.pyplot as plt
from model_config import FEATURES_TO_EXCLUDE, MANUAL_CATEGORICAL_FEATURES
from feature_names import FEATURE_NAME_MAP
from data_loader import load_and_concat_csvs


# --- 1. Configuration ---
TARGET_COLUMN = 'SpeedIndex'
MODEL_FILE_NAME = 'aislow_desktop.pkl'
TEST_CSV_FILE = 'testpages.csv'  # Used when ANALYSIS_MODE = 'test'
ETSY_CSV_FILE = 'etsypages.csv'  # Used when ANALYSIS_MODE = 'etsy'

# Parse command line arguments
parser = argparse.ArgumentParser(description='Analyze page speed and identify performance issues.')
parser.add_argument(
    '--mode',
    choices=['median', 'test', 'etsy'],
    default='test',
    help='Analysis mode: "median" (median page from training data), "test" (random from testpages.csv), or "etsy" (random from etsypages.csv). Default: test'
)
args = parser.parse_args()
ANALYSIS_MODE = args.mode

# --- 2. Load Model and Training Data ---
#print("Loading model and training data...")
try:
    model = joblib.load(MODEL_FILE_NAME)
except FileNotFoundError:
    print(f"ERROR: Could not find model file '{MODEL_FILE_NAME}'.")
    exit()

# Always load training data for SHAP background context
#print("Loading training data for SHAP background...")
df_background = load_and_concat_csvs(verbose=False)
#print(f"  Loaded {len(df_background)} training pages for background context")

# Calculate and display average SpeedIndex
avg_speedindex = df_background[TARGET_COLUMN].mean()
median_speedindex = df_background[TARGET_COLUMN].median()
print(f"Training data: {len(df_background)} pages")
print(f"  Average SpeedIndex: {avg_speedindex:.0f} ms")
print(f"  Median SpeedIndex: {median_speedindex:.0f} ms")

# --- 3. Load Page to Analyze ---
if ANALYSIS_MODE == 'test':
    #print(f"\nAnalysis Mode: TEST")
    #print(f"Loading test page from '{TEST_CSV_FILE}'...")
    try:
        df_test = pd.read_csv(TEST_CSV_FILE)
        #print(f"  Found {len(df_test)} test pages")
        
        # Select a random page from test data
        random.seed()  # Use system time for true randomness
        test_row_index = random.randint(0, len(df_test) - 1)
        
        # Extract the single page we want to analyze
        df_to_analyze = df_test.iloc[[test_row_index]].copy()
        real_speedindex = df_to_analyze.iloc[0][TARGET_COLUMN]
        page_url = df_to_analyze.iloc[0]['page']
        
        #print(f"\nSelected RANDOM test page (Row {test_row_index}, SI: {real_speedindex:.0f} ms)")
        #print(f"URL: {page_url}")
        
    except FileNotFoundError:
        print(f"ERROR: Could not find file '{TEST_CSV_FILE}'.")
        exit()
elif ANALYSIS_MODE == 'etsy':
    #print(f"\nAnalysis Mode: ETSY")
    #print(f"Loading Etsy page from '{ETSY_CSV_FILE}'...")
    try:
        df_etsy = pd.read_csv(ETSY_CSV_FILE)
        #print(f"  Found {len(df_etsy)} Etsy pages")
        
        # Select a random page from Etsy data
        random.seed()  # Use system time for true randomness
        etsy_row_index = random.randint(0, len(df_etsy) - 1)
        
        # Extract the single page we want to analyze
        df_to_analyze = df_etsy.iloc[[etsy_row_index]].copy()
        real_speedindex = df_to_analyze.iloc[0][TARGET_COLUMN]
        page_url = df_to_analyze.iloc[0]['page']
        
        #print(f"\nSelected RANDOM Etsy page (Row {etsy_row_index}, SI: {real_speedindex:.0f} ms)")
        #print(f"URL: {page_url}")
        
    except FileNotFoundError:
        print(f"ERROR: Could not find file '{ETSY_CSV_FILE}'.")
        exit()
else:
    #print(f"\nAnalysis Mode: MEDIAN")
    # Use training data to find median page
    df_to_analyze = df_background.copy()
    median_speedindex_value = df_to_analyze[TARGET_COLUMN].median()
    row_index_to_explain = (df_to_analyze[TARGET_COLUMN] - median_speedindex_value).abs().idxmin()
    
    # Extract just that one row
    df_to_analyze = df_to_analyze.iloc[[row_index_to_explain]].copy()
    real_speedindex = df_to_analyze.iloc[0][TARGET_COLUMN]
    page_url = df_to_analyze.iloc[0]['page']
    
    #print(f"\nSelected MEDIAN page from training data (Row {row_index_to_explain}, SI: {real_speedindex:.0f} ms)")
    #print(f"Dataset median SI: {median_speedindex_value:.0f} ms")
    #print(f"URL: {page_url}")

# --- 4. Prepare Data ---
#print("\nPreparing data...")

# Build list of columns to drop (same as training)
columns_to_drop = [TARGET_COLUMN, 'page'] + FEATURES_TO_EXCLUDE
columns_to_drop = [col for col in columns_to_drop if col in df_background.columns]

# Prepare background data for SHAP
X_background = df_background.drop(columns=columns_to_drop)

# Prepare the single page to analyze
X_to_analyze = df_to_analyze.drop(columns=[col for col in columns_to_drop if col in df_to_analyze.columns])

# Calculate p25 benchmarks BEFORE converting to categories (so we capture all numeric features)
p25_metrics = {}
for col in X_background.columns:
    # Only for numeric columns (before category conversion)
    if X_background[col].dtype in ['int64', 'float64']:
        p25_metrics[col] = X_background[col].quantile(0.25)

# Convert categories (must be identical to training) for BOTH datasets
for col in MANUAL_CATEGORICAL_FEATURES:
    if col in X_background.columns:
        X_background[col] = X_background[col].astype('category')
    if col in X_to_analyze.columns:
        X_to_analyze[col] = X_to_analyze[col].astype('category')

# --- 5. Run SHAP Analysis ---
#print("Calculating SHAP values...")
#print("(This can take a moment)")

# Create explainer with just the model (SHAP will calculate its own baseline)
explainer = shap.TreeExplainer(model)

# Run SHAP on the background data to get all explanations, then extract the one we want
if ANALYSIS_MODE == 'test':
    # For test mode, we need to run SHAP on the test page
    # But we want the baseline from training data, so we need to be clever
    # Run on both background (for baseline) and test page
    all_shap = explainer(X_background)  # Get baseline from training
    test_shap = explainer(X_to_analyze)  # Explain test page
    explanation = test_shap[0]
else:
    # For median mode, run on full background and extract the median row
    # Find which row in X_background corresponds to our median page
    median_row_in_background = df_background.index.get_loc(df_to_analyze.index[0])
    all_shap = explainer(X_background)
    explanation = all_shap[median_row_in_background]

predicted_speedindex = model.predict(X_to_analyze)[0]
base_value = explanation.base_values

# Combine feature names, their data values, and their SHAP impact
features = []
for name, impact, value in zip(X_to_analyze.columns, explanation.values, explanation.data):
    features.append({'name': name, 'impact': impact, 'value': value})

# Sort by the *absolute* impact
features.sort(key=lambda x: abs(x['impact']), reverse=True)
problems = [f for f in features if f['impact'] > 50] # 50ms is the threshold for significance
strengths = [f for f in features if f['impact'] < 50]

# Helper function to get friendly names
def get_name(name):
    return FEATURE_NAME_MAP.get(name, name)

# --- 6. Generate SHAP Waterfall Plot ---
# Generate a unique filename based on the page URL
page_slug = page_url.replace('https://', '').replace('http://', '').replace('/', '_').replace('?', '_').replace('&', '_')[:100]
output_filename = f"shap_waterfall_{page_slug}.png"

# Create the waterfall plot
plt.figure(figsize=(10, 8))
shap.plots.waterfall(explanation, max_display=15, show=False)
plt.tight_layout()
plt.savefig(output_filename, dpi=150, bbox_inches='tight')
plt.close()
#print(f"SHAP waterfall plot saved to: {output_filename}")

# --- 7. Print Text Report ---
print("\n\n---------------------------------------")
print("---------     EH, I SLOW?     ---------")
print("---------------------------------------")
print(f"Page: {page_url}")
print(f"SpeedIndex: {real_speedindex:.0f}ms (actual)")
print(f"Predicted SpeedIndex: {predicted_speedindex:.0f}ms")
error_ms = abs(real_speedindex - predicted_speedindex)
print(f"Prediction error: {error_ms:.0f}ms")

print("\n--- Top Problems (Areas for Improvement) ---")
if not problems:
    print("No significant problems found.")
else:
    for f in problems[:5]:
        print(f"  * {get_name(f['name'])} = {f['value']:,.0f}")
        print(f"    └─ Impact: +{f['impact']:.0f} ms")

print("\n--- Top Strengths (What's Working Well) ---")
if not strengths:
    print("No significant strengths found.")
else:
    for f in strengths[:3]:
        print(f"  * {get_name(f['name'])} = {f['value']:,.0f}")
        print(f"    └─ Impact: {f['impact']:.0f} ms")

# --- 8. "What-If" Simulation ---
print("\n--- What-If Simulation ---")

if not problems:
    print("No problems to simulate.")
    exit()

top_problem = problems[0]
top_problem_name = top_problem['name']
top_problem_value = top_problem['value']

X_modified = X_to_analyze.copy()
scenario_text = ""

# Get the model's "Before" prediction (use the one we already calculated)
pred_before = predicted_speedindex

# Generic "what-if" logic: Improve the top problem to "good" benchmark (p25)
if top_problem_name in p25_metrics:
    p25_value = p25_metrics[top_problem_name]
    
    # Only simulate if the current value is worse than p25 (higher for metrics where more = worse)
    # We'll assume most metrics follow "higher = worse" pattern (bytes, time, counts)
    if top_problem_value > p25_value:
        scenario_text = f"Improve '{get_name(top_problem_name)}' from {top_problem_value:,.0f} to 'good' benchmark {p25_value:,.0f} (25th percentile)"
        X_modified[top_problem_name] = p25_value
    else:
        print(f"Top problem '{get_name(top_problem_name)}' is already at or better than the 'good' benchmark.")
        print("No simulation needed.")
        scenario_text = ""
else:
    # For categorical or non-numeric features
    print(f"Cannot simulate '{get_name(top_problem_name)}' (not a numeric feature).")
    print("Skipping simulation.")
    scenario_text = ""


# Run the simulation if a scenario was defined
if scenario_text:
    print(f"  #1 problem is {get_name(top_problem_name)}")
    print(f"  {scenario_text}")
    
    # Get the "After" prediction
    pred_after = model.predict(X_modified)[0]
    
    savings = pred_before - pred_after
    
    if savings > 0:
        print(f"  Estimated SpeedIndex Improvement: {savings:.0f} ms")
        print(f"  └─ (from {pred_before:.0f}ms to {pred_after:.0f}ms)")
    else:
        print(f"  No significant improvement predicted (Est: {savings:.0f} ms).")

