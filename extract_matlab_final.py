"""
Final version: Extract time series data from MATLAB batch files

Based on understanding the structure from ReadBatchData.m
"""

import sys
import numpy as np
from pathlib import Path

try:
    import scipy.io
except ImportError:
    print("❌ scipy not available")
    sys.exit(1)

def extract_batch_final(mat_file, output_dir="data"):
    """Extract time series data from batch MATLAB files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n📁 Processing: {Path(mat_file).name}")
    
    try:
        # Load with struct_as_record=True to preserve structure
        mat_data = scipy.io.loadmat(str(mat_file), struct_as_record=True, squeeze_me=False)
        
        # Get batch data
        batch_key = [k for k in mat_data.keys() if not k.startswith('__') and 'batch' in k.lower()]
        if not batch_key:
            print(f"   ⚠️  No batch data found")
            return None
        
        batch = mat_data[batch_key[0]][0, 0]
        
        # Extract time (age)
        if 'age' in batch.dtype.names:
            time_data = batch['age']
            if time_data.shape[0] > 0:
                time = time_data.flatten()
            else:
                print(f"   ⚠️  Empty time data")
                return None
        else:
            print(f"   ⚠️  No 'age' field found")
            return None
        
        # Extract VCD (biomass)
        biomass = None
        if 'vcd' in batch.dtype.names:
            vcd_data = batch['vcd']
            # vcd might be nested - try to extract
            if vcd_data.shape == (1, 1) and vcd_data.dtype == object:
                # Nested structure
                try:
                    vcd_inner = vcd_data[0, 0]
                    if isinstance(vcd_inner, np.ndarray):
                        biomass = vcd_inner.flatten()
                except:
                    pass
            elif len(vcd_data.shape) == 2:
                biomass = vcd_data.flatten()
        
        # Extract product
        product = None
        if 'product' in batch.dtype.names:
            prod_data = batch['product']
            if prod_data.shape == (1, 1) and prod_data.dtype == object:
                try:
                    prod_inner = prod_data[0, 0]
                    if isinstance(prod_inner, np.ndarray):
                        product = prod_inner.flatten()
                except:
                    pass
            elif len(prod_data.shape) == 2:
                product = prod_data.flatten()
        
        # Extract metabolite/substrate (met)
        substrate = None
        if 'met' in batch.dtype.names:
            met_data = batch['met']
            # met might be a matrix (multiple metabolites) or nested
            if met_data.shape == (1, 1) and met_data.dtype == object:
                try:
                    met_inner = met_data[0, 0]
                    if isinstance(met_inner, np.ndarray):
                        # If it's 2D, take first column (glucose typically)
                        if len(met_inner.shape) == 2:
                            substrate = met_inner[:, 0].flatten()
                        else:
                            substrate = met_inner.flatten()
                except:
                    pass
            elif len(met_data.shape) == 2:
                # If 2D, take first column
                if met_data.shape[1] > 0:
                    substrate = met_data[:, 0].flatten()
                else:
                    substrate = met_data.flatten()
        
        # Build data dictionary
        data_dict = {'time': time}
        
        if biomass is not None and len(biomass) > 0:
            data_dict['biomass'] = biomass
        if substrate is not None and len(substrate) > 0:
            data_dict['substrate'] = substrate
        if product is not None and len(product) > 0:
            data_dict['product'] = product
        
        # Align to same length
        lengths = [len(v) for v in data_dict.values()]
        min_len = min(lengths)
        
        aligned_data = {}
        for key, value in data_dict.items():
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
        print(f"   Time range: {time[0]:.1f} - {time[-1]:.1f} hours")
        
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
        print("Run: bash download_example_data.sh")
        return
    
    mat_files = sorted(repo_dir.glob("batch*.mat"))
    
    if not mat_files:
        print("❌ No batch MATLAB files found")
        return
    
    print("=" * 60)
    print("EXTRACTING BIOPROCESS DATA FROM MATLAB FILES")
    print("=" * 60)
    
    extracted_files = []
    for mat_file in mat_files:
        result = extract_batch_final(mat_file, output_dir)
        if result:
            extracted_files.append(result)
    
    print("\n" + "=" * 60)
    if extracted_files:
        print(f"✅ Successfully extracted {len(extracted_files)} batch file(s)")
        print("\nExtracted files:")
        for f in extracted_files:
            size = f.stat().st_size / 1024
            lines = sum(1 for _ in open(f))
            print(f"  - {f.name} ({size:.1f} KB, {lines-1} time points)")
        
        print("\n📋 Next steps:")
        print("  1. Review the CSV files in data/ directory")
        print("  2. Check column names match your expectations")
        print("  3. Run: python load_real_data.py to test loading")
        print("  4. Adjust column mapping in load_real_data.py if needed")
    else:
        print("❌ No files were extracted")
        print("   The MATLAB files may have a different structure")

if __name__ == "__main__":
    main()

