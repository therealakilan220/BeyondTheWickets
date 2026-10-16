"""
EBM Explanation Generator & Visualizer
Extracts global feature importance, feature shape functions (how each feature affects the outcome),
and saves both publication-quality static PNG figures and comprehensive JSON/CSV summaries to outputs/.
"""

import os
import joblib
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.model_training import NUMERICAL_FEATURES, CATEGORICAL_FEATURES, get_feature_names

def map_term_name(term_tuple, feature_names):
    """Maps index-based term tuples (e.g. (1,) or (1, 9)) to human-readable names."""
    if len(term_tuple) == 1:
        idx = term_tuple[0]
        return feature_names[idx] if idx < len(feature_names) else f"feature_{idx:04d}"
    else:
        names = [feature_names[i] if i < len(feature_names) else f"feature_{i:04d}" for i in term_tuple]
        return " x ".join(names)

def generate_ebm_explanations():
    os.makedirs('outputs', exist_ok=True)
    
    preprocessor = joblib.load('models/preprocessor.joblib')
    feature_names = get_feature_names(preprocessor, CATEGORICAL_FEATURES, NUMERICAL_FEATURES)
    num_scaler = preprocessor.named_transformers_['num'].named_steps['scaler']
    
    targets = ['economy_rate', 'boundary_frequency']
    
    summary_report = {}
    
    for target in targets:
        model_path = f"models/{target}_EBM (Explainable Boosting).joblib"
        if not os.path.exists(model_path):
            print(f"Model file {model_path} not found. Skipping.")
            continue
            
        print(f"\n--- Processing EBM explanations for {target} ---")
        ebm = joblib.load(model_path)
        
        # 1. Compute Named Term Importance
        term_importances = []
        for i, term in enumerate(ebm.term_features_):
            term_name = map_term_name(term, feature_names)
            # Mean absolute contribution of this term across bins / training data
            scores = ebm.term_scores_[i]
            # Overall importance score: weighted/mean absolute score
            imp_val = float(np.mean(np.abs(scores)))
            term_importances.append({
                'term_index': i,
                'term_tuple': list(term),
                'feature_name': term_name,
                'is_interaction': len(term) > 1,
                'importance_score': imp_val
            })
            
        imp_df = pd.DataFrame(term_importances).sort_values(by='importance_score', ascending=False).reset_index(drop=True)
        csv_path = f"outputs/ebm_{target}_feature_importance.csv"
        imp_df.to_csv(csv_path, index=False)
        print(f"Saved feature importance table to {csv_path}")
        
        # Plot Top 15 Overall Global Feature/Interaction Importances
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
        fig, ax = plt.subplots(figsize=(10, 6))
        top15 = imp_df.head(15).iloc[::-1]
        
        colors = ['#1f77b4' if not is_inter else '#ff7f0e' for is_inter in top15['is_interaction']]
        bars = ax.barh(top15['feature_name'], top15['importance_score'], color=colors)
        ax.set_xlabel('Mean Absolute Score (Impact on Prediction)', fontsize=12, fontweight='bold')
        ax.set_title(f'EBM Global Feature Importance: {target.replace("_", " ").title()}', fontsize=14, fontweight='bold', pad=12)
        
        # Add legend for main vs interaction
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#1f77b4', label='Main Effect'),
            Patch(facecolor='#ff7f0e', label='Interaction Term')
        ]
        ax.legend(handles=legend_elements, loc='lower right', frameon=True)
        plt.tight_layout()
        plot_imp_path = f"outputs/ebm_{target}_feature_importance.png"
        fig.savefig(plot_imp_path, dpi=300)
        plt.close(fig)
        print(f"Saved global feature importance chart to {plot_imp_path}")
        
        # 2. Extract and Plot Shape Functions for Key Continuous Domain Features
        # Target specific environmental, pitch, and phase features:
        key_features = [
            'relative_humidity',
            'dew_spread',
            'temperature',
            'pitch_degradation_proxy',
            'death_balls_ratio',
            'powerplay_balls_ratio'
        ]
        
        fig, axes = plt.subplots(2, 3, figsize=(16, 9))
        axes = axes.flatten()
        
        for ax_idx, feat in enumerate(key_features):
            ax = axes[ax_idx]
            if feat in NUMERICAL_FEATURES:
                num_idx = NUMERICAL_FEATURES.index(feat)
                # Find matching 1D term in ebm.term_features_
                term_idx = None
                for t_i, t in enumerate(ebm.term_features_):
                    if len(t) == 1 and t[0] == num_idx:
                        term_idx = t_i
                        break
                        
                if term_idx is not None:
                    # ebm.bins_[term_idx][0] contains bin cutoffs
                    bin_edges = ebm.bins_[term_idx][0]
                    scores = ebm.term_scores_[term_idx]
                    
                    # Unstandardize bin edges back to real units
                    mean_val = num_scaler.mean_[num_idx]
                    scale_val = num_scaler.scale_[num_idx]
                    unscaled_edges = bin_edges * scale_val + mean_val
                    
                    # Compute bin centers for plotting
                    bin_centers = (unscaled_edges[:-1] + unscaled_edges[1:]) / 2.0
                    # Handle scores dimension (last bin includes tails)
                    plot_scores = scores[1:len(bin_centers) + 1] if len(scores) > len(bin_centers) else scores[:len(bin_centers)]
                    
                    ax.step(bin_centers, plot_scores, where='mid', color='#2ca02c', linewidth=2.2)
                    ax.axhline(0, color='grey', linestyle='--', alpha=0.7)
                    ax.set_title(f"Effect of {feat.replace('_', ' ').title()}", fontsize=11, fontweight='bold')
                    ax.set_ylabel(f"Marginal Impact on {target.replace('_', ' ').title()}", fontsize=9)
                    ax.set_xlabel(f"{feat.replace('_', ' ').title()} (Original Units)", fontsize=9)
                    ax.grid(True, linestyle=':', alpha=0.6)
            
        plt.suptitle(f"EBM Feature Shape Functions: Why Features Affect {target.replace('_', ' ').title()}", fontsize=14, fontweight='bold', y=0.98)
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        shape_plot_path = f"outputs/ebm_{target}_shape_functions.png"
        fig.savefig(shape_plot_path, dpi=300)
        plt.close(fig)
        print(f"Saved shape functions plot to {shape_plot_path}")
        
        # Save key domain explanations into summary report
        summary_report[target] = {
            'top_5_features': imp_df.head(5)[['feature_name', 'importance_score', 'is_interaction']].to_dict(orient='records'),
            'feature_importance_plot': plot_imp_path,
            'shape_functions_plot': shape_plot_path,
            'explanation_description': (
                f"Explainable Boosting Machines (EBM) decompose the predicted {target.replace('_', ' ')} "
                "into additive 1D shape functions and 2D interaction terms. Each shape curve explains "
                "the isolated non-linear marginal effect of that feature on the target."
            )
        }
        
    summary_json_path = 'outputs/ebm_explanations_summary.json'
    with open(summary_json_path, 'w') as f:
        json.dump(summary_report, f, indent=2)
    print(f"\nSaved complete EBM explanations summary to {summary_json_path}")

if __name__ == '__main__':
    generate_ebm_explanations()
