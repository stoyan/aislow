import pandas as pd
import sys

# Default CSV files to load
CSV_FILES = [
    'fast 6k - rank under 10k si 500 to 2500.csv',
    'fast 5k - rank under 50k si 500 to 2500.csv',
    'slow 13k - rank under 100K si 4500 to 20k.csv'
]

def load_and_concat_csvs(csv_files=None, remove_duplicates=False, verbose=False):
    """
    Load and concatenate multiple CSV files into a single DataFrame.
    
    Args:
        csv_files: List of CSV file paths to load. If None, uses CSV_FILES constant.
        remove_duplicates: If True, remove duplicate URLs based on 'page' column
        verbose: If True, print detailed loading information
    
    Returns:
        pd.DataFrame: Combined DataFrame from all CSV files
    """
    if csv_files is None:
        csv_files = CSV_FILES
    
    if verbose:
        print(f"Loading and combining {len(csv_files)} CSV files...")
    
    dfs = []
    for csv_file in csv_files:
        try:
            if verbose:
                print(f"  Loading '{csv_file}'...")
            temp_df = pd.read_csv(csv_file)
            if verbose:
                print(f"    Loaded {len(temp_df)} rows")
            dfs.append(temp_df)
        except FileNotFoundError:
            print(f"ERROR: Could not find file '{csv_file}'.")
            if verbose:
                print("Please make sure the script is in the same folder as your data files.")
            sys.exit(1)
    
    if verbose:
        print(f"\nCombining all datasets...")
    
    df_combined = pd.concat(dfs, ignore_index=True)
    
    if verbose:
        print(f"Successfully combined into {len(df_combined)} total rows and {len(df_combined.columns)} columns.")
    
    # Check for and remove duplicate URLs if requested
    if remove_duplicates and 'page' in df_combined.columns:
        if verbose:
            print(f"Checking for duplicate URLs...")
        initial_rows = len(df_combined)
        df_combined = df_combined.drop_duplicates(subset=['page'], keep='first')
        duplicates_removed = initial_rows - len(df_combined)
        if verbose:
            if duplicates_removed > 0:
                print(f"  Removed {duplicates_removed} duplicate URLs")
            else:
                print(f"  No duplicates found")
    
    return df_combined

