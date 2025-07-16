import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# 1. Load transactions

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

# 2. Preprocess and Feature Engineering

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
        deposit_freq = group[group['action'] == 'deposit'].shape[0] / max(1, (group['timestamp'].max() - group['timestamp'].min())/86400)
        borrow_freq = group[group['action'] == 'borrow'].shape[0] / max(1, (group['timestamp'].max() - group['timestamp'].min())/86400)
        days_active = (group['timestamp'].max() - group['timestamp'].min())/86400
        features.append({
            'wallet_address': wallet,
            'total_deposits': deposits,
            'total_borrows': borrows,
            'total_repays': repays,
            'total_redemptions': redemptions,
            'repay_to_borrow_ratio': repay_to_borrow,
            'times_liquidated': liquidations,
            'deposit_frequency': deposit_freq,
            'borrow_frequency': borrow_freq,
            'days_active': days_active,
        })
    return pd.DataFrame(features)

# 3. Generate synthetic labels for demonstration (good: high repay-to-borrow, low liquidations)
def label_wallets(df):
    # This is a heuristic for demo purposes.
    labels = []
    for _, row in df.iterrows():
        if row['repay_to_borrow_ratio'] > 0.8 and row['times_liquidated'] == 0:
            labels.append(1)  # Good
        else:
            labels.append(0)  # Bad
    return np.array(labels)

# 4. Main ML Pipeline

def main():
    if len(sys.argv) != 3:
        print("Usage: python ml_credit_scorer.py user-wallet-transactions.json wallet_scores.csv")
        sys.exit(1)
    json_path, output_path = sys.argv[1:3]
    print(f"Loading {json_path}...")
    df = load_transactions(json_path)
    df = preprocess(df)
    features = engineer_features(df)
    # For demo: create synthetic labels
    labels = label_wallets(features)
    X = features.drop(['wallet_address'], axis=1)
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, labels, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    print("Classification Report (demo labels):\n", classification_report(y_test, y_pred))
    # Predict probabilities for all wallets
    y_prob = clf.predict_proba(X_scaled)[:, 1]  # Probability of 'good' class
    # Map to 0-1000 credit score
    scores = (y_prob * 1000).round().astype(int)
    features['score'] = scores
    features[['wallet_address', 'score']].to_csv(output_path, index=False)
    print(f"Scores saved to {output_path} (ML-based, normalized 0-1000)")

if __name__ == "__main__":
    main()
