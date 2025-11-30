# GitHub Data Sources for Bioprocess Data

This document lists GitHub repositories and resources where you can find real bioprocess data for hybrid modeling.

## 🔍 Recommended Repositories

### 1. REINFORCE-PSE (Batch Bioprocess Optimization)
**Repository:** https://github.com/OptiMaL-PSE-Lab/REINFORCE-PSE

**Description:**
- Reinforcement learning for batch bioprocess optimization
- Includes code and data for chemical systems modeled via ODEs
- Focuses on batch process optimization
- May contain example datasets

**How to Access:**
```bash
git clone https://github.com/OptiMaL-PSE-Lab/REINFORCE-PSE.git
# Check for data files in the repository
```

### 2. Awesome Bio Datasets
**Repository:** https://github.com/OpenGene/awesome-bio-datasets

**Description:**
- Curated list of biological datasets
- May include bioprocess-related data
- Good starting point for finding datasets

**How to Access:**
```bash
git clone https://github.com/OpenGene/awesome-bio-datasets.git
# Browse the curated list for bioprocess datasets
```

### 3. Hybrid Modeling of Bioreactor with LSTM
**Repository:** https://github.com/jrcramos/Hybrid-modeling-of-bioreactor-with-LSTM

**Description:**
- MATLAB implementation of hybrid LSTM-bioreactor model
- Specifically for HEK293 cell culture processes
- May include synthetic DoE datasets
- **Most relevant to your pipeline!**

**How to Access:**
```bash
git clone https://github.com/jrcramos/Hybrid-modeling-of-bioreactor-with-LSTM.git
# Check for data files or generate synthetic data using their scripts
```

## 📊 Alternative Data Sources

### Academic Databases

1. **Zenodo** (https://zenodo.org/)
   - Search for "bioprocess data" or "fermentation data"
   - Many researchers publish datasets here
   - Often includes CSV/Excel files

2. **Figshare** (https://figshare.com/)
   - Academic data repository
   - Search for bioprocess, fermentation, cell culture
   - Many datasets available for download

3. **Kaggle** (https://www.kaggle.com/)
   - Search for "bioprocess", "fermentation", "cell culture"
   - Some datasets available
   - May require account registration

### Research Papers with Supplementary Data

Many research papers include supplementary data files. Search for:
- "hybrid modeling bioprocess"
- "digital twin cell culture"
- "bioprocess optimization data"
- "fermentation process data"

## 🔧 How to Use These Data Sources

### Option 1: Download from GitHub Repository

```bash
cd "/scratch/project_2010726/solution_data scientist/real_data_hybrid_modeling/data"

# Clone repository (if it contains data)
git clone https://github.com/REPO_URL.git temp_repo

# Find and copy data files
find temp_repo -name "*.csv" -o -name "*.xlsx" -o -name "*.xls" | head -5

# Copy relevant files to data/ directory
cp temp_repo/path/to/data.csv .

# Clean up
rm -rf temp_repo
```

### Option 2: Manual Download

1. Visit the repository on GitHub
2. Navigate to data files
3. Download CSV/Excel files
4. Place in `data/` directory

### Option 3: Use Data Generation Scripts

Some repositories include scripts to generate synthetic data based on real process parameters. You can:
1. Clone the repository
2. Run their data generation scripts
3. Use the generated data (which is based on real process parameters)

## 📝 Data Format Conversion

If you find data in different formats, you may need to convert it. Common conversions:

### From MATLAB .mat files:
```python
import scipy.io
mat = scipy.io.loadmat('data.mat')
# Extract and convert to DataFrame
```

### From JSON:
```python
import json
import pandas as pd
with open('data.json') as f:
    data = json.load(f)
df = pd.DataFrame(data)
```

### From HDF5:
```python
import h5py
import pandas as pd
with h5py.File('data.h5', 'r') as f:
    # Extract data and convert
```

## 🎯 Recommended Search Strategy

1. **Start with the LSTM-bioreactor repository** (most relevant)
2. **Check REINFORCE-PSE** for batch process data
3. **Browse awesome-bio-datasets** for curated list
4. **Search Zenodo/Figshare** for published datasets
5. **Check research paper supplementary materials**

## ⚠️ Important Notes

- **Licensing:** Always check the license of any dataset you use
- **Attribution:** Cite the source if required
- **Data Quality:** Review data for completeness and quality
- **Format:** May need to adjust column names in `load_real_data.py`

## 🔗 Quick Links

- GitHub Search: https://github.com/search?q=bioprocess+data
- Zenodo: https://zenodo.org/search?q=bioprocess
- Figshare: https://figshare.com/search?q=bioprocess
- Kaggle: https://www.kaggle.com/datasets?search=bioprocess

## 📧 Alternative: Contact Researchers

If you can't find suitable data:
1. Contact authors of relevant papers
2. Reach out to bioprocess engineering groups
3. Check if your institution has data sharing agreements
4. Consider using synthetic data based on real process parameters (like the pipeline does)

---

**Last Updated:** November 30, 2025

