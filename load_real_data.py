"""
Load and Preprocess Real Bioprocess Data

This script loads real bioprocess data from files and prepares it for
hybrid modeling analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


# Column name mapping - UPDATE THESE TO MATCH YOUR DATA FORMAT
COLUMN_MAPPING = {
    'time': 'time',           # Time column (hours)
    'biomass': 'biomass',     # Biomass concentration (X)
    'substrate': 'substrate', # Substrate concentration (S)
    'product': 'product',     # Product concentration (P)
    'experiment_id': 'experiment_id'  # Experiment identifier (optional)
}

# Alternative column names (will be tried if primary names not found)
ALTERNATIVE_NAMES = {
    'time': ['Time', 't', 'hour', 'hours', 'time_h', 'timepoint'],
    'biomass': ['X', 'biomass', 'cell_density', 'cells', 'VCD', 'viable_cell_density'],
    'substrate': ['S', 'substrate', 'glucose', 'carbon_source', 'feed'],
    'product': ['P', 'product', 'protein', 'mAb', 'antibody', 'titer'],
    'experiment_id': ['experiment', 'exp_id', 'run', 'batch', 'condition']
}


def find_column(df: pd.DataFrame, target: str) -> Optional[str]:
    """
    Find column name in dataframe using mapping and alternatives.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    target : str
        Target column type (e.g., 'time', 'biomass')
    
    Returns:
    --------
    column_name : str or None
        Found column name or None
    """
    # Try primary mapping
    if COLUMN_MAPPING[target] in df.columns:
        return COLUMN_MAPPING[target]
    
    # Try alternatives
    for alt_name in ALTERNATIVE_NAMES.get(target, []):
        if alt_name in df.columns:
            return alt_name
    
    return None


def load_data_from_file(filepath: str) -> pd.DataFrame:
    """
    Load data from CSV or Excel file.
    
    Parameters:
    -----------
    filepath : str
        Path to data file
    
    Returns:
    --------
    df : pd.DataFrame
        Loaded dataframe
    """
    filepath = Path(filepath)
    
    if filepath.suffix == '.csv':
        df = pd.read_csv(filepath)
    elif filepath.suffix in ['.xlsx', '.xls']:
        df = pd.read_excel(filepath)
    else:
        raise ValueError(f"Unsupported file format: {filepath.suffix}")
    
    return df


def preprocess_data(df: pd.DataFrame, 
                   remove_outliers: bool = True,
                   outlier_threshold: float = 3.0) -> pd.DataFrame:
    """
    Preprocess data: clean, normalize, handle missing values.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Raw dataframe
    remove_outliers : bool
        Whether to remove outliers
    outlier_threshold : float
        Z-score threshold for outlier detection
    
    Returns:
    --------
    df_clean : pd.DataFrame
        Cleaned dataframe
    """
    df = df.copy()
    
    # Find required columns
    time_col = find_column(df, 'time')
    biomass_col = find_column(df, 'biomass')
    substrate_col = find_column(df, 'substrate')
    product_col = find_column(df, 'product')
    
    if not time_col or not biomass_col:
        raise ValueError("Required columns (time, biomass) not found!")
    
    # Select and rename columns
    columns_to_keep = [time_col, biomass_col]
    new_names = ['time', 'biomass']
    
    # Substrate is optional - estimate from biomass if missing
    if substrate_col:
        columns_to_keep.append(substrate_col)
        new_names.append('substrate')
    
    if product_col:
        columns_to_keep.append(product_col)
        new_names.append('product')
    
    # Keep experiment_id if present
    exp_id_col = find_column(df, 'experiment_id')
    if exp_id_col:
        columns_to_keep.append(exp_id_col)
        new_names.append('experiment_id')
    
    df = df[columns_to_keep].copy()
    df.columns = new_names
    
    # Remove rows with missing required values
    df = df.dropna(subset=['time', 'biomass'])
    
    # Fill missing product values with 0 if column exists
    if 'product' in df.columns:
        df['product'] = df['product'].fillna(0)
    
    # If substrate is missing, estimate it from biomass growth
    if 'substrate' not in df.columns:
        print("  ⚠️  Substrate column not found - estimating from biomass growth")
        # Estimate substrate: start high, decrease with biomass growth
        initial_substrate = 10.0  # g/L (typical initial glucose)
        # Simple model: S = S0 - (X - X0) / Yxs
        Yxs_estimate = 0.5  # Estimated yield
        X0 = df['biomass'].iloc[0]
        df['substrate'] = initial_substrate - (df['biomass'] - X0) / Yxs_estimate
        df['substrate'] = df['substrate'].clip(lower=0)  # Ensure non-negative
    
    # Ensure time is numeric
    df['time'] = pd.to_numeric(df['time'], errors='coerce')
    df = df.dropna(subset=['time'])
    
    # Ensure concentrations are numeric and non-negative
    for col in ['biomass', 'substrate', 'product']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if col == 'substrate':
                # Substrate can be estimated, so handle NaN
                df[col] = df[col].fillna(0)
            df[col] = df[col].clip(lower=0)  # Ensure non-negative
    
    # Remove outliers if requested
    if remove_outliers:
        for col in ['biomass', 'substrate', 'product']:
            if col in df.columns:
                z_scores = np.abs((df[col] - df[col].mean()) / (df[col].std() + 1e-8))
                df = df[z_scores < outlier_threshold]
    
    # Sort by time
    df = df.sort_values('time').reset_index(drop=True)
    
    return df


def load_real_data(data_dir: str = "data",
                  file_pattern: str = "*.csv",
                  combine_experiments: bool = True) -> Tuple[np.ndarray, np.ndarray, Dict]:
    """
    Load and combine real bioprocess data from files.
    
    Parameters:
    -----------
    data_dir : str
        Directory containing data files
    file_pattern : str
        File pattern to match (e.g., "*.csv", "*.xlsx")
    combine_experiments : bool
        Whether to combine multiple experiments into one dataset
    
    Returns:
    --------
    data : np.ndarray
        Combined data array of shape (n_samples, n_features)
        Features: [biomass, substrate, product]
    time : np.ndarray
        Time points
    metadata : dict
        Metadata about the data (experiment IDs, file names, etc.)
    """
    data_dir = Path(data_dir)
    
    # Find all data files
    if '*' in file_pattern or '?' in file_pattern:
        # Use glob pattern
        files = list(data_dir.glob(file_pattern))
    else:
        # Single file or exact match
        if (data_dir / file_pattern).exists():
            files = [data_dir / file_pattern]
        else:
            # Try as glob pattern anyway
            files = list(data_dir.glob(file_pattern))
    
    if not files:
        raise FileNotFoundError(f"No files found matching {file_pattern} in {data_dir}")
    
    print(f"Found {len(files)} data file(s)")
    
    all_data = []
    all_times = []
    experiment_ids = []
    file_names = []
    
    for filepath in files:
        print(f"Loading: {filepath.name}")
        df = load_data_from_file(filepath)
        df = preprocess_data(df)
        
        # Extract data
        if 'experiment_id' in df.columns:
            exp_ids = df['experiment_id'].values
        else:
            exp_ids = [filepath.stem] * len(df)
        
        # Create data array - ensure we have [biomass, substrate, product]
        required_cols = ['biomass', 'substrate']
        if 'product' in df.columns:
            required_cols.append('product')
        
        # Check all required columns exist
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns after preprocessing: {missing_cols}")
        
        data_array = df[required_cols].values
        
        # If product is missing, add zero column
        if 'product' not in df.columns:
            data_array = np.column_stack([
                data_array,
                np.zeros(len(df))
            ])
        
        all_data.append(data_array)
        all_times.append(df['time'].values)
        experiment_ids.extend(exp_ids)
        file_names.extend([filepath.name] * len(df))
    
    # Combine all experiments
    if combine_experiments:
        data = np.vstack(all_data)
        time = np.hstack(all_times)
    else:
        # Keep separate (for per-experiment analysis)
        data = all_data
        time = all_times
    
    metadata = {
        'n_experiments': len(files),
        'n_samples': len(data) if combine_experiments else sum(len(d) for d in all_data),
        'experiment_ids': experiment_ids,
        'file_names': file_names,
        'files_loaded': [f.name for f in files]
    }
    
    print(f"\nData Summary:")
    print(f"  Total samples: {metadata['n_samples']}")
    print(f"  Experiments: {metadata['n_experiments']}")
    print(f"  Features: [Biomass, Substrate, Product]")
    print(f"  Data shape: {data.shape if combine_experiments else [d.shape for d in data]}")
    
    return data, time, metadata


if __name__ == "__main__":
    # Example usage
    import sys
    
    data_dir = "data"
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    
    try:
        data, time, metadata = load_real_data(data_dir)
        print("\n✅ Data loaded successfully!")
        print(f"\nFirst 5 samples:")
        print(f"Time: {time[:5]}")
        print(f"Data:\n{data[:5]}")
        
        # Save preprocessed data
        output_dir = Path("inputs")
        output_dir.mkdir(exist_ok=True)
        
        np.save(output_dir / "data.npy", data)
        np.save(output_dir / "time.npy", time)
        
        import json
        with open(output_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✅ Preprocessed data saved to {output_dir}/")
        
    except Exception as e:
        print(f"\n❌ Error loading data: {e}")
        import traceback
        traceback.print_exc()

