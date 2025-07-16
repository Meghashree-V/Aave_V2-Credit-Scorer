# Aave V2 Wallet Credit Scorer

## Overview
This project provides a **transparent, one-step Python script** (`credit_scorer.py`) to compute interpretable credit scores for DeFi wallets based on Aave V2 transaction data. The approach is fully rule-based (no black-box ML), designed for clarity, extensibility, and practical DeFi risk assessment.

---

## Scoring Methodology (Logic)
- **Features engineered per wallet:**
  - Number and amounts of deposits, borrows, repayments, redemptions, liquidations
  - Repay-to-borrow ratio
  - Deposit/borrow frequency per day
  - Average time to repay
  - Maximum utilization (borrow/deposit)
  - Days active, last activity gap
- **Score calculation:**
  - Rewards positive behaviors (deposits, repayments, longevity, responsible ratios)
  - Penalizes risky actions (liquidations, low repayments, high utilization)
  - Rule-based additive formula (see `credit_scorer.py` for exact weights)
  - Raw scores are linearly normalized to 0–1000 for clear ranking
- **Transparency:**
  - Every feature and weight is visible in the code for audit and adjustment
  - Easy to extend: add new features or tune weights as needed

---

## Architecture
- **Single-file:** All logic is in `credit_scorer.py` (no external modules)
- **Input:** `user-wallet-transactions.json` (DeFi transaction data, one file)
- **Output:** `wallet_scores.csv` (wallet address, score), plus optional plots/stats
- **Dependencies:** Only `pandas` and `numpy` (see `requirements.txt`)

---

## Processing Flow
1. **Load** transaction data from JSON
2. **Preprocess:** Standardize columns, extract required fields, clean types
3. **Feature Engineering:** Compute wallet-level features
4. **Scoring:** Apply transparent rule-based logic to features
5. **Normalize:** Rescale scores to 0–1000 (min-max)
6. **Output:** Write results to CSV for analysis or downstream use

---

## How to Run
```bash
pip install -r requirements.txt
python credit_scorer.py user-wallet-transactions.json wallet_scores.csv
```
- Results will be in `wallet_scores.csv` (columns: wallet_address, score)
- Inspect or plot the results as needed

---

## Extensibility
- Add new features by editing the feature engineering section in `credit_scorer.py`
- Adjust scoring weights for different DeFi protocols or risk philosophies
- All logic is visible and modifiable for maximum transparency

---

## Example Output
| wallet_address                              | score |
|---------------------------------------------|-------|
| 0x00000000001accfa9cef68cf5371a23025b6d4b6  | 228   |
| ...                                         | ...   |

---

## License
MIT License. For questions or improvements, open an issue or PR.


This project provides a transparent, explainable credit scoring model for Aave V2 wallets using transaction-level data. The model is designed for clarity, robustness, and practical risk assessment, making it suitable for internship submissions, technical interviews, or DeFi analytics portfolios.

---

## Table of Contents

- [Overview](#overview)
- [Credit Score Philosophy](#credit-score-philosophy)
- [Feature Engineering](#feature-engineering)
- [Scoring Logic](#scoring-logic)
- [Score Distribution](#score-distribution)
- [How to Run](#how-to-run)
- [Project Structure](#project-structure)
- [Sample Output](#sample-output)
- [Notes & Further Improvements](#notes--further-improvements)

---

## Overview

**Goal:** Assign a credit score (0–1000) to each wallet based on its Aave V2 transaction history.  
**Input:** JSON file of user-level Aave V2 transactions (`user-wallet-transactions.json`).  
**Output:** CSV of wallet addresses and credit scores (`wallet_scores.csv`), plus distribution plot and bucket stats.  
**Design:** Fully deterministic, interpretable, and robust to edge cases; no black-box ML.

---

## Project Structure

- **data/**: Contains input transaction data (`user-wallet-transactions.json`).
- **credit_scorer.py**: The single Python script that loads user transaction data, engineers features, computes scores, and writes results.
- **results/**: Stores all outputs, including `wallet_scores.csv`, `score_distribution.png`, and `score_bins.txt`.
- **analysis.md**: Contains detailed analysis, interpretation of results, and example wallet behaviors.
- **requirements.txt**: Lists required Python packages.
- **README.md**: Project documentation and instructions.

**Processing Flow:**
1. Load and preprocess transaction data from `user-wallet-transactions.json`.
2. Engineer features for each wallet (e.g., action counts, ratios, time spans).
3. Apply rule-based scoring logic to compute a raw score per wallet.
4. Normalize all scores to the 0–1000 range.
5. Output results to `results/` and analyze with `analysis.md`.

---

## Credit Score Philosophy

The model reflects real-world credit risk principles, adapted for DeFi, and aligns with the actual distribution of scores in your dataset:

| Score Range | Category         | Description                                   | Wallets |
|-------------|------------------|-----------------------------------------------|---------|
| 0–100       | Critical         | Extremely high risk or bot-like activity      | 240     |
| 100–200     | Very Poor        | Repeated liquidations, almost no repayments   | 33      |
| 200–300     | Poor             | High leverage, low activity, some risk        | 2266    |
| 300–400     | Below Average    | Risky borrowing, limited repayments           | 38      |
| 400–500     | Fair             | Typical user, some risk, moderate activity    | 43      |
| 500–600     | Average          | Reasonable activity, some diversity           | 47      |
| 600–700     | Good             | Healthy, diversified, low risk                | 74      |
| 700–800     | Very Good        | Reliable, consistent, low risk                | 51      |
| 800–900     | Excellent        | Long-term, diverse, no risk                   | 52      |
| 900–1000    | Outstanding      | Top-tier, safest, best DeFi practices         | 652     |

- **Rewards:** Deposits, repayments, longevity, action diversity  
- **Penalties:** Liquidations, over-borrowing, inactivity, bot-like frequency, erratic transaction sizes  
- **Rescaling:** Final scores are linearly rescaled to 0–1000 to ensure a full spread and preserve wallet order

---

## Feature Engineering

Features are engineered per wallet using transaction-level data:

- Number of deposits, borrows, repays, liquidations
- Total and max amounts for each action
- Repay/borrow ratio
- Activity span (days between first and last tx)
- Average time between transactions
- Average and std deviation of transaction amounts
- Number of unique action types
- Transaction frequency per day
- Borrow/deposit ratio (riskiness)

---

## Scoring Logic

**Raw Additive Score:**  
Starts at a base value.  
Rewards for deposits, repay/borrow ratio, longevity, action diversity.  
Penalties for liquidations, high leverage, no repayments, bot-like frequency, erratic tx sizes, short lifespan.

**Linear Min-Max Scaling:**  
Raw scores are linearly mapped to [0, 1000] across the dataset.  
Ensures full use of the score range and neutral, dataset-relative distribution.

**No Black-Box ML:**  
All logic is rule-based and easily auditable.

---

## Score Distribution

Actual bucket counts (after normalization):

| Score Range    | Wallets |
|----------------|---------|
| 0–100          | 240     |
| 100–200        | 33      |
| 200–300        | 2266    |
| 300–400        | 38      |
| 400–500        | 43      |
| 500–600        | 47      |
| 600–700        | 74      |
| 700–800        | 51      |
| 800–900        | 52      |
| 900–1000       | 652     |

**Score Distribution Plot:**  
![Score Distribution](score_distribution.png)

See `analysis.md` for further analysis and score distribution after running the script.

---

## How to Run

**Requirements:** Python 3.10+, pandas, numpy

**Install dependencies:**
```bash
pip install pandas numpy
```

**Run the scoring pipeline:**
```bash
python credit_scorer.py user-wallet-transactions.json wallet_scores.csv
```

**Check results:**  
- `wallet_scores.csv`  
- `score_distribution.png`  
- `results/score_bins.txt`

---

---

## Sample Output

**CSV (wallet_scores.csv):**
| wallet                                    | credit_score |
|--------------------------------------------|--------------|
| 0x00000000001accfa9cef68cf5371a23025b6d4b6 | 228          |
| 0x0000000002032370b971dabd36d72f3e5a7bf1ee | 231          |
| ...                                        | ...          |

---

## Notes & Further Improvements

- **Explainability:** All scoring steps are transparent and easily auditable
- **Robustness:** Handles missing data, outliers, and blank scores
- **Extensibility:** Easy to add new features or adjust weights/rules

**Further work:**
- Explore anomaly/bot detection
- Add more domain-specific features
- Test on larger/more diverse datasets

---

**Author:** Meghashree V

For questions or improvements, please open an issue or fork the repo.


This project assigns a credit score (0–1000) to each wallet address based on their historical activity in the Aave V2 protocol.

---

## Method Chosen

The scoring model is based on engineered features that capture responsible and risky DeFi behaviors. Features include total deposits, borrow/repay activity, liquidation events, and timing/frequency metrics. The scoring logic rewards responsible usage (e.g., full repayments, regular deposits) and penalizes risky or exploitative actions (e.g., repeated liquidations, no repayments). After feature-based scoring, all scores are normalized to the 0–1000 range for interpretability.

---

## Architecture

- **Input:** Raw transaction-level JSON file (can be a list or dict of transactions)
- **Processing:**
  - Load and standardize transaction data
  - Engineer wallet-level features
  - Apply rule-based scoring logic
  - Normalize scores to 0–1000
- **Output:** CSV file with columns: `wallet_address,score`
- **Analysis:** Score distribution and behavioral analysis in `README.md`

---

## Processing Flow

1. **Load Data:**
   - Accepts a JSON file of transaction data.
   - Accepts either a list of transaction dicts or a dict of wallet:transactions.
   - Handles variations in wallet address and amount field names.
2. **Preprocessing:**
   - Standardizes column names and types
   - Extracts `amount` from nested structures if needed
   - Ensures all required columns are present
3. **Feature Engineering:**
   - Calculates wallet-level aggregates: total deposits, borrows, repays, redemptions
   - Computes ratios (e.g., repay-to-borrow), frequencies, activity durations, and liquidation counts
4. **Scoring:**
   - Applies a rule-based formula to assign a raw score based on engineered features
   - Penalizes liquidations, rewards repayments and responsible usage
5. **Normalization:**
   - Rescales all scores so the minimum is 0 and the maximum is 1000
6. **Output:**
   - Writes wallet addresses and their normalized scores to a CSV file

---

## How to Use

1. Place your `user-wallet-transactions.json` file in the `data/` directory.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the scoring pipeline:**
   ```bash
   python credit_scorer.py user-wallet-transactions.json wallet_scores.csv
   ```
4. **Check results:**  
   - `wallet_scores.csv`  
   - `score_distribution.png`  
   - `results/score_bins.txt`

---

## Assumptions
- The input JSON can be a list of transaction records or a dict mapping wallet addresses to lists of transactions.
- Each transaction includes: `wallet_address`, `action`, `amount`, `timestamp` (UNIX time).

## Features Used
- Total deposits, borrows, repays, redemptions
- Repay-to-borrow ratio
- Times liquidated
- Average time to repay
- Deposit/borrow frequency
- Max utilization
- Days active, last activity gap
- Number of unique assets (placeholder)

## Scoring Logic
- Higher score for more deposits, repayments, and responsible usage
- Penalties for liquidations and risky behavior
- Score is normalized to [0, 1000] for interpretability

## Extending the Model
- Add more features (e.g., asset diversity, time-weighted utilization)
- Tune scoring weights
- Use clustering for unsupervised credit risk segmentation

## Score Distribution

Actual score ranges and wallet counts from this dataset:

| Score Range    | Wallets |
|----------------|---------|
| 0–100          | 240     |
| 100–200        | 33      |
| 200–300        | 2266    |
| 300–400        | 38      |
| 400–500        | 43      |
| 500–600        | 47      |
| 600–700        | 74      |
| 700–800        | 51      |
| 800–900        | 52      |
| 900–1000       | 652     |

**Score Distribution Plot:**  
![Score Distribution](score_distribution.png)

See `analysis.md` for analysis and score distribution after running the script.

---

## Visual Summary

A bar chart of the wallet credit score distribution is generated as `score_distribution.png` after running the script. This plot provides a quick visual summary of how wallet scores are distributed across the 0–1000 range. Include this image in your repo and reference it in reports or presentations for clarity.
