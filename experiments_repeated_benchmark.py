"""
Ablation and Repeated Multi-Iteration Benchmark Experiment (15 Runs)
Role: Member 4 - ML & Results (Akilan Pon Ilango)
Institution: SRM Institute of Science and Technology
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import KFold

# -------------------------------------------------------------
# 1. Feature Sets: Baseline vs Pruned (Ablated)
# -------------------------------------------------------------
BASELINE_NUMERICAL = [
    'innings', 'powerplay_balls_ratio', 'middle_balls_ratio', 'death_balls_ratio',
    'bowler_career_economy', 'bowler_career_boundary_freq', 'bowler_strike_rate',
    'opponent_avg_runs_per_over', 'venue_historical_avg_economy', 'temperature',
    'relative_humidity', 'dew_point', 'dew_spread', 'wind_speed', 'is_night_match',
    'pitch_degradation_proxy', 'innings_pitch_wear'
]
BASELINE_CATEGORICAL = ['bowling_team', 'opponent_team', 'venue', 'bowler_type']

# Pruned parameters:
# - Dropped 'dew_point' (multicollinear with dew_spread & temperature)
# - Dropped 'is_night_match' (redundant with continuous micro-weather)
# - Dropped 'bowler_strike_rate' (high noise for economy/boundary rate)
# - Dropped sparse 'bowling_team' & 'opponent_team' (high-cardinality noise, roster churn across years)
PRUNED_NUMERICAL = [
    'innings', 'powerplay_balls_ratio', 'middle_balls_ratio', 'death_balls_ratio',
    'bowler_career_economy', 'bowler_career_boundary_freq',
    'opponent_avg_runs_per_over', 'venue_historical_avg_economy',
    'temperature', 'relative_humidity', 'dew_spread', 'wind_speed',
    'pitch_degradation_proxy', 'innings_pitch_wear'
]
PRUNED_CATEGORICAL = ['venue', 'bowler_type']

TARGETS = ['economy_rate', 'boundary_frequency']

def build_pipeline(num_feats, cat_feats):
    num_tf = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    cat_tf = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    return ColumnTransformer([
        ('num', num_tf, num_feats),
        ('cat', cat_tf, cat_feats)
    ])

def get_models(seed):
    return {
        'Ridge Regression': Ridge(alpha=10.0, random_state=seed),
        'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=10, min_samples_leaf=5, random_state=seed, n_jobs=-1),
        'LightGBM': LGBMRegressor(n_estimators=100, max_depth=5, learning_rate=0.05, num_leaves=31, subsample=0.8, random_state=seed, n_jobs=-1, verbose=-1),
        'XGBoost': XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=seed, n_jobs=-1)
    }

def run_repeated_experiments(n_iterations=15):
    print("=" * 80)
    print(f"RUNNING REPEATED EXPERIMENTS ({n_iterations} ITERATIONS)")
    print("Evaluating Parameter Pruning on Bowler Spell Metrics")
    print("=" * 80)
    
    df = pd.read_csv('outputs/bowler_spells_dataset.csv')
    
    # Store records for all runs
    all_run_records = []
    
    seeds = [42 + i * 7 for i in range(n_iterations)]
    
    for run_idx, seed in enumerate(seeds, start=1):
        print(f"\n---> Iteration {run_idx}/{n_iterations} (Seed: {seed})")
        
        # 5-fold cross-validation split for robust generalization measurement
        kf = KFold(n_splits=5, shuffle=True, random_state=seed)
        
        for feature_config, (num_f, cat_f) in [('Baseline (21 Features)', (BASELINE_NUMERICAL, BASELINE_CATEGORICAL)),
                                               ('Pruned / Optimized (16 Features)', (PRUNED_NUMERICAL, PRUNED_CATEGORICAL))]:
            
            for target in TARGETS:
                y = df[target].values
                X = df[num_f + cat_f]
                
                # We record CV scores across folds for this iteration
                cv_metrics = {m: {'rmse': [], 'mae': [], 'r2': []} for m in ['Ridge Regression', 'Random Forest', 'LightGBM', 'XGBoost']}
                
                for train_idx, val_idx in kf.split(X):
                    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
                    y_train, y_val = y[train_idx], y[val_idx]
                    
                    prep = build_pipeline(num_f, cat_f)
                    X_train_proc = prep.fit_transform(X_train)
                    X_val_proc = prep.transform(X_val)
                    
                    models = get_models(seed)
                    for model_name, model in models.items():
                        model.fit(X_train_proc, y_train)
                        y_pred = model.predict(X_val_proc)
                        
                        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
                        mae = mean_absolute_error(y_val, y_pred)
                        r2 = r2_score(y_val, y_pred)
                        
                        cv_metrics[model_name]['rmse'].append(rmse)
                        cv_metrics[model_name]['mae'].append(mae)
                        cv_metrics[model_name]['r2'].append(r2)
                        
                for model_name in cv_metrics:
                    all_run_records.append({
                        'iteration': run_idx,
                        'seed': seed,
                        'feature_config': feature_config,
                        'target': target,
                        'model': model_name,
                        'cv_rmse': np.mean(cv_metrics[model_name]['rmse']),
                        'cv_mae': np.mean(cv_metrics[model_name]['mae']),
                        'cv_r2': np.mean(cv_metrics[model_name]['r2'])
                    })
                    
    results_df = pd.DataFrame(all_run_records)
    os.makedirs('outputs', exist_ok=True)
    results_df.to_csv('outputs/repeated_experiments_raw.csv', index=False)
    
    # Aggregate Mean and Std across the 15 iterations
    summary = results_df.groupby(['target', 'feature_config', 'model']).agg(
        mean_rmse=('cv_rmse', 'mean'),
        std_rmse=('cv_rmse', 'std'),
        mean_mae=('cv_mae', 'mean'),
        std_mae=('cv_mae', 'std'),
        mean_r2=('cv_r2', 'mean'),
        std_r2=('cv_r2', 'std')
    ).reset_index()
    
    summary.to_csv('outputs/repeated_experiments_summary.csv', index=False)
    print("\n" + "=" * 80)
    print("15-ITERATION BENCHMARK SUMMARY (Mean ± Std)")
    print("=" * 80)
    print(summary.to_string(index=False))
    
    return summary

if __name__ == '__main__':
    run_repeated_experiments(15)
