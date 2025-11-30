"""
Extract time series data from MATLAB .mat files (improved version)

Handles nested MATLAB structures properly.
"""

import sys
import numpy as np
from pathlib import Path

try:
    import scipy.io
    SCIPY_AVAILABLE = True
except ImportError:
    print("❌ scipy not available")
    sys.exit(1)

def extract_nested_data(obj, max_depth=5, current_depth=0):
    """Recursively extract numeric arrays from nested MATLAB structures."""
    if current_depth > max_depth:
        return None
    
    # If it's already a numpy array
    if isinstance(obj, np.ndarray):
        # If it's a simple numeric array
        if obj.dtype.kind in ['f', 'i', 'u']:  # float, int, uint
            return obj.flatten()
        # If it's object array, recurse
        elif obj.dtype == object:
            results = []
            for item in obj.flat:
                extracted = extract_nested_data(item, max_depth, current_depth + 1)
                if extracted is not None:
                    results.append(extracted)
            if results:
                # Try to combine if same length
                try:
                    return np.array(results).flatten()
                except:
                    return results[0] if results else None
    
    # If it's a MATLAB struct
    if hasattr(obj, '_fieldnames') or (hasattr(obj, 'dtype') and obj.dtype.names):
        # Try to access as structured array
        if hasattr(obj, 'dtype') and obj.dtype.names:
            results = {}
            for field in obj.dtype.names:
                try:
                    field_data = obj[field] if isinstance(obj, np.ndarray) else getattr(obj, field, None)
                    if field_data is not None:
                        extracted = extract_nested_data(field_data, max_depth, current_depth + 1)
                        if extracted is not None:
                            results[field] = extracted
                except:
                    continue
            return results if results else None
    
    # Try as scipy mat_struct
    if 'mat_struct' in str(type(obj)):
        results = {}
        for attr in dir(obj):
            if not attr.startswith('_'):
                try:
                    field_data = getattr(obj, attr)
                    extracted = extract_nested_data(field_data, max_depth, current_depth + 1)
                    if extracted is not None:
                        results[attr] = extracted
                except:
                    continue
        return results if results else None
    
    return None

def extract_batch_data_v2(mat_file, output_dir="data"):
    """Extract time series data from batch MATLAB files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n📁 Processing: {Path(mat_file).name}")
    
    try:
        # Load with different options
        mat_data = scipy.io.loadmat(str(mat_file), struct_as_record=False, squeeze_me=True)
        
        # Find batch key
        batch_key = None
        for key in mat_data.keys():
            if not key.startswith('__') and 'batch' in key.lower():
                batch_key = key
                break
        
        if not batch_key:
            print(f"   ⚠️  No batch data found")
            return None
        
        batch_data = mat_data[batch_key]
        
        # Extract nested data
        extracted = extract_nested_data(batch_data)
        
        if not extracted:
            print(f"   ⚠️  Could not extract data")
            return None
        
        # Handle different extraction results
        if isinstance(extracted, dict):
            # Map field names to standard names
            data_dict = {}
            
            # Time
            for key in ['age', 'time', 't']:
                if key in extracted:
                    arr = extracted[key]
                    if isinstance(arr, np.ndarray) and len(arr) > 0:
                        data_dict['time'] = arr.flatten()
                        break
            
            # Biomass (VCD)
            for key in ['vcd', 'biomass', 'x', 'cell_density']:
                if key in extracted:
                    arr = extracted[key]
                    if isinstance(arr, np.ndarray) and len(arr) > 0:
                        data_dict['biomass'] = arr.flatten()
                        break
            
            # Product
            for key in ['product', 'p']:
                if key in extracted:
                    arr = extracted[key]
                    if isinstance(arr, np.ndarray) and len(arr) > 0:
                        data_dict['product'] = arr.flatten()
                        break
            
            # Substrate/Metabolite
            for key in ['met', 'substrate', 's', 'glucose']:
                if key in extracted:
                    arr = extracted[key]
                    if isinstance(arr, np.ndarray) and len(arr) > 0:
                        data_dict['substrate'] = arr.flatten()
                        break
            
            if not data_dict:
                print(f"   ⚠️  No time series data found in extracted structure")
                print(f"   Available keys: {list(extracted.keys())[:10]}")
                return None
            
            # Align arrays to same length
            lengths = [len(v) for v in data_dict.values() if isinstance(v, np.ndarray)]
            if not lengths:
                return None
            
            min_len = min(lengths)
            aligned_data = {}
            for key, value in data_dict.items():
                if isinstance(value, np.ndarray):
                    aligned_data[key] = value[:min_len]
            
            # Save to CSV
            output_file = output_dir / f"{Path(mat_file).stem}.csv"
            
            with open(output_file, 'w') as f:
                headers = list(aligned_data.keys())
                f.write(','.join(headers) + '\n')
                
                for i in range(min_len):
                    row = [str(float(aligned_data[h][i])) for h in headers]
                    f.write(','.join(row) + '\n')
            
            print(f"   ✅ Extracted {min_len} time points")
            print(f"   ✅ Saved to: {output_file}")
            print(f"   Columns: {headers}")
            
            return output_file
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function."""
    repo_dir = Path("temp_repos/Hybrid-modeling-of-bioreactor-with-LSTM/data")
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    if not repo_dir.exists():
        print("❌ Repository directory not found")
        return
    
    mat_files = list(repo_dir.glob("batch*.mat"))
    
    print("=" * 60)
    print("EXTRACTING TIME SERIES DATA FROM MATLAB FILES (v2)")
    print("=" * 60)
    
    extracted_files = []
    for mat_file in sorted(mat_files):
        result = extract_batch_data_v2(mat_file, output_dir)
        if result:
            extracted_files.append(result)
    
    print("\n" + "=" * 60)
    print(f"✅ Extraction complete! {len(extracted_files)} file(s) extracted")
    
    if extracted_files:
        print("\nExtracted files:")
        for f in extracted_files:
            size = f.stat().st_size / 1024
            print(f"  - {f.name} ({size:.1f} KB)")

if __name__ == "__main__":
    main()

