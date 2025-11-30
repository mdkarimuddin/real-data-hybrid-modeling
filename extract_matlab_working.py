"""
Working version: Extract time series data from MATLAB batch files

Handles the nested structure: vcd[0,0]['val'] contains the actual data
"""

import sys
import numpy as np
from pathlib import Path

try:
    import scipy.io
except ImportError:
    print("❌ scipy not available")
    sys.exit(1)

def extract_batch_working(mat_file, output_dir="data", batch_column=0):
    """
    Extract time series data from batch MATLAB files.
    
    Parameters:
    -----------
    batch_column : int
        Which column to extract from multi-batch data (0 = first batch)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n📁 Processing: {Path(mat_file).name}")
    
    try:
        mat_data = scipy.io.loadmat(str(mat_file), struct_as_record=True, squeeze_me=False)
        
        batch_key = [k for k in mat_data.keys() if not k.startswith('__') and 'batch' in k.lower()]
        if not batch_key:
            return None
        
        batch = mat_data[batch_key[0]][0, 0]
        
        # Extract time (age) - this is straightforward
        time = batch['age'].flatten()
        
        # Extract VCD (biomass) - nested structure
        biomass = None
        if 'vcd' in batch.dtype.names:
            vcd_struct = batch['vcd'][0, 0]
            if 'val' in vcd_struct.dtype.names:
                vcd_data = vcd_struct['val']
                # vcd_data is (time_points, batches) - extract one batch
                if len(vcd_data.shape) == 2:
                    biomass = vcd_data[:, batch_column].flatten()
                else:
                    biomass = vcd_data.flatten()
        
        # Extract product - similar structure
        product = None
        if 'product' in batch.dtype.names:
            prod_struct = batch['product'][0, 0]
            if 'val' in prod_struct.dtype.names:
                prod_data = prod_struct['val']
                if len(prod_data.shape) == 2:
                    product = prod_data[:, batch_column].flatten()
                else:
                    product = prod_data.flatten()
        
        # Extract metabolite/substrate (met) - similar structure
        substrate = None
        if 'met' in batch.dtype.names:
            met_struct = batch['met'][0, 0]
            if 'val' in met_struct.dtype.names:
                met_data = met_struct['val']
                # met_data might be (time_points, metabolites) - take first metabolite (glucose)
                if len(met_data.shape) == 2:
                    substrate = met_data[:, 0].flatten()  # First metabolite column
                else:
                    substrate = met_data.flatten()
        
        # Build data dictionary
        data_dict = {'time': time}
        
        if biomass is not None and len(biomass) == len(time):
            data_dict['biomass'] = biomass
        if substrate is not None and len(substrate) == len(time):
            data_dict['substrate'] = substrate
        if product is not None and len(product) == len(time):
            data_dict['product'] = product
        
        if len(data_dict) < 2:
            print(f"   ⚠️  Insufficient data extracted (only time)")
            return None
        
        # Save to CSV
        output_file = output_dir / f"{Path(mat_file).stem}.csv"
        
        with open(output_file, 'w') as f:
            headers = list(data_dict.keys())
            f.write(','.join(headers) + '\n')
            
            for i in range(len(time)):
                row = [str(float(data_dict[h][i])) for h in headers]
                f.write(','.join(row) + '\n')
        
        print(f"   ✅ Extracted {len(time)} time points")
        print(f"   ✅ Saved to: {output_file}")
        print(f"   Columns: {headers}")
        print(f"   Time range: {time[0]:.1f} - {time[-1]:.1f} hours")
        if 'biomass' in headers:
            print(f"   Biomass range: {biomass.min():.2f} - {biomass.max():.2f} (Mcell/mL)")
        if 'substrate' in headers:
            print(f"   Substrate range: {substrate.min():.2f} - {substrate.max():.2f}")
        
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
        result = extract_batch_working(mat_file, output_dir, batch_column=0)
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
        
        print("\n📋 Sample of first file:")
        with open(extracted_files[0], 'r') as f:
            for i, line in enumerate(f):
                if i < 6:
                    print(f"  {line.strip()}")
                else:
                    break
        
        print("\n✅ Data ready for hybrid modeling!")
        print("\nNext steps:")
        print("  1. Review the CSV files in data/ directory")
        print("  2. Run: python load_real_data.py to test loading")
        print("  3. Adjust column mapping if needed")
        print("  4. Run: sbatch run_real_data_puhti.sh to train model")
    else:
        print("❌ No files were extracted")

if __name__ == "__main__":
    main()

