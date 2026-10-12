"""
Master ML & Results Execution Pipeline
Role: Member 4 - ML & Results (Akilan Pon Ilango)
Institution: SRM Institute of Science and Technology
Project: Spatio-Temporal Impact of Micro-Weather and Pitch Degradation on IPL Bowler Performance
"""

import os
import sys
import time
import pandas as pd

from src.feature_engineering import build_bowler_spells_dataset
from src.model_training import train_and_evaluate
from src.domain_analysis import run_domain_analysis
from src.visualizations import generate_visualizations

def run_full_pipeline():
    start_time = time.time()
    print("=" * 80)
    print("SPATIO-TEMPORAL IPL BOWLER PERFORMANCE ANALYSIS PIPELINE")
    print("Role: Member 4 - ML & Results (Akilan Pon Ilango)")
    print("=" * 80)
    
    # Step 1: Feature Engineering & Ingestion
    print("\n[STEP 1 & 2] Ingestion, Multimodal Feature Engineering & Spell Aggregation...")
    csv_path = os.path.join('SpaTemp Datasets', 'Arvind-fused dataset', 'fused_ipl_weather_pitch_ml.csv')
    spells_df = build_bowler_spells_dataset(csv_path)
    os.makedirs('outputs', exist_ok=True)
    spells_df.to_csv('outputs/bowler_spells_dataset.csv', index=False)
    
    # Step 2: Temporal Split, Preprocessing Pipeline & Model Training
    print("\n[STEP 3, 4, 5, 6] Temporal Splitting (2008-2022 vs 2023-2026), Scikit-Learn Pipeline & Model Benchmarking...")
    results_df, test_predictions, trained_models, preprocessor, feature_names = train_and_evaluate(spells_df)
    
    # Step 3: Domain Findings & Hypothesis Quantification
    print("\n[STEP 7] Domain Findings Quantification & Statistical Hypothesis Testing...")
    findings = run_domain_analysis()
    
    # Step 4: Deliverables & Visualization Generation
    print("\n[STEP 8] High-Resolution Visualization Generation...")
    generate_visualizations()
    
    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.2f} SECONDS!")
    print("=" * 80)
    print("\nBenchmark Comparison Summary:")
    print(results_df.to_string(index=False))
    print("\nGenerated Deliverables in outputs/:")
    for f in sorted(os.listdir('outputs')):
        sz = os.path.getsize(os.path.join('outputs', f))
        print(f" - outputs/{f} ({sz:,} bytes)")
    print("=" * 80)

if __name__ == '__main__':
    run_full_pipeline()
