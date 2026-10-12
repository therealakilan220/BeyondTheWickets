"""
Visualization and Domain Analysis Module
Role: Member 4 - ML & Results (Akilan Pon Ilango)
Institution: SRM Institute of Science and Technology
Includes comprehensive Venue-Specific (Chinnaswamy vs Chepauk) & Dew / Ball Grip analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from matplotlib.patches import Patch

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8

def clean_feature_label(feat: str) -> str:
    """Format technical feature names for presentation-ready charts."""
    feat = feat.replace('num__', '').replace('cat__', '')
    feat = feat.replace('bowling_team_', 'Bowling: ')
    feat = feat.replace('opponent_team_', 'Opponent: ')
    feat = feat.replace('venue_', 'Venue: ')
    feat = feat.replace('bowler_type_', 'Style: ')
    feat = feat.replace('_', ' ').title()
    return feat

def generate_visualizations():
    os.makedirs('outputs', exist_ok=True)
    
    # Load Data & Models
    spells_df = pd.read_csv('outputs/bowler_spells_dataset.csv')
    comp_df = pd.read_csv('outputs/model_comparison.csv')
    preprocessor = joblib.load('models/preprocessor.joblib')
    
    from src.model_training import NUMERICAL_FEATURES, CATEGORICAL_FEATURES, get_feature_names
    feat_names = get_feature_names(preprocessor, CATEGORICAL_FEATURES, NUMERICAL_FEATURES)
    
    test_df = spells_df[spells_df['season_year'] >= 2023].copy().reset_index(drop=True)
    X_test = test_df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
    X_test_proc = preprocessor.transform(X_test)
    
    rf_econ = joblib.load('models/economy_rate_Random Forest.joblib')
    rf_bound = joblib.load('models/boundary_frequency_Random Forest.joblib')
    lgb_econ = joblib.load('models/economy_rate_LightGBM.joblib')
    
    test_df['pred_econ_rf'] = rf_econ.predict(X_test_proc)
    test_df['pred_econ_lgb'] = lgb_econ.predict(X_test_proc)
    test_df['pred_bound_rf'] = rf_bound.predict(X_test_proc)
    test_df['residual_econ'] = test_df['economy_rate'] - test_df['pred_econ_rf']
    test_df['residual_bound'] = test_df['boundary_frequency'] - test_df['pred_bound_rf']

    # =========================================================================
    # PLOT 1: outputs/model_comparison_rmse.png
    # =========================================================================
    print("Generating Plot 1: outputs/model_comparison_rmse.png...")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
    
    econ_comp = comp_df[comp_df['Target'] == 'economy_rate']
    x = np.arange(len(econ_comp))
    width = 0.35
    
    ax1 = axes[0]
    bars1 = ax1.bar(x - width/2, econ_comp['RMSE'], width, label='RMSE', color='#1f77b4', edgecolor='black', alpha=0.9)
    bars2 = ax1.bar(x + width/2, econ_comp['MAE'], width, label='MAE', color='#ff7f0e', edgecolor='black', alpha=0.9)
    ax1.set_xticks(x)
    ax1.set_xticklabels(econ_comp['Model'], rotation=15, ha='right', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Error Metric Value (Runs / Over)', fontsize=12, fontweight='bold')
    ax1.set_title('A. Bowler Economy Rate Evaluation (2023–2026 Test Set)', fontsize=13, fontweight='bold', pad=12)
    ax1.legend(frameon=True, facecolor='white', framealpha=0.9)
    ax1.set_ylim(0, max(econ_comp['RMSE']) * 1.2)
    
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval + 0.08, f'{yval:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    for bar in bars2:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval + 0.08, f'{yval:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
    bound_comp = comp_df[comp_df['Target'] == 'boundary_frequency']
    ax2 = axes[1]
    b_bars1 = ax2.bar(x - width/2, bound_comp['RMSE'], width, label='RMSE', color='#2ca02c', edgecolor='black', alpha=0.9)
    b_bars2 = ax2.bar(x + width/2, bound_comp['MAE'], width, label='MAE', color='#d62728', edgecolor='black', alpha=0.9)
    ax2.set_xticks(x)
    ax2.set_xticklabels(bound_comp['Model'], rotation=15, ha='right', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Error Metric Value (Boundaries / Over)', fontsize=12, fontweight='bold')
    ax2.set_title('B. Boundary Frequency Evaluation (2023–2026 Test Set)', fontsize=13, fontweight='bold', pad=12)
    ax2.legend(frameon=True, facecolor='white', framealpha=0.9)
    ax2.set_ylim(0, max(bound_comp['RMSE']) * 1.25)
    
    for bar in b_bars1:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, yval + 0.02, f'{yval:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    for bar in b_bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, yval + 0.02, f'{yval:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
    plt.tight_layout()
    plt.savefig('outputs/model_comparison_rmse.png', dpi=300)
    plt.close()

    # =========================================================================
    # PLOT 2: outputs/feature_importance_economy.png
    # =========================================================================
    print("Generating Plot 2: outputs/feature_importance_economy.png...")
    rf_imp = pd.Series(rf_econ.feature_importances_, index=feat_names)
    top15_econ = rf_imp.sort_values(ascending=False).head(15).iloc[::-1]
    labels_econ = [clean_feature_label(name) for name in top15_econ.index]
    
    colors_econ = []
    for f in top15_econ.index:
        if any(w in f for w in ['temperature', 'humidity', 'dew', 'wind', 'is_night']):
            colors_econ.append('#2b5c8f') # Weather
        elif any(p in f for p in ['pitch', 'wear', 'innings']):
            colors_econ.append('#8c564b') # Pitch
        elif any(c in f for c in ['career', 'ratio', 'strike', 'opponent', 'venue']):
            colors_econ.append('#2ca02c') # Cricket Dynamics
        else:
            colors_econ.append('#7f7f7f')
            
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    bars = ax.barh(range(len(top15_econ)), top15_econ.values, color=colors_econ, edgecolor='black', alpha=0.88, height=0.7)
    ax.set_yticks(range(len(top15_econ)))
    ax.set_yticklabels(labels_econ, fontsize=10, fontweight='bold')
    ax.set_xlabel('Gini Feature Importance (Random Forest Regressor)', fontsize=11, fontweight='bold')
    ax.set_title('Top 15 Most Important Features for Bowler Economy Rate Prediction', fontsize=13, fontweight='bold', pad=12)
    
    legend_elements = [
        Patch(facecolor='#2ca02c', edgecolor='black', label='Cricket & Match Dynamics'),
        Patch(facecolor='#2b5c8f', edgecolor='black', label='Spatio-Temporal Weather Signals'),
        Patch(facecolor='#8c564b', edgecolor='black', label='Pitch Degradation Signals')
    ]
    ax.legend(handles=legend_elements, loc='lower right', frameon=True, facecolor='white', framealpha=0.9)
    
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.002, bar.get_y() + bar.get_height()/2, f'{w:.4f}', ha='left', va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('outputs/feature_importance_economy.png', dpi=300)
    plt.close()

    # =========================================================================
    # PLOT 3: outputs/feature_importance_boundaries.png
    # =========================================================================
    print("Generating Plot 3: outputs/feature_importance_boundaries.png...")
    rf_bound_imp = pd.Series(rf_bound.feature_importances_, index=feat_names)
    top15_bound = rf_bound_imp.sort_values(ascending=False).head(15).iloc[::-1]
    labels_bound = [clean_feature_label(name) for name in top15_bound.index]
    
    colors_bound = []
    for f in top15_bound.index:
        if any(w in f for w in ['temperature', 'humidity', 'dew', 'wind', 'is_night']):
            colors_bound.append('#2b5c8f')
        elif any(p in f for p in ['pitch', 'wear', 'innings']):
            colors_bound.append('#8c564b')
        elif any(c in f for c in ['career', 'ratio', 'strike', 'opponent', 'venue']):
            colors_bound.append('#2ca02c')
        else:
            colors_bound.append('#7f7f7f')

    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    bars = ax.barh(range(len(top15_bound)), top15_bound.values, color=colors_bound, edgecolor='black', alpha=0.88, height=0.7)
    ax.set_yticks(range(len(top15_bound)))
    ax.set_yticklabels(labels_bound, fontsize=10, fontweight='bold')
    ax.set_xlabel('Gini Feature Importance (Random Forest Regressor)', fontsize=11, fontweight='bold')
    ax.set_title('Top 15 Most Important Features for Boundary Frequency Prediction', fontsize=13, fontweight='bold', pad=12)
    ax.legend(handles=legend_elements, loc='lower right', frameon=True, facecolor='white', framealpha=0.9)
    
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.002, bar.get_y() + bar.get_height()/2, f'{w:.4f}', ha='left', va='center', fontsize=9, fontweight='bold')
        
    plt.tight_layout()
    plt.savefig('outputs/feature_importance_boundaries.png', dpi=300)
    plt.close()

    # =========================================================================
    # PLOT 4: outputs/weather_vs_economy_actual_predicted.png (4-Panel with Dew focus)
    # =========================================================================
    print("Generating Plot 4: outputs/weather_vs_economy_actual_predicted.png (4-Panel Dew & Weather Impact)...")
    fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=300)
    
    # 4A: Temperature vs Economy
    ax1 = axes[0, 0]
    sns.regplot(
        data=test_df, x='temperature', y='economy_rate',
        scatter_kws={'alpha': 0.22, 'color': '#1f77b4', 's': 22},
        line_kws={'color': '#d62728', 'linewidth': 2.5, 'label': 'Actual Trend'},
        ax=ax1
    )
    sns.regplot(
        data=test_df, x='temperature', y='pred_econ_rf',
        scatter_kws={'alpha': 0.15, 'color': '#2ca02c', 's': 15},
        line_kws={'color': '#2ca02c', 'linewidth': 2.5, 'linestyle': '--', 'label': 'Predicted Trend (RF)'},
        ax=ax1
    )
    ax1.set_xlabel('Mean Ambient Temperature (°C)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Bowler Economy Rate (Runs / Over)', fontsize=11, fontweight='bold')
    ax1.set_title('A. Temperature vs Bowler Economy Rate', fontsize=12, fontweight='bold', pad=10)
    ax1.set_ylim(0, 20)
    ax1.legend(frameon=True, facecolor='white', framealpha=0.9)

    # 4B: Relative Humidity vs Economy
    ax2 = axes[0, 1]
    sns.regplot(
        data=test_df, x='relative_humidity', y='economy_rate',
        scatter_kws={'alpha': 0.22, 'color': '#1f77b4', 's': 22},
        line_kws={'color': '#d62728', 'linewidth': 2.5, 'label': 'Actual Trend'},
        ax=ax2
    )
    sns.regplot(
        data=test_df, x='relative_humidity', y='pred_econ_rf',
        scatter_kws={'alpha': 0.15, 'color': '#ff7f0e', 's': 15},
        line_kws={'color': '#ff7f0e', 'linewidth': 2.5, 'linestyle': '--', 'label': 'Predicted Trend (RF)'},
        ax=ax2
    )
    ax2.set_xlabel('Relative Humidity (%)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Bowler Economy Rate (Runs / Over)', fontsize=11, fontweight='bold')
    ax2.set_title('B. Relative Humidity vs Bowler Economy Rate', fontsize=12, fontweight='bold', pad=10)
    ax2.set_ylim(0, 20)
    ax2.legend(frameon=True, facecolor='white', framealpha=0.9)

    # 4C: Dew Spread (Dew Formation / Grip Loss Index) vs Economy
    ax3 = axes[1, 0]
    sns.regplot(
        data=test_df, x='dew_spread', y='economy_rate',
        scatter_kws={'alpha': 0.22, 'color': '#1f77b4', 's': 22},
        line_kws={'color': '#d62728', 'linewidth': 2.5, 'label': 'Actual Trend'},
        ax=ax3
    )
    sns.regplot(
        data=test_df, x='dew_spread', y='pred_econ_rf',
        scatter_kws={'alpha': 0.15, 'color': '#9467bd', 's': 15},
        line_kws={'color': '#9467bd', 'linewidth': 2.5, 'linestyle': '--', 'label': 'Predicted Trend (RF)'},
        ax=ax3
    )
    ax3.axvspan(0, 6, color='blue', alpha=0.08, label='Heavy Dew Zone (Dew Spread ≤ 6°C)')
    ax3.set_xlabel('Dew Spread: Temperature − Dew Point (°C) [Lower = Heavy Dew / Wet Ball]', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Bowler Economy Rate (Runs / Over)', fontsize=11, fontweight='bold')
    ax3.set_title('C. Dew Spread (Ball Grip Risk) vs Bowler Economy Rate', fontsize=12, fontweight='bold', pad=10)
    ax3.set_ylim(0, 20)
    ax3.legend(frameon=True, facecolor='white', framealpha=0.9)

    # 4D: Dew Point (°C) vs Economy
    ax4 = axes[1, 1]
    sns.regplot(
        data=test_df, x='dew_point', y='economy_rate',
        scatter_kws={'alpha': 0.22, 'color': '#1f77b4', 's': 22},
        line_kws={'color': '#d62728', 'linewidth': 2.5, 'label': 'Actual Trend'},
        ax=ax4
    )
    sns.regplot(
        data=test_df, x='dew_point', y='pred_econ_rf',
        scatter_kws={'alpha': 0.15, 'color': '#8c564b', 's': 15},
        line_kws={'color': '#8c564b', 'linewidth': 2.5, 'linestyle': '--', 'label': 'Predicted Trend (RF)'},
        ax=ax4
    )
    ax4.set_xlabel('Atmospheric Dew Point (°C)', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Bowler Economy Rate (Runs / Over)', fontsize=11, fontweight='bold')
    ax4.set_title('D. Atmospheric Dew Point vs Bowler Economy Rate', fontsize=12, fontweight='bold', pad=10)
    ax4.set_ylim(0, 20)
    ax4.legend(frameon=True, facecolor='white', framealpha=0.9)

    plt.tight_layout()
    plt.savefig('outputs/weather_vs_economy_actual_predicted.png', dpi=300)
    plt.close()

    # =========================================================================
    # PLOT 5: outputs/residual_distribution.png
    # =========================================================================
    print("Generating Plot 5: outputs/residual_distribution.png...")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
    
    ax1 = axes[0]
    sns.histplot(test_df['residual_econ'], kde=True, ax=ax1, color='#1f77b4', edgecolor='black', alpha=0.6, bins=40)
    ax1.axvline(0, color='red', linestyle='--', linewidth=2, label='Zero Error Line')
    ax1.set_xlabel('Prediction Residual (Actual - Predicted Economy Rate)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Spell Frequency', fontsize=11, fontweight='bold')
    ax1.set_title(f'A. Economy Rate Residual Distribution\n(Mean: {test_df["residual_econ"].mean():.3f}, Std: {test_df["residual_econ"].std():.3f})', fontsize=12, fontweight='bold', pad=10)
    ax1.legend(frameon=True, facecolor='white', framealpha=0.9)
    
    ax2 = axes[1]
    sns.histplot(test_df['residual_bound'], kde=True, ax=ax2, color='#2ca02c', edgecolor='black', alpha=0.6, bins=40)
    ax2.axvline(0, color='red', linestyle='--', linewidth=2, label='Zero Error Line')
    ax2.set_xlabel('Prediction Residual (Actual - Predicted Boundary Freq)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Spell Frequency', fontsize=11, fontweight='bold')
    ax2.set_title(f'B. Boundary Frequency Residual Distribution\n(Mean: {test_df["residual_bound"].mean():.3f}, Std: {test_df["residual_bound"].std():.3f})', fontsize=12, fontweight='bold', pad=10)
    ax2.legend(frameon=True, facecolor='white', framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig('outputs/residual_distribution.png', dpi=300)
    plt.close()

    # =========================================================================
    # PLOT 6: outputs/feature_importance_chinnaswamy_vs_chepauk.png (NEW VENUE COMPARISON)
    # =========================================================================
    print("Generating Plot 6: outputs/feature_importance_chinnaswamy_vs_chepauk.png (Chinnaswamy vs Chepauk)...")
    venue_features = [f for f in NUMERICAL_FEATURES if f != 'venue_historical_avg_economy']
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7), dpi=300)
    
    venues_to_plot = [
        ('M Chinnaswamy Stadium', 'M. Chinnaswamy Stadium (Bengaluru - High Altitude, Small Boundaries)', axes[0]),
        ('MA Chidambaram Stadium, Chepauk', 'MA Chidambaram Stadium, Chepauk (Chennai - Coastal Humidity & Turn)', axes[1])
    ]
    
    for venue_name, title, ax in venues_to_plot:
        v_df = spells_df[spells_df['venue'] == venue_name]
        X = v_df[venue_features]
        y = v_df['economy_rate']
        
        pipe = Pipeline([
            ('imp', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler()),
            ('rf', RandomForestRegressor(n_estimators=150, max_depth=8, random_state=42, n_jobs=-1))
        ])
        pipe.fit(X, y)
        rf_m = pipe.named_steps['rf']
        v_imp = pd.Series(rf_m.feature_importances_, index=venue_features).sort_values(ascending=False).head(10).iloc[::-1]
        
        v_labels = [clean_feature_label(name) for name in v_imp.index]
        v_colors = []
        for f in v_imp.index:
            if any(w in f for w in ['temperature', 'humidity', 'dew', 'wind', 'is_night']):
                v_colors.append('#2b5c8f') # Weather
            elif any(p in f for p in ['pitch', 'wear', 'innings']):
                v_colors.append('#8c564b') # Pitch
            else:
                v_colors.append('#2ca02c') # Cricket dynamics
                
        bars = ax.barh(range(len(v_imp)), v_imp.values, color=v_colors, edgecolor='black', alpha=0.88, height=0.65)
        ax.set_yticks(range(len(v_imp)))
        ax.set_yticklabels(v_labels, fontsize=10, fontweight='bold')
        ax.set_xlabel('Feature Importance (Random Forest Gini)', fontsize=11, fontweight='bold')
        ax.set_title(title, fontsize=11, fontweight='bold', pad=10)
        
        for bar in bars:
            w = bar.get_width()
            ax.text(w + 0.003, bar.get_y() + bar.get_height()/2, f'{w:.3f}', ha='left', va='center', fontsize=9, fontweight='bold')
            
        ax.legend(handles=legend_elements, loc='lower right', frameon=True, facecolor='white', framealpha=0.9, fontsize=9)
        
    plt.suptitle('Venue-Specific Feature Importance Comparison: Chinnaswamy vs Chepauk', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('outputs/feature_importance_chinnaswamy_vs_chepauk.png', dpi=300, bbox_inches='tight')
    plt.close()

    # =========================================================================
    # PLOT 7: outputs/dew_impact_ball_grip_analysis.png (NEW DEW & GRIP ANALYSIS)
    # =========================================================================
    print("Generating Plot 7: outputs/dew_impact_ball_grip_analysis.png (In-depth Dew & Wet-Ball Grip Impact)...")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), dpi=300)
    
    # Panel A: Dew Spread vs Economy Rate across Bowler Types in 2nd Innings
    ax1 = axes[0]
    inn2_df = spells_df[spells_df['innings'] == 2].copy()
    inn2_df['dew_bin'] = pd.cut(
        inn2_df['dew_spread'],
        bins=[-np.inf, 6, 12, np.inf],
        labels=['Severe Dew (≤6°C)\n[Wet Ball / No Grip]', 'Moderate Dew (6-12°C)', 'Dry Outfield (>12°C)']
    )
    
    dew_style = inn2_df.groupby(['dew_bin', 'bowler_type'], observed=False)['economy_rate'].mean().reset_index()
    sns.barplot(
        data=dew_style, x='dew_bin', y='economy_rate', hue='bowler_type',
        palette=['#1f77b4', '#ff7f0e'], edgecolor='black', ax=ax1
    )
    ax1.set_ylabel('2nd Innings Mean Economy Rate (Runs / Over)', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Dew Severity / Outfield Wetness Category', fontsize=11, fontweight='bold')
    ax1.set_title('A. 2nd Innings Ball Grip Loss Impact by Bowling Style', fontsize=12, fontweight='bold', pad=10)
    ax1.set_ylim(7.0, 9.5)
    ax1.legend(title='Bowling Style', frameon=True, facecolor='white', framealpha=0.9)
    
    for p in ax1.patches:
        h = p.get_height()
        if not np.isnan(h) and h > 0:
            ax1.text(p.get_x() + p.get_width()/2, h + 0.05, f'{h:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
            
    # Panel B: Chinnaswamy vs Chepauk 2nd Innings Dew Sensitivity
    ax2 = axes[1]
    venue_dew = spells_df[spells_df['venue'].isin(['M Chinnaswamy Stadium', 'MA Chidambaram Stadium, Chepauk']) & (spells_df['innings'] == 2)].copy()
    venue_dew['dew_condition'] = np.where(venue_dew['dew_spread'] <= 8.0, 'High Dew Risk (≤8°C)', 'Low Dew Risk (>8°C)')
    venue_dew['venue_short'] = venue_dew['venue'].replace({
        'M Chinnaswamy Stadium': 'Chinnaswamy (Bengaluru)',
        'MA Chidambaram Stadium, Chepauk': 'Chepauk (Chennai)'
    })
    
    v_dew_summary = venue_dew.groupby(['venue_short', 'dew_condition'], observed=False)['economy_rate'].mean().reset_index()
    sns.barplot(
        data=v_dew_summary, x='venue_short', y='economy_rate', hue='dew_condition',
        palette='crest', edgecolor='black', ax=ax2
    )
    ax2.set_ylabel('2nd Innings Mean Economy Rate (Runs / Over)', fontsize=11, fontweight='bold')
    ax2.set_xlabel('Venue', fontsize=11, fontweight='bold')
    ax2.set_title('B. Venue Sensitivity to Dew during Chases', fontsize=12, fontweight='bold', pad=10)
    ax2.set_ylim(7.0, 10.0)
    ax2.legend(title='Dew Condition', frameon=True, facecolor='white', framealpha=0.9)
    
    for p in ax2.patches:
        h = p.get_height()
        if not np.isnan(h) and h > 0:
            ax2.text(p.get_x() + p.get_width()/2, h + 0.05, f'{h:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig('outputs/dew_impact_ball_grip_analysis.png', dpi=300)
    plt.close()

    print("All updated visualizations generated successfully in outputs/ directory.")

if __name__ == '__main__':
    generate_visualizations()
