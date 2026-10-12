"""
Feature Engineering Module for Spatio-Temporal IPL Bowler Performance Analysis
Role: Member 4 - ML & Results (Akilan Pon Ilango)
Institution: SRM Institute of Science and Technology
"""

import pandas as pd
import numpy as np
import os
from src.bowler_classifier import get_bowler_type

def parse_season_year(s):
    """Clean season string to numeric year."""
    s = str(s).strip()
    if '/' in s:
        p = s.split('/')
        return int(p[0]) if len(p[1]) > 2 else int(p[0][:2] + p[1])
    return int(s)

def build_bowler_spells_dataset(fused_csv_path: str, min_legal_balls: int = 6) -> pd.DataFrame:
    """
    Ingests ball-by-ball fused dataset, aggregates into Bowler Spells per match,
    and engineers non-leaking chronological features, weather signals, and pitch signals.
    """
    print(f"Loading raw fused dataset from: {fused_csv_path}")
    df = pd.read_csv(fused_csv_path, low_memory=False)
    
    # 1. Date & Season parsing
    df['parsed_date'] = pd.to_datetime(df['match_date'], format='mixed', dayfirst=True)
    df['season_year'] = df['season'].apply(parse_season_year)
    
    # 2. Determine Day vs Night match
    # On days with >1 match, match 1 is day (0), match 2 is night (1); single matches are night (1)
    match_dates = df.groupby('match_id').agg({
        'parsed_date': 'first'
    }).reset_index()
    match_dates['date_only'] = match_dates['parsed_date'].dt.date
    match_dates['match_count_on_day'] = match_dates.groupby('date_only')['match_id'].transform('count')
    match_dates['rank_on_day'] = match_dates.groupby('date_only')['match_id'].rank(method='first')
    
    match_dates['is_night_match'] = np.where(
        (match_dates['match_count_on_day'] > 1) & (match_dates['rank_on_day'] == 1),
        0, 1
    )
    night_dict = dict(zip(match_dates['match_id'], match_dates['is_night_match']))
    df['is_night_match'] = df['match_id'].map(night_dict)
    
    # 3. Bowler type classification (Pace vs Spin)
    df['bowler_type'] = df['bowler'].apply(get_bowler_type)
    
    # Standardize venue and teams
    venue_col = 'standard_venue' if 'standard_venue' in df.columns else 'venue'
    
    # 4. Aggregation per Bowler Spell in an Innings of a Match
    df['is_pp'] = (df['over'] < 6) & df['is_legal_delivery']
    df['is_middle'] = (df['over'] >= 6) & (df['over'] < 15) & df['is_legal_delivery']
    df['is_death'] = (df['over'] >= 15) & df['is_legal_delivery']
    
    spell_group = df.groupby(['match_id', 'innings', 'bowling_team', 'batting_team', 'bowler'])
    
    spells = spell_group.agg(
        match_date=('parsed_date', 'first'),
        season_year=('season_year', 'first'),
        venue=(venue_col, 'first'),
        city=('city', 'first'),
        bowler_type=('bowler_type', 'first'),
        is_night_match=('is_night_match', 'first'),
        
        # Deliveries & Runs
        legal_balls=('is_legal_delivery', 'sum'),
        runs_conceded=('bowler_runs_conceded', 'sum'),
        boundaries_conceded=('is_boundary', 'sum'),
        wickets_taken=('bowler_wicket', 'sum'),
        
        # Phase balls
        pp_balls=('is_pp', 'sum'),
        middle_balls=('is_middle', 'sum'),
        death_balls=('is_death', 'sum'),
        
        # Weather Signals
        temperature=('temperature_mean', 'first'),
        relative_humidity=('humidity_mean', 'first'),
        dew_point=('dew_point_mean', 'first'),
        wind_speed=('wind_speed_mean', 'first'),
        
        # Pitch Signals
        pitch_season_prior_matches=('pitch_season_prior_matches', 'first'),
        pitch_venue_career_matches=('pitch_venue_career_matches', 'first'),
        pitch_in_match_balls_elapsed=('pitch_in_match_balls_elapsed', 'mean')
    ).reset_index()
    
    # Filter spells with minimum legal deliveries (at least 6 balls = 1 over)
    spells = spells[spells['legal_balls'] >= min_legal_balls].copy()
    
    # Rename batting_team to opponent_team
    spells.rename(columns={'batting_team': 'opponent_team'}, inplace=True)
    
    # Compute Target Variables
    spells['economy_rate'] = 6.0 * spells['runs_conceded'] / spells['legal_balls']
    spells['boundary_frequency'] = 6.0 * spells['boundaries_conceded'] / spells['legal_balls']
    
    # Compute Phase Ratios
    spells['powerplay_balls_ratio'] = spells['pp_balls'] / spells['legal_balls']
    spells['middle_balls_ratio'] = spells['middle_balls'] / spells['legal_balls']
    spells['death_balls_ratio'] = spells['death_balls'] / spells['legal_balls']
    
    # Compute Spatio-Temporal Weather Signals
    spells['dew_spread'] = spells['temperature'] - spells['dew_point']
    
    # Compute Pitch Degradation Signals
    spells['pitch_degradation_proxy'] = spells['pitch_season_prior_matches']
    spells['innings_pitch_wear'] = spells['innings']
    
    # 5. Chronological Historical Features (Zero-Leakage)
    print("Computing zero-leakage chronological historical features...")
    spells = spells.sort_values(by=['match_date', 'match_id', 'innings']).reset_index(drop=True)
    
    unique_dates = spells['match_date'].drop_duplicates().sort_values().tolist()
    
    # Initialize trackers
    bowler_stats = {}   # bowler -> {'runs': 0, 'balls': 0, 'boundaries': 0, 'wickets': 0}
    opp_stats = {}      # team -> {'runs': 0, 'balls': 0}
    venue_stats = {}    # venue -> {'runs': 0, 'balls': 0}
    
    bowler_hist_econ = []
    bowler_hist_bound = []
    bowler_hist_sr = []
    opp_hist_econ = []
    venue_hist_econ = []
    
    global_runs = 0
    global_balls = 0
    global_boundaries = 0
    global_wickets = 0
    
    # Group spells by match_date to update stats only AFTER all spells on that date
    for current_date, date_spells in spells.groupby('match_date', sort=False):
        for idx, row in date_spells.iterrows():
            b = row['bowler']
            opp = row['opponent_team']
            v = row['venue']
            
            # Bowler historical economy & boundary freq & strike rate
            if b in bowler_stats and bowler_stats[b]['balls'] >= 12:
                b_econ = 6.0 * bowler_stats[b]['runs'] / bowler_stats[b]['balls']
                b_bound = 6.0 * bowler_stats[b]['boundaries'] / bowler_stats[b]['balls']
                b_sr = (bowler_stats[b]['balls'] / bowler_stats[b]['wickets']) if bowler_stats[b]['wickets'] > 0 else 30.0
            else:
                b_econ = (6.0 * global_runs / global_balls) if global_balls > 0 else 8.0
                b_bound = (6.0 * global_boundaries / global_balls) if global_balls > 0 else 1.2
                b_sr = (global_balls / global_wickets) if global_wickets > 0 else 24.0
            
            # Opponent team scoring rate
            if opp in opp_stats and opp_stats[opp]['balls'] >= 30:
                o_econ = 6.0 * opp_stats[opp]['runs'] / opp_stats[opp]['balls']
            else:
                o_econ = (6.0 * global_runs / global_balls) if global_balls > 0 else 8.0
                
            # Venue historical economy
            if v in venue_stats and venue_stats[v]['balls'] >= 60:
                v_econ = 6.0 * venue_stats[v]['runs'] / venue_stats[v]['balls']
            else:
                v_econ = (6.0 * global_runs / global_balls) if global_balls > 0 else 8.0
                
            bowler_hist_econ.append(b_econ)
            bowler_hist_bound.append(b_bound)
            bowler_hist_sr.append(b_sr)
            opp_hist_econ.append(o_econ)
            venue_hist_econ.append(v_econ)
            
        # Update trackers after current match date
        for idx, row in date_spells.iterrows():
            b = row['bowler']
            opp = row['opponent_team']
            v = row['venue']
            r = row['runs_conceded']
            balls = row['legal_balls']
            bd = row['boundaries_conceded']
            w = row['wickets_taken']
            
            if b not in bowler_stats:
                bowler_stats[b] = {'runs': 0, 'balls': 0, 'boundaries': 0, 'wickets': 0}
            bowler_stats[b]['runs'] += r
            bowler_stats[b]['balls'] += balls
            bowler_stats[b]['boundaries'] += bd
            bowler_stats[b]['wickets'] += w
            
            if opp not in opp_stats:
                opp_stats[opp] = {'runs': 0, 'balls': 0}
            opp_stats[opp]['runs'] += r
            opp_stats[opp]['balls'] += balls
            
            if v not in venue_stats:
                venue_stats[v] = {'runs': 0, 'balls': 0}
            venue_stats[v]['runs'] += r
            venue_stats[v]['balls'] += balls
            
            global_runs += r
            global_balls += balls
            global_boundaries += bd
            global_wickets += w

    spells['bowler_career_economy'] = bowler_hist_econ
    spells['bowler_career_boundary_freq'] = bowler_hist_bound
    spells['bowler_strike_rate'] = bowler_hist_sr
    spells['opponent_avg_runs_per_over'] = opp_hist_econ
    spells['venue_historical_avg_economy'] = venue_hist_econ
    
    print(f"Feature engineering complete. Total bowler spells: {len(spells)}")
    return spells

if __name__ == '__main__':
    csv_path = 'SpaTemp Datasets/Arvind-fused dataset/fused_ipl_weather_pitch_ml.csv'
    spells_df = build_bowler_spells_dataset(csv_path)
    os.makedirs('outputs', exist_ok=True)
    spells_df.to_csv('outputs/bowler_spells_dataset.csv', index=False)
    print("Saved outputs/bowler_spells_dataset.csv successfully.")
