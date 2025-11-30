#!/bin/bash
#SBATCH --job-name=real_data_hybrid
#SBATCH --account=project_2010726
#SBATCH --partition=small
#SBATCH --time=02:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --output=logs/real_data_hybrid_%j.out
#SBATCH --error=logs/real_data_hybrid_%j.err

# Print job info
echo "=========================================="
echo "REAL DATA HYBRID MODELING - PUHTI BATCH JOB"
echo "=========================================="
echo "Job ID: $SLURM_JOB_ID"
echo "Job Name: $SLURM_JOB_NAME"
echo "Start Time: $(date)"
echo "Node: $SLURMD_NODENAME"
echo "CPUs: $SLURM_CPUS_PER_TASK"
echo "Memory: $SLURM_MEM_PER_NODE MB"
echo "=========================================="
echo ""

# On Puhti, initialize Lmod (module system)
if [ -f /usr/share/lmod/lmod/init/bash ]; then
    source /usr/share/lmod/lmod/init/bash
elif [ -f /appl/lmod/lmod/init/bash ]; then
    source /appl/lmod/lmod/init/bash
fi

# Set MODULEPATH if not set
if [ -z "$MODULEPATH" ]; then
    if [ -d /appl/modulefiles ]; then
        export MODULEPATH=/appl/modulefiles
    fi
fi

# Load required modules
echo "Loading modules..."
if command -v module &> /dev/null; then
    module load python-data/3.10-22.09 2>&1 || module load python-data 2>&1
    module load pytorch/2.4 2>&1 || module load pytorch 2>&1
    echo "✅ python-data module loaded"
    echo "✅ pytorch module loaded"
else
    echo "❌ Module command not available"
    exit 1
fi
echo ""

# Set working directory
PIPELINE_DIR="/scratch/project_2010726/solution_data scientist/real_data_hybrid_modeling"
cd "$PIPELINE_DIR"
echo "Working directory: $(pwd)"
echo ""

# Create logs directory
mkdir -p logs

# Check Python version and available packages
echo "=== Environment Check ==="
if [ -f /appl/soft/ai/wrap/pytorch-2.4/bin/python3 ]; then
    PYTHON_CMD=/appl/soft/ai/wrap/pytorch-2.4/bin/python3
elif [ -f /appl/soft/ai/python-data/3.10-22.09/bin/python3 ]; then
    PYTHON_CMD=/appl/soft/ai/python-data/3.10-22.09/bin/python3
else
    PYTHON_CMD=$(which python3)
fi

echo "Using Python: $PYTHON_CMD"
$PYTHON_CMD --version
echo ""

# Check if data directory exists and has files
echo "=== Data Check ==="
if [ ! -d "data" ]; then
    echo "❌ Data directory not found!"
    echo "Please create 'data/' directory and place your data files there"
    exit 1
fi

DATA_FILES=$(find data -type f \( -name "*.csv" -o -name "*.xlsx" -o -name "*.xls" \) 2>/dev/null | wc -l)
if [ "$DATA_FILES" -eq 0 ]; then
    echo "⚠️  No data files found in data/ directory"
    echo "Please place your CSV or Excel files in data/"
    exit 1
fi

echo "✅ Found $DATA_FILES data file(s) in data/ directory"
echo ""

# Check if required Python packages are available
echo "Checking Python packages..."
$PYTHON_CMD << EOF
import sys
required_packages = ['numpy', 'scipy', 'pandas', 'torch', 'matplotlib', 'seaborn']
missing_required = []
for pkg in required_packages:
    try:
        __import__(pkg)
        print(f"✅ {pkg} available")
    except ImportError:
        print(f"❌ {pkg} NOT available")
        missing_required.append(pkg)

if missing_required:
    print(f"\n❌ Missing required packages: {', '.join(missing_required)}")
    sys.exit(1)
else:
    print("\n✅ All required packages are available")
EOF

if [ $? -ne 0 ]; then
    echo "❌ Environment check failed"
    exit 1
fi

echo ""
echo "=== Starting Real Data Hybrid Modeling Pipeline ==="
echo ""

# Configure matplotlib for non-interactive backend
export MPLBACKEND=Agg

# Ensure we use the module Python
if [ ! -f "$PYTHON_CMD" ] || [ "$PYTHON_CMD" = "/usr/bin/python3" ]; then
    if [ -f /appl/soft/ai/wrap/pytorch-2.4/bin/python3 ]; then
        PYTHON_CMD=/appl/soft/ai/wrap/pytorch-2.4/bin/python3
    fi
fi

echo "Running pipeline with: $PYTHON_CMD"
echo ""

# Run the real data analysis script
$PYTHON_CMD -u run_real_data.py

EXIT_CODE=$?

echo ""
echo "=========================================="
echo "JOB SUMMARY"
echo "=========================================="
echo "Exit code: $EXIT_CODE"
echo "End time: $(date)"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Job completed successfully"
    echo ""
    echo "📁 OUTPUT FILES:"
    if [ -d "outputs" ]; then
        ls -lh outputs/ 2>/dev/null | while read line; do 
            echo "  $line"
        done
    else
        echo "  No outputs directory found"
    fi
    
    echo ""
    echo "📊 Check the following for results:"
    echo "  - outputs/training_history.png: Training curves"
    echo "  - outputs/predictions.png: Model predictions"
    echo "  - outputs/prediction_scatter.png: Prediction accuracy"
    echo "  - outputs/metrics_comparison.png: Model comparison"
    echo "  - outputs/final_model.pt: Trained model checkpoint"
else
    echo "❌ Job failed with exit code $EXIT_CODE"
    echo ""
    echo "📋 Check error log for details:"
    echo "  logs/real_data_hybrid_${SLURM_JOB_ID}.err"
fi

echo ""
echo "📁 Full logs available at:"
echo "  stdout: logs/real_data_hybrid_${SLURM_JOB_ID}.out"
echo "  stderr: logs/real_data_hybrid_${SLURM_JOB_ID}.err"
echo "=========================================="

