#!/bin/bash
# Script to download example bioprocess data from GitHub repositories

# Set working directory
DATA_DIR="/scratch/project_2010726/solution_data scientist/real_data_hybrid_modeling/data"
cd "$DATA_DIR"

echo "=========================================="
echo "DOWNLOADING BIOPROCESS DATA FROM GITHUB"
echo "=========================================="
echo ""

# Create temporary directory for cloning
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Repository 1: Hybrid Modeling of Bioreactor with LSTM
echo "1. Checking: Hybrid-modeling-of-bioreactor-with-LSTM"
REPO1="https://github.com/jrcramos/Hybrid-modeling-of-bioreactor-with-LSTM.git"
if git clone --depth 1 "$REPO1" bioreactor_lstm 2>/dev/null; then
    echo "   ✅ Repository cloned"
    
    # Look for data files
    DATA_FILES=$(find bioreactor_lstm -type f \( -name "*.csv" -o -name "*.mat" -o -name "*data*" -o -name "*DoE*" \) 2>/dev/null)
    if [ -n "$DATA_FILES" ]; then
        echo "   📁 Found data files:"
        echo "$DATA_FILES" | head -5
        # Copy CSV files if found
        find bioreactor_lstm -name "*.csv" -exec cp {} "$DATA_DIR/" \; 2>/dev/null
        echo "   ✅ CSV files copied to data/ directory"
    else
        echo "   ⚠️  No data files found (may need to generate using their scripts)"
    fi
else
    echo "   ❌ Could not clone repository"
fi
echo ""

# Repository 2: REINFORCE-PSE
echo "2. Checking: REINFORCE-PSE"
REPO2="https://github.com/OptiMaL-PSE-Lab/REINFORCE-PSE.git"
if git clone --depth 1 "$REPO2" reinforce_pse 2>/dev/null; then
    echo "   ✅ Repository cloned"
    
    # Look for data files
    DATA_FILES=$(find reinforce_pse -type f \( -name "*.csv" -o -name "*.pkl" -o -name "*data*" \) 2>/dev/null)
    if [ -n "$DATA_FILES" ]; then
        echo "   📁 Found data files:"
        echo "$DATA_FILES" | head -5
        # Copy CSV files if found
        find reinforce_pse -name "*.csv" -exec cp {} "$DATA_DIR/" \; 2>/dev/null
        echo "   ✅ CSV files copied to data/ directory"
    else
        echo "   ⚠️  No CSV data files found"
    fi
else
    echo "   ❌ Could not clone repository"
fi
echo ""

# Repository 3: Awesome Bio Datasets (for links)
echo "3. Checking: awesome-bio-datasets"
REPO3="https://github.com/OpenGene/awesome-bio-datasets.git"
if git clone --depth 1 "$REPO3" awesome_bio 2>/dev/null; then
    echo "   ✅ Repository cloned"
    echo "   📋 This is a curated list - check README.md for dataset links"
    if [ -f awesome_bio/README.md ]; then
        echo "   📄 README.md available - review for bioprocess dataset links"
    fi
else
    echo "   ❌ Could not clone repository"
fi
echo ""

# Cleanup
cd "$DATA_DIR"
rm -rf "$TEMP_DIR"

echo "=========================================="
echo "DOWNLOAD SUMMARY"
echo "=========================================="
echo ""
echo "Files in data/ directory:"
ls -lh "$DATA_DIR"/*.csv 2>/dev/null || echo "  No CSV files found"
echo ""

if [ -z "$(ls -A $DATA_DIR/*.csv 2>/dev/null)" ]; then
    echo "⚠️  No data files were downloaded automatically."
    echo ""
    echo "Next steps:"
    echo "1. Manually download data from the repositories above"
    echo "2. Check the repositories for data generation scripts"
    echo "3. Review GITHUB_DATA_SOURCES.md for more options"
    echo "4. Search Zenodo/Figshare for published datasets"
else
    echo "✅ Data files downloaded successfully!"
    echo "   Review the files and adjust column names in load_real_data.py if needed"
fi
echo ""

