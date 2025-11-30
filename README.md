# Real Data Hybrid Modeling Analysis

This directory contains scripts and workflows for applying the hybrid modeling pipeline to **real bioprocess data**.

## Directory Structure

```
real_data_hybrid_modeling/
├── data/              # Place your real bioprocess data files here
├── inputs/            # Preprocessed data files
├── outputs/           # Results, models, and visualizations
├── logs/              # Job logs
├── load_real_data.py  # Script to load and preprocess real data
├── run_real_data.py   # Main script for real data analysis
├── run_real_data_puhti.sh  # Batch script for Puhti
└── README.md          # This file
```

## Data Format Requirements

### Expected Data Format

Your real bioprocess data should be in one of these formats:

1. **CSV File** (Recommended)
   - Columns: `time`, `biomass` (or `X`), `substrate` (or `S`), `product` (or `P`)
   - Optional: `experiment_id`, `pH`, `temperature`, `DO` (dissolved oxygen)
   - Example:
     ```csv
     time,biomass,substrate,product,experiment_id
     0,0.2,10.0,0.0,exp1
     10,0.5,8.5,0.1,exp1
     20,1.2,6.0,0.3,exp1
     ...
     ```

2. **Excel File** (.xlsx, .xls)
   - Same column structure as CSV
   - Can have multiple sheets (one per experiment)

3. **Multiple Files**
   - One file per experiment
   - All files should have the same structure

### Data Requirements

- **Time Series Data:** Measurements over time for each experiment
- **Minimum Features:** 
  - Time (hours)
  - Biomass concentration (X, cells/mL or g/L)
  - Substrate concentration (S, g/L)
  - Product concentration (P, g/L) - optional but recommended
- **Multiple Experiments:** At least 3-5 experiments for meaningful training
- **Time Points:** At least 10-20 time points per experiment

## Quick Start

### 1. Prepare Your Data

Place your data file(s) in the `data/` directory:

```bash
cd "/scratch/project_2010726/solution_data scientist/real_data_hybrid_modeling"
# Copy your data file here
cp /path/to/your/data.csv data/
```

### 2. Configure Data Loading

Edit `load_real_data.py` to match your data format:

```python
# Update column names to match your data
COLUMN_MAPPING = {
    'time': 'time',           # or 'Time', 't', etc.
    'biomass': 'biomass',     # or 'X', 'cell_density', etc.
    'substrate': 'substrate', # or 'S', 'glucose', etc.
    'product': 'product'      # or 'P', 'protein', etc.
}
```

### 3. Run Analysis

**On Puhti (recommended):**
```bash
sbatch run_real_data_puhti.sh
```

**Locally:**
```bash
python run_real_data.py
```

## Data Preprocessing

The pipeline will automatically:

1. **Load Data:** Read from CSV/Excel files
2. **Clean Data:** 
   - Remove missing values
   - Handle outliers
   - Normalize units
3. **Prepare Sequences:** 
   - Create time series sequences for LSTM
   - Handle multiple experiments
4. **Split Data:** 
   - Train/validation/test sets
   - Maintain temporal structure

## Customization

### Adjust Model Parameters

Edit `run_real_data.py` to customize:

- **Mechanistic Parameters:** Based on your cell line/process
  ```python
  mechanistic_params = {
      'mu_max': 0.5,   # Adjust based on your process
      'Ks': 0.1,       # Substrate saturation constant
      'Yxs': 0.5,      # Biomass yield
      'Yps': 0.3,      # Product yield
      'qp_max': 0.1    # Product formation rate
  }
  ```

- **Model Architecture:**
  ```python
  model = HybridModel(
      mechanistic_params=mechanistic_params,
      ml_input_dim=3,      # Increase if adding pH, T, etc.
      ml_hidden_dim=64,    # Adjust based on data complexity
      ml_num_layers=2,     # Deeper for complex patterns
      use_residual_learning=True
  )
  ```

- **Training Parameters:**
  ```python
  trainer = Trainer(
      model=model,
      learning_rate=0.001,  # Adjust learning rate
      weight_decay=1e-5
  )
  ```

## Output Files

After running, you'll find in `outputs/`:

- `training_history.png` - Training curves
- `predictions.png` - Model predictions vs observations
- `prediction_scatter.png` - Prediction accuracy
- `metrics_comparison.png` - Hybrid vs mechanistic comparison
- `final_model.pt` - Trained model
- `real_data_analysis_report.md` - Detailed analysis report

## Troubleshooting

### Data Format Issues

If you get errors about missing columns:
1. Check your column names match the mapping in `load_real_data.py`
2. Ensure required columns (time, biomass, substrate) are present
3. Check for typos or extra spaces in column names

### Data Quality Issues

If model performance is poor:
1. Check for outliers or missing values
2. Ensure sufficient data (multiple experiments, enough time points)
3. Verify data units are consistent
4. Consider data normalization

### Memory Issues

If you run out of memory:
1. Reduce batch size in `run_real_data.py`
2. Use fewer experiments or time points
3. Request more memory in batch script

## Example Data Formats

### Format 1: Single CSV with Multiple Experiments

```csv
time,biomass,substrate,product,experiment_id
0,0.2,10.0,0.0,exp1
10,0.5,8.5,0.1,exp1
20,1.2,6.0,0.3,exp1
0,0.15,12.0,0.0,exp2
10,0.4,9.0,0.08,exp2
...
```

### Format 2: Separate Files per Experiment

```
data/
├── experiment1.csv
├── experiment2.csv
├── experiment3.csv
...
```

Each file:
```csv
time,biomass,substrate,product
0,0.2,10.0,0.0
10,0.5,8.5,0.1
...
```

## Next Steps

1. **Prepare Your Data:** Format according to requirements above
2. **Test Data Loading:** Run `load_real_data.py` to verify data loads correctly
3. **Run Analysis:** Submit batch job or run locally
4. **Review Results:** Check outputs and analysis report
5. **Iterate:** Adjust parameters and rerun as needed

## Support

For issues or questions:
- Check the main pipeline README: `../hybrid_modeling_pipeline/README.md`
- Review example usage: `../hybrid_modeling_pipeline/example_usage.py`
- Check logs in `logs/` directory

