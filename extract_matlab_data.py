"""
Extract time series data from MATLAB .mat files

The bioreactor LSTM repository contains structured MATLAB data.
This script extracts the time series (age, vcd, product, met) into CSV format.
"""

import sys
import numpy as np
from pathlib import Path

try:
    import scipy.io
    SCIPY_AVAILABLE = True
except ImportError:
    print("❌ scipy not available - cannot read .mat files")
    sys.exit(1)

def extract_batch_data(mat_file, output_dir="data"):
    """Extract time series data from batch MATLAB files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n📁 Processing: {Path(mat_file).name}")
    
    try:
        mat_data = scipy.io.loadmat(mat_file, struct_as_record=False, squeeze_me=True)
        
        # Find the batch data structure
        batch_key = None
        for key in mat_data.keys():
            if not key.startswith('__') and 'batch' in key.lower():
                batch_key = key
                break
        
        if not batch_key:
            print(f"   ⚠️  No batch data found")
            return None
        
        batch_data = mat_data[batch_key]
        
        # Extract time series data
        # The structure typically has: age (time), vcd (biomass), product, met (substrate/metabolite)
        extracted_data = {}
        
        # Try to extract common fields
        if hasattr(batch_data, 'age') or 'age' in dir(batch_data):
            try:
                age = batch_data.age if hasattr(batch_data, 'age') else getattr(batch_data, 'age', None)
                if age is not None and hasattr(age, '__len__'):
                    extracted_data['time'] = np.array(age).flatten()
            except:
                pass
        
        if hasattr(batch_data, 'vcd') or 'vcd' in dir(batch_data):
            try:
                vcd = batch_data.vcd if hasattr(batch_data, 'vcd') else getattr(batch_data, 'vcd', None)
                if vcd is not None and hasattr(vcd, '__len__'):
                    extracted_data['biomass'] = np.array(vcd).flatten()
            except:
                pass
        
        if hasattr(batch_data, 'product') or 'product' in dir(batch_data):
            try:
                product = batch_data.product if hasattr(batch_data, 'product') else getattr(batch_data, 'product', None)
                if product is not None and hasattr(product, '__len__'):
                    extracted_data['product'] = np.array(product).flatten()
            except:
                pass
        
        if hasattr(batch_data, 'met') or 'met' in dir(batch_data):
            try:
                met = batch_data.met if hasattr(batch_data, 'met') else getattr(batch_data, 'met', None)
                if met is not None and hasattr(met, '__len__'):
                    extracted_data['substrate'] = np.array(met).flatten()
            except:
                pass
        
        # If we got structured array, try different approach
        if not extracted_data and isinstance(batch_data, np.ndarray):
            # Try to access as structured array
            if batch_data.dtype.names:
                print(f"   Found fields: {batch_data.dtype.names}")
                for field in batch_data.dtype.names:
                    try:
                        field_data = batch_data[field]
                        if hasattr(field_data, '__len__') and len(field_data) > 0:
                            # Try to get first element if it's nested
                            if isinstance(field_data[0], np.ndarray):
                                arr = field_data[0].flatten()
                            else:
                                arr = np.array(field_data).flatten()
                            
                            # Map field names
                            if 'age' in field.lower() or 'time' in field.lower():
                                extracted_data['time'] = arr
                            elif 'vcd' in field.lower() or 'biomass' in field.lower():
                                extracted_data['biomass'] = arr
                            elif 'product' in field.lower():
                                extracted_data['product'] = arr
                            elif 'met' in field.lower() or 'glucose' in field.lower():
                                extracted_data['substrate'] = arr
                    except Exception as e:
                        continue
        
        if not extracted_data:
            print(f"   ⚠️  Could not extract time series data")
            print(f"   Data type: {type(batch_data)}")
            if hasattr(batch_data, 'dtype'):
                print(f"   Dtype: {batch_data.dtype}")
            return None
        
        # Create DataFrame-like structure
        # Find the minimum length to align all arrays
        lengths = [len(v) for v in extracted_data.values()]
        if not lengths:
            return None
        
        min_len = min(lengths)
        
        # Align all arrays to same length
        aligned_data = {}
        for key, value in extracted_data.items():
            aligned_data[key] = value[:min_len]
        
        # Save as CSV
        output_file = output_dir / f"{Path(mat_file).stem}.csv"
        
        # Create CSV content
        with open(output_file, 'w') as f:
            # Write header
            headers = list(aligned_data.keys())
            f.write(','.join(headers) + '\n')
            
            # Write data
            for i in range(min_len):
                row = [str(aligned_data[h][i]) for h in headers]
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
    """Main function to extract data from all batch files."""
    repo_dir = Path("temp_repos/Hybrid-modeling-of-bioreactor-with-LSTM/data")
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    if not repo_dir.exists():
        print("❌ Repository directory not found. Run download_example_data.sh first.")
        return
    
    mat_files = list(repo_dir.glob("batch*.mat"))
    
    if not mat_files:
        print("❌ No batch MATLAB files found")
        return
    
    print("=" * 60)
    print("EXTRACTING TIME SERIES DATA FROM MATLAB FILES")
    print("=" * 60)
    
    extracted_files = []
    for mat_file in sorted(mat_files):
        result = extract_batch_data(mat_file, output_dir)
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

