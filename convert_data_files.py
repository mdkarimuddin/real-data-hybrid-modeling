"""
Convert data files from GitHub repositories to CSV format

This script converts Excel (.xlsx) and MATLAB (.mat) files to CSV
for use with the hybrid modeling pipeline.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

try:
    import scipy.io
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("⚠️  scipy not available - cannot convert .mat files")

def convert_excel_to_csv(excel_path, output_dir="data"):
    """Convert Excel file to CSV."""
    try:
        df = pd.read_excel(excel_path)
        output_path = Path(output_dir) / f"{excel_path.stem}.csv"
        df.to_csv(output_path, index=False)
        print(f"  ✅ Converted {excel_path.name} to {output_path}")
        print(f"     Shape: {df.shape}, Columns: {list(df.columns)[:5]}")
        return output_path
    except Exception as e:
        print(f"  ❌ Error converting {excel_path.name}: {e}")
        return None

def convert_mat_to_csv(mat_path, output_dir="data"):
    """Convert MATLAB .mat file to CSV."""
    if not SCIPY_AVAILABLE:
        print(f"  ⚠️  Skipping {mat_path.name} (scipy not available)")
        return None
    
    try:
        mat_data = scipy.io.loadmat(str(mat_path))
        
        # Find data arrays (skip metadata keys starting with __)
        data_keys = [k for k in mat_data.keys() if not k.startswith('__')]
        
        if not data_keys:
            print(f"  ⚠️  No data arrays found in {mat_path.name}")
            return None
        
        converted_files = []
        for key in data_keys:
            data = mat_data[key]
            
            # Handle different data structures
            if isinstance(data, np.ndarray):
                if len(data.shape) == 2:
                    # 2D array - save as CSV
                    df = pd.DataFrame(data)
                    output_path = Path(output_dir) / f"{mat_path.stem}_{key}.csv"
                    df.to_csv(output_path, index=False, header=False)
                    print(f"  ✅ Extracted {key} from {mat_path.name} to {output_path}")
                    print(f"     Shape: {data.shape}")
                    converted_files.append(output_path)
                elif len(data.shape) == 1:
                    # 1D array - save as single column
                    df = pd.DataFrame(data, columns=[key])
                    output_path = Path(output_dir) / f"{mat_path.stem}_{key}.csv"
                    df.to_csv(output_path, index=False)
                    print(f"  ✅ Extracted {key} from {mat_path.name} to {output_path}")
                    converted_files.append(output_path)
        
        return converted_files if converted_files else None
        
    except Exception as e:
        print(f"  ❌ Error converting {mat_path.name}: {e}")
        return None

def find_and_convert_data_files(search_dir=".", output_dir="data"):
    """Find and convert all data files in the directory tree."""
    search_path = Path(search_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print("Searching for data files...")
    print("=" * 60)
    
    excel_files = list(search_path.rglob("*.xlsx"))
    mat_files = list(search_path.rglob("*.mat"))
    
    print(f"Found {len(excel_files)} Excel file(s)")
    print(f"Found {len(mat_files)} MATLAB file(s)")
    print()
    
    converted_count = 0
    
    # Convert Excel files
    if excel_files:
        print("Converting Excel files:")
        for excel_file in excel_files:
            if 'bioreactor' in str(excel_file).lower() or 'data' in excel_file.name.lower():
                result = convert_excel_to_csv(excel_file, output_dir)
                if result:
                    converted_count += 1
        print()
    
    # Convert MATLAB files
    if mat_files:
        print("Converting MATLAB files:")
        for mat_file in mat_files:
            if 'data' in mat_file.name.lower() or 'batch' in mat_file.name.lower():
                result = convert_mat_to_csv(mat_file, output_dir)
                if result:
                    if isinstance(result, list):
                        converted_count += len(result)
                    else:
                        converted_count += 1
        print()
    
    print("=" * 60)
    print(f"✅ Conversion complete! {converted_count} file(s) converted")
    print(f"   Output directory: {output_path.absolute()}")
    
    # List converted files
    csv_files = list(output_path.glob("*.csv"))
    if csv_files:
        print(f"\nConverted CSV files:")
        for csv_file in csv_files:
            size = csv_file.stat().st_size / 1024  # KB
            print(f"  - {csv_file.name} ({size:.1f} KB)")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert data files to CSV")
    parser.add_argument("--search-dir", default=".", help="Directory to search for files")
    parser.add_argument("--output-dir", default="data", help="Output directory for CSV files")
    
    args = parser.parse_args()
    
    find_and_convert_data_files(args.search_dir, args.output_dir)

