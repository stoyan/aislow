import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
import joblib
import time
import warnings
from model_config import FEATURES_TO_EXCLUDE, MANUAL_CATEGORICAL_FEATURES
from data_loader import load_and_concat_csvs
from feature_names import FEATURE_NAME_MAP

# Suppress numpy warnings from correlation calculations with zero-variance features
warnings.filterwarnings('ignore', category=RuntimeWarning, module='numpy')

# --- Configuration ---
TARGET_COLUMN = 'SpeedIndex'
MODEL_FILE_NAME = 'aislow_desktop.pkl'

print(f"Starting model training process...")

# 1. Load and Combine Data
df = load_and_concat_csvs(remove_duplicates=True, verbose=True)

# Check for missing target values
print(f"Checking for missing values in '{TARGET_COLUMN}'...")
missing_target = df[TARGET_COLUMN].isna().sum()
if missing_target > 0:
    print(f"  Warning: Found {missing_target} missing values in target. Removing these rows...")
    df = df.dropna(subset=[TARGET_COLUMN])
else:
    print(f"  No missing values in target column")

# 2. Separate Features (X) and Target (y)
print(f"Separating features (X) and target '{TARGET_COLUMN}' (y)...")
y = df[TARGET_COLUMN]

# Build list of columns to drop
columns_to_drop = [TARGET_COLUMN, 'page'] + FEATURES_TO_EXCLUDE

# Filter out any excluded features that don't exist in the dataframe
columns_to_drop = [col for col in columns_to_drop if col in df.columns]

# Report what's being dropped
excluded_found = [col for col in FEATURES_TO_EXCLUDE if col in df.columns]
excluded_not_found = [col for col in FEATURES_TO_EXCLUDE if col not in df.columns]

print(f"Dropping 'page' (URL) and target '{TARGET_COLUMN}' from features...")
if excluded_found:
    print(f"Excluding {len(excluded_found)} additional feature(s): {', '.join(excluded_found)}")
if excluded_not_found:
    print(f"  Note: {len(excluded_not_found)} excluded feature(s) not found in data: {', '.join(excluded_not_found)}")

X = df.drop(columns=columns_to_drop)

# 3. Preprocessing
print("Converting specified columns to 'category' type...")

# Loop through your manual list and convert columns
features_converted = []
features_not_found = []
for col in MANUAL_CATEGORICAL_FEATURES:
    if col in X.columns:
        X[col] = X[col].astype('category')
        features_converted.append(col)
    else:
        features_not_found.append(col)

if features_converted:
    print(f"  Converted: {features_converted}")
if features_not_found:
    print(f"  Warning: Did not find: {features_not_found}")

print(f"\nFeatures (X) shape: {X.shape}")
print(f"Target (y) shape: {y.shape}")

# 4. Create Training and Test Sets
print("Splitting data into training and test sets (80% train / 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Initialize and Train the Model
print("Initializing LGBMRegressor model...")
model = lgb.LGBMRegressor(
    random_state=42,
    n_estimators=500,      # Maximum number of boosting rounds
    learning_rate=0.05,    # Lower learning rate for better generalization
    verbosity=-1           # Suppress warnings
)

print("Starting model training... (This should be fast!)")
start_time = time.time()

# Pass the list of categorical feature names directly to the model
model.fit(X_train, y_train,
          eval_set=[(X_test, y_test)],
          eval_metric='l2', # Mean Squared Error
          callbacks=[lgb.early_stopping(stopping_rounds=10, verbose=False)],
          categorical_feature=features_converted  # Tell LightGBM the category names
         )

end_time = time.time()

print(f"\n--- Training Complete ---")
print(f"Training took {end_time - start_time:.2f} seconds.")
print(f"Best iteration: {model.best_iteration_}")

# 6. Evaluate Model Score
score = model.score(X_test, y_test)
print(f"Model R-squared score on test data: {score:.4f}")

# 7. Feature Importance with Correlation Analysis
print(f"\nTop 13 Most Important Features:")
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'split_count': model.feature_importances_,  # How many times used to split
    'gain': model.booster_.feature_importance(importance_type='gain')  # Total improvement in loss
})

# Add normalized percentages
feature_importance['split_pct'] = 100 * feature_importance['split_count'] / feature_importance['split_count'].sum()
feature_importance['gain_pct'] = 100 * feature_importance['gain'] / feature_importance['gain'].sum()

# Add correlation with target (shows direction of relationship)
correlations = []
for feature in feature_importance['feature']:
    try:
        corr = df[feature].corr(df[TARGET_COLUMN])
        # Handle NaN (occurs when feature has zero variance or is all NaN)
        if pd.isna(corr):
            corr = 0.0
    except Exception:
        corr = 0.0
    correlations.append(corr)
feature_importance['correlation'] = correlations

# Sort by gain (usually more meaningful for understanding impact)
feature_importance = feature_importance.sort_values('gain', ascending=False)

print(f"{'Feature':<40} {'Splits':<8} {'Gain %':<9} {'Correlation':<12} {'Impact':<15}")
print("-" * 95)
for idx, row in feature_importance.head(13).iterrows():
    corr = row['correlation']
    # Interpret correlation direction
    if corr > 0.3:
        impact = "↑↑ SLOWS page"
    elif corr > 0.1:
        impact = "↑ slows page"
    elif corr > -0.1:
        impact = "~ neutral"
    elif corr > -0.3:
        impact = "↓ speeds up"
    else:
        impact = "↓↓ SPEEDS UP"
    
    # Get friendly name, fallback to original if not found
    friendly_name = FEATURE_NAME_MAP.get(row['feature'], row['feature'])
    
    print(f"{friendly_name:<40} {row['split_count']:<8.0f} {row['gain_pct']:<9.2f} {corr:<12.3f} {impact:<15}")

print("\nNote: Correlation shows LINEAR relationship with SpeedIndex.")
print("      Positive = higher values → higher SpeedIndex (slower)")
print("      Negative = higher values → lower SpeedIndex (faster)")
print("      The model may capture more complex non-linear patterns.")

# 8. Save the Trained Model
print(f"\nSaving trained model to '{MODEL_FILE_NAME}'...")
joblib.dump(model, MODEL_FILE_NAME)

print("---")
print("Success! Trained model saved.")