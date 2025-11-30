"""
Real Data Hybrid Modeling Pipeline

This script runs the hybrid modeling pipeline on real bioprocess data.
It loads real data, trains the hybrid model, and generates results.
"""

import sys
import os
from pathlib import Path
import numpy as np
import torch
import matplotlib
matplotlib.use('Agg')  # For batch jobs
import matplotlib.pyplot as plt

# Add parent directory to path to import pipeline modules
sys.path.insert(0, str(Path(__file__).parent.parent / "hybrid_modeling_pipeline"))

from hybrid_model import HybridModel
from data_processing import (
    create_dataloaders,
    split_data
)
from training import Trainer
from evaluation import (
    evaluate_model,
    plot_training_history,
    plot_predictions,
    plot_prediction_scatter,
    plot_metrics_comparison,
    print_evaluation_report
)
from load_real_data import load_real_data


def main():
    """
    Main workflow for real data analysis.
    """
    print("=" * 60)
    print("REAL DATA HYBRID MODELING PIPELINE")
    print("=" * 60)
    print()
    
    # Set random seeds for reproducibility
    np.random.seed(42)
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(42)
    
    # Device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    print()
    
    # ===================================================================
    # STEP 1: Load Real Bioprocess Data
    # ===================================================================
    print("STEP 1: Loading real bioprocess data...")
    
    data_dir = Path("data")
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        print("Please place your data files in the 'data/' directory")
        print("See README.md for data format requirements")
        return
    
    try:
        data, time, metadata = load_real_data(
            data_dir=str(data_dir),
            file_pattern="batch*.csv",  # Only load batch files
            combine_experiments=True
        )
        
        print(f"  Loaded {len(data)} data points")
        print(f"  Data shape: {data.shape}")
        print(f"  Features: [Biomass (X), Substrate (S), Product (P)]")
        print()
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ===================================================================
    # STEP 2: Prepare Data
    # ===================================================================
    print("STEP 2: Preparing data for training...")
    
    # Determine sequence length and batch size first
    n_samples = len(data)
    sequence_length = min(10, max(3, n_samples // 10))  # Adaptive: 3-10, based on data size
    batch_size = min(32, max(4, n_samples // 10))  # Adaptive batch size
    
    # Split data - ensure validation and test sets are large enough
    min_val_size = sequence_length + 2  # Need at least sequence_length + some samples
    min_test_size = sequence_length + 2
    
    # Adjust ratios if dataset is small
    if n_samples < 50:
        train_ratio = 0.6
        val_ratio = 0.2
    else:
        train_ratio = 0.7
        val_ratio = 0.15
    
    train_data, val_data, test_data = split_data(
        data, train_ratio=train_ratio, val_ratio=val_ratio
    )
    
    # Ensure minimum sizes
    if len(val_data) < min_val_size:
        # Reduce train size to increase val
        n_train = n_samples - min_val_size - min_test_size
        train_data = data[:n_train]
        val_data = data[n_train:n_train + min_val_size]
        test_data = data[n_train + min_val_size:]
    
    if len(test_data) < min_test_size:
        # Adjust to ensure test has minimum size
        n_train = len(train_data)
        n_val = len(val_data)
        n_test = max(min_test_size, n_samples - n_train - n_val)
        test_data = data[n_train + n_val:n_train + n_val + n_test]
    
    print(f"  Train samples: {len(train_data)}")
    print(f"  Validation samples: {len(val_data)}")
    print(f"  Test samples: {len(test_data)}")
    
    # Create dataloaders (sequence_length and batch_size already set above)
    
    train_loader, val_loader, test_loader, scaler = create_dataloaders(
        train_data, val_data, test_data,
        sequence_length=sequence_length,
        batch_size=batch_size,
        normalize=True
    )
    
    print(f"  Sequence length: {sequence_length}")
    print(f"  Batch size: {batch_size}")
    print()
    
    # ===================================================================
    # STEP 3: Initialize Hybrid Model
    # ===================================================================
    print("STEP 3: Initializing hybrid model...")
    
    # TODO: Adjust these parameters based on your specific process
    # Typical values for mammalian cell culture:
    mechanistic_params = {
        'mu_max': 0.5,   # Maximum growth rate (1/h) - ADJUST based on your cell line
        'Ks': 0.1,       # Substrate saturation constant (g/L) - ADJUST
        'Yxs': 0.5,      # Biomass yield on substrate (g/g) - ADJUST
        'Yps': 0.3,      # Product yield on substrate (g/g) - ADJUST
        'qp_max': 0.1    # Maximum product formation rate (g/g/h) - ADJUST
    }
    
    # Initialize model
    model = HybridModel(
        mechanistic_params=mechanistic_params,
        ml_input_dim=3,      # X, S, P (increase if adding pH, T, etc.)
        ml_hidden_dim=64,    # Adjust based on data complexity
        ml_num_layers=2,
        use_residual_learning=True
    )
    
    print(f"  Model architecture:")
    print(f"    - Mechanistic component: ODE-based bioprocess model")
    print(f"    - ML component: LSTM with {64} hidden units, {2} layers")
    print(f"    - Residual learning: {True}")
    print()
    
    # ===================================================================
    # STEP 4: Train Model
    # ===================================================================
    print("STEP 4: Training hybrid model...")
    print()
    
    # Create trainer
    trainer = Trainer(
        model=model,
        device=device,
        learning_rate=0.001,  # Adjust if needed
        weight_decay=1e-5
    )
    
    # Create output directory
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    checkpoint_dir = output_dir / "checkpoints"
    checkpoint_dir.mkdir(exist_ok=True)
    
    # Train
    history = trainer.train(
        train_loader=train_loader,
        val_loader=val_loader,
        n_epochs=100,  # Adjust based on convergence
        early_stopping_patience=20,
        checkpoint_dir=str(checkpoint_dir),
        verbose=True
    )
    
    print()
    
    # ===================================================================
    # STEP 5: Visualize Training History
    # ===================================================================
    print("STEP 5: Visualizing training history...")
    plot_training_history(
        history,
        save_path=str(output_dir / "training_history.png")
    )
    print()
    
    # ===================================================================
    # STEP 6: Evaluate Model
    # ===================================================================
    print("STEP 6: Evaluating model on test set...")
    
    # Prepare test data for evaluation
    test_eval_data = test_data
    t_span_eval = np.linspace(0, len(test_eval_data), len(test_eval_data))
    
    results = evaluate_model(
        model=model,
        test_data=test_eval_data,
        t_span=t_span_eval,
        device=device
    )
    
    # Print evaluation report
    print_evaluation_report(results)
    print()
    
    # ===================================================================
    # STEP 7: Visualize Results
    # ===================================================================
    print("STEP 7: Creating visualization plots...")
    
    # Plot predictions
    plot_predictions(
        results,
        save_path=str(output_dir / "predictions.png"),
        n_samples=5
    )
    
    # Plot scatter plots
    plot_prediction_scatter(
        results,
        save_path=str(output_dir / "prediction_scatter.png")
    )
    
    # Plot metrics comparison
    plot_metrics_comparison(
        results,
        save_path=str(output_dir / "metrics_comparison.png")
    )
    
    print()
    
    # ===================================================================
    # STEP 8: Save Model and Results
    # ===================================================================
    print("STEP 8: Saving model and results...")
    
    # Save final model
    model_path = output_dir / "final_model.pt"
    torch.save({
        'model_state_dict': model.state_dict(),
        'mechanistic_params': mechanistic_params,
        'scaler': scaler,
        'history': history,
        'metadata': metadata
    }, model_path)
    
    print(f"  Model saved to: {model_path}")
    print(f"  All outputs saved to: {output_dir}")
    print()
    
    print("=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Review the generated plots in the 'outputs' directory")
    print("  2. Adjust mechanistic parameters based on your process")
    print("  3. Experiment with different hyperparameters")
    print("  4. Compare results with domain knowledge")


if __name__ == "__main__":
    main()

