"""
Model Training & Benchmarking Pipeline
Role: Member 4 - ML & Results (Akilan Pon Ilango)
Institution: SRM Institute of Science and Technology
"""

import pandas as pd
import numpy as np
import os
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from interpret.glassbox import ExplainableBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Feature definitions
NUMERICAL_FEATURES = [
    'innings',
    'powerplay_balls_ratio',
    'middle_balls_ratio',
    'death_balls_ratio',
    'bowler_career_economy',
    'bowler_career_boundary_freq',
    'bowler_strike_rate',
    'opponent_avg_runs_per_over',
    'venue_historical_avg_economy',
    'temperature',
    'relative_humidity',
    'dew_point',
    'dew_spread',
    'wind_speed',
    'is_night_match',
    'pitch_degradation_proxy',
    'innings_pitch_wear'
]

CATEGORICAL_FEATURES = [
    'bowling_team',
    'opponent_team',
    'venue',
    'bowler_type'
]

TARGETS = ['economy_rate', 'boundary_frequency']

def build_preprocessor():
    """Builds a scikit-learn ColumnTransformer for zero-leakage preprocessing."""
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, NUMERICAL_FEATURES),
            ('cat', categorical_transformer, CATEGORICAL_FEATURES)
        ]
    )
    return preprocessor

def get_feature_names(preprocessor, categorical_features, numerical_features):
    """Extracts post-transformation feature names from the ColumnTransformer."""
    cat_encoder = preprocessor.named_transformers_['cat'].named_steps['onehot']
    cat_names = cat_encoder.get_feature_names_out(categorical_features).tolist()
    return numerical_features + cat_names

def train_and_evaluate(df: pd.DataFrame):
    """
    Executes Temporal Split:
      - Train: 2008-2020
      - Validation: 2021-2022
      - Test (Out-of-Time): 2023-2026
    fits Linear Regression, Random Forest, XGBoost, LightGBM, and EBM models,
    and returns evaluation results, predictions, and trained models.
    """
    # Temporal Split
    train_df = df[df['season_year'] <= 2020].copy()
    val_df   = df[(df['season_year'] >= 2021) & (df['season_year'] <= 2022)].copy()
    test_df  = df[df['season_year'] >= 2023].copy()
    
    print(f"Training instances (2008-2020):   {len(train_df)}")
    print(f"Validation instances (2021-2022): {len(val_df)}")
    print(f"Testing instances (2023-2026):    {len(test_df)}")
    
    X_train = train_df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
    X_val   = val_df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
    X_test  = test_df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
    
    preprocessor = build_preprocessor()
    X_train_proc = preprocessor.fit_transform(X_train)
    X_val_proc   = preprocessor.transform(X_val)
    X_test_proc  = preprocessor.transform(X_test)
    
    feature_names = get_feature_names(preprocessor, CATEGORICAL_FEATURES, NUMERICAL_FEATURES)
    
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=150, max_depth=12, random_state=42, n_jobs=-1),
        'XGBoost': XGBRegressor(n_estimators=150, max_depth=6, learning_rate=0.05, random_state=42, n_jobs=-1),
        'LightGBM': LGBMRegressor(n_estimators=150, max_depth=6, learning_rate=0.05, random_state=42, n_jobs=-1, verbose=-1),
        'EBM (Explainable Boosting)': ExplainableBoostingRegressor(random_state=42, n_jobs=-1)
    }
    
    results = []
    trained_models = {}
    test_predictions = {
        'train_df': train_df.reset_index(drop=True),
        'val_df': val_df.reset_index(drop=True),
        'test_df': test_df.reset_index(drop=True),
        'feature_names': feature_names,
        'X_train_proc': X_train_proc,
        'X_val_proc': X_val_proc,
        'X_test_proc': X_test_proc
    }
    
    for target in TARGETS:
        y_train = train_df[target].values
        y_val   = val_df[target].values
        y_test  = test_df[target].values
        
        print(f"\n================ Target: {target} ================")
        for model_name, model in models.items():
            print(f"Training {model_name}...")
            model.fit(X_train_proc, y_train)
            
            # Validation predictions
            y_val_pred = model.predict(X_val_proc)
            val_rmse = np.sqrt(mean_squared_error(y_val, y_val_pred))
            val_mae = mean_absolute_error(y_val, y_val_pred)
            val_r2 = r2_score(y_val, y_val_pred)
            
            # Test predictions
            y_test_pred = model.predict(X_test_proc)
            test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
            test_mae = mean_absolute_error(y_test, y_test_pred)
            test_r2 = r2_score(y_test, y_test_pred)
            
            print(f"[{target} | {model_name}] Val (2021-2022)  -> RMSE: {val_rmse:.4f}, MAE: {val_mae:.4f}, R2: {val_r2:.4f}")
            print(f"[{target} | {model_name}] Test (2023-2026) -> RMSE: {test_rmse:.4f}, MAE: {test_mae:.4f}, R2: {test_r2:.4f}")
            
            results.append({
                'Target': target,
                'Model': model_name,
                'Val_RMSE': round(val_rmse, 4),
                'Val_MAE': round(val_mae, 4),
                'Val_R2': round(val_r2, 4),
                'Test_RMSE': round(test_rmse, 4),
                'Test_MAE': round(test_mae, 4),
                'Test_R2': round(test_r2, 4),
                # Keeping legacy columns for backwards compatibility with any downstream code
                'RMSE': round(test_rmse, 4),
                'MAE': round(test_mae, 4),
                'R2': round(test_r2, 4)
            })
            
            key = f"{target}_{model_name}"
            trained_models[key] = model
            test_predictions[f"{key}_val_pred"] = y_val_pred
            test_predictions[f"{key}_pred"] = y_test_pred
            
    results_df = pd.DataFrame(results)
    
    os.makedirs('outputs', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    results_df.to_csv('outputs/model_comparison.csv', index=False)
    print("\nSaved benchmark metrics to outputs/model_comparison.csv")
    
    joblib.dump(preprocessor, 'models/preprocessor.joblib')
    for k, m in trained_models.items():
        joblib.dump(m, f'models/{k}.joblib')
        
    return results_df, test_predictions, trained_models, preprocessor, feature_names

if __name__ == '__main__':
    df = pd.read_csv('outputs/bowler_spells_dataset.csv')
    train_and_evaluate(df)
