import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime

def load_transactions(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    if isinstance(data, dict):
        records = []
        for wallet, txs in data.items():
            for tx in txs:
                tx['wallet_address'] = wallet
                records.append(tx)
        return pd.DataFrame(records)
    elif isinstance(data, list):
        return pd.DataFrame(data)
    else:
        raise ValueError('Unexpected JSON format.')

def preprocess(df):
    df = df.copy()
    df.columns = [c.lower() for c in df.columns]
    if 'wallet_address' not in df.columns:
        if 'user' in df.columns:
            df = df.rename(columns={'user': 'wallet_address'})
        elif 'address' in df.columns:
            df = df.rename(columns={'address': 'wallet_address'})
        elif 'userwallet' in df.columns:
            df = df.rename(columns={'userwallet': 'wallet_address'})
    if 'amount' not in df.columns:
        def extract_amount(ad):
            if isinstance(ad, dict):
                return ad.get('amount', 0)
            try:
                ad_dict = json.loads(ad)
                return ad_dict.get('amount', 0)
            except Exception as e:
                print(f"Could not parse actiondata: {ad}, error: {e}")
                return 0
        df['amount'] = df['actiondata'].apply(extract_amount)
    required = ['wallet_address', 'action', 'amount', 'timestamp']
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")
    df['amount'] = df['amount'].astype(float)
    df['timestamp'] = df['timestamp'].astype(int)
    df = df.sort_values(['wallet_address', 'timestamp'])
    return df

def engineer_features(df):
    features = []
    grouped = df.groupby('wallet_address')
    for wallet, group in grouped:
        group = group.sort_values('timestamp')
        deposits = group[group['action'] == 'deposit']['amount'].sum()
        borrows = group[group['action'] == 'borrow']['amount'].sum()
        repays = group[group['action'] == 'repay']['amount'].sum()
        redemptions = group[group['action'] == 'redeemunderlying']['amount'].sum()
        liquidations = group[group['action'] == 'liquidationcall'].shape[0]
        repay_to_borrow = repays / borrows if borrows > 0 else 0
        borrow_times = group[group['action'] == 'borrow']['timestamp'].values
        repay_times = group[group['action'] == 'repay']['timestamp'].values
        if len(borrow_times) > 0 and len(repay_times) > 0:
            avg_time_to_repay = np.mean([max(rt - bt, 0) for bt, rt in zip(borrow_times, repay_times)])
        else:
            avg_time_to_repay = np.nan
        deposit_freq = group[group['action'] == 'deposit'].shape[0] / max((group['timestamp'].max() - group['timestamp'].min()) / (60*60*24), 1)
        borrow_freq = group[group['action'] == 'borrow'].shape[0] / max((group['timestamp'].max() - group['timestamp'].min()) / (60*60*24), 1)
        max_utilization = borrows / deposits if deposits > 0 else 0
        days_active = (group['timestamp'].max() - group['timestamp'].min()) / (60*60*24)
        last_activity_gap = (datetime.now().timestamp() - group['timestamp'].max()) / (60*60*24)
        unique_assets = len(group['amount'])
        features.append({
            'wallet_address': wallet,
            'total_deposits': deposits,
            'total_borrows': borrows,
            'total_repays': repays,
            'total_redemptions': redemptions,
            'repay_to_borrow_ratio': repay_to_borrow,
            'times_liquidated': liquidations,
            'avg_time_to_repay': avg_time_to_repay,
            'deposit_frequency': deposit_freq,
            'borrow_frequency': borrow_freq,
            'max_utilization': max_utilization,
            'days_active': days_active,
            'last_activity_gap': last_activity_gap,
            'unique_assets': unique_assets
        })
    return pd.DataFrame(features)

def score_wallet(row):
    score = 0
    score += min(row['total_deposits'] / 1000, 100)
    score += (row['repay_to_borrow_ratio'] * 300) if row['repay_to_borrow_ratio'] <= 1 else 300
    score -= row['times_liquidated'] * 50
    if not np.isnan(row['avg_time_to_repay']) and row['avg_time_to_repay'] > 0:
        score += (1 / row['avg_time_to_repay']) * 200
    score = max(0, min(score, 1000))
    return round(score)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python one_step_score.py sample_user_transactions.json sample_wallet_scores.csv")
        sys.exit(1)
    json_path, output_path = sys.argv[1:3]
    print(f"Loading {json_path}...")
    df = load_transactions(json_path)
    print(f"Loaded {len(df)} rows. Head:\n{df.head()}\n")
    df = preprocess(df)
    print(f"After preprocess: {len(df)} rows. Head:\n{df.head()}\n")
    print(f"Engineering features...")
    features = engineer_features(df)
    print(f"After feature engineering: {len(features)} wallets. Head:\n{features.head()}\n")
    print(f"Scoring wallets...")
    features['score'] = features.apply(score_wallet, axis=1)
    min_score = features['score'].min()
    max_score = features['score'].max()
    if max_score > min_score:
        features['score'] = ((features['score'] - min_score) / (max_score - min_score)) * 1000
        features['score'] = features['score'].round().astype(int)
        features.loc[features['score'].idxmin(), 'score'] = 0
        features.loc[features['score'].idxmax(), 'score'] = 1000
    else:
        features['score'] = 1000
    features[['wallet_address', 'score']].to_csv(output_path, index=False)
    print(f"Scores saved to {output_path} (normalized 0-1000)")
