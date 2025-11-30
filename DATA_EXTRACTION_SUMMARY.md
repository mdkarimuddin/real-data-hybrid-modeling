# Data Extraction Summary

## ✅ Successfully Extracted Data

### Source Repository
**Hybrid-modeling-of-bioreactor-with-LSTM**
- Repository: https://github.com/jrcramos/Hybrid-modeling-of-bioreactor-with-LSTM
- Description: HEK293 cell culture process data
- Data Type: Synthetic DoE (Design of Experiments) data based on real process parameters

### Extracted Files

Three batch files were successfully extracted:

1. **batch1.csv** (0.8 KB, 21 time points)
2. **batch2.csv** (0.8 KB, 21 time points)  
3. **batch3.csv** (0.8 KB, 21 time points)

### Data Structure

Each file contains:
- **time**: Time in hours (0-240 hours)
- **biomass**: Viable cell density (VCD) in Mcell/mL (4.00 - 19.92 range)
- **product**: Product concentration (very small values, near detection limit)

**Note:** Substrate (glucose/metabolite) data is available in the MATLAB files but requires additional extraction. The current files have time, biomass, and product.

### Data Characteristics

- **Time Points:** 21 measurements per batch
- **Time Range:** 0-240 hours (10-day process)
- **Biomass Range:** 4.00 - 19.92 Mcell/mL (typical for HEK293)
- **Experiments:** 3 batches (can be combined for training)

### Data Quality

✅ **Strengths:**
- Real process-based synthetic data
- Consistent time points across batches
- Realistic biomass growth curves
- Suitable for hybrid modeling

⚠️ **Limitations:**
- Missing substrate data in current extraction
- Product values are very small (may need scaling)
- Only 3 batches (limited for deep learning)

## Next Steps

### 1. Test Data Loading

```bash
cd "/scratch/project_2010726/solution_data scientist/real_data_hybrid_modeling"
python load_real_data.py
```

### 2. Adjust Column Mapping

If needed, update `load_real_data.py`:
```python
COLUMN_MAPPING = {
    'time': 'time',
    'biomass': 'biomass',  # Already correct
    'substrate': 'substrate',  # May need to extract from MATLAB
    'product': 'product'  # Already correct
}
```

### 3. Combine Batches

The pipeline can combine all 3 batches into one dataset for training.

### 4. Run Analysis

```bash
sbatch run_real_data_puhti.sh
```

## Alternative: Extract Substrate Data

If you need substrate (glucose) data, you can:

1. **Re-run extraction with substrate:**
   - Modify `extract_matlab_working.py` to better handle metabolite extraction
   - The 'met' field contains metabolite data but needs proper extraction

2. **Use existing data:**
   - The current data (time, biomass, product) is sufficient for hybrid modeling
   - Substrate can be inferred or estimated from biomass growth

## Data Files Location

```
real_data_hybrid_modeling/
└── data/
    ├── batch1.csv  ✅ Ready to use
    ├── batch2.csv  ✅ Ready to use
    └── batch3.csv  ✅ Ready to use
```

## Usage Example

```python
from load_real_data import load_real_data

# Load all batches
data, time, metadata = load_real_data(
    data_dir="data",
    file_pattern="batch*.csv",
    combine_experiments=True
)

# data shape: (63, 3) - 3 batches × 21 time points, 3 features
# Features: [biomass, substrate (if available), product]
```

---

**Extraction Date:** November 30, 2025  
**Source:** GitHub - Hybrid-modeling-of-bioreactor-with-LSTM  
**Status:** ✅ Ready for hybrid modeling analysis

