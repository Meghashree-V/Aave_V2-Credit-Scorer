# Analysis of Credit Scores

## 1. Score Distribution

The machine learning-based wallet scores are normalized to cover the full 0–1000 range. Below is the distribution of wallet scores (number of wallets in each 100-point bin):

| Score Range   | Number of Wallets |
|--------------|-------------------|
| 0–100        | 2746              |
| 100–200      | 8                 |
| 200–300      | 1                 |
| 300–400      | 1                 |
| 400–500      | 1                 |
| 500–600      | 0                 |
| 600–700      | 1                 |
| 700–800      | 0                 |
| 800–900      | 8                 |
| 900–1000     | 731               |

The plot `score_distribution.png` visualizes this distribution. This bar chart provides a visual summary of how machine learning-based wallet scores are distributed across the 0–1000 range, making it easy to spot clusters of responsible and risky users.

---

## Analysis of Wallet Score Ranges

### Behavior of Wallets in the Lower Range (0–200)
- **Many borrows, few or no repayments:** These wallets often borrow assets but fail to repay, indicating risky or irresponsible behavior.
- **High liquidation rate:** Frequent liquidations suggest poor risk management or exploitative strategies.
- **Little or no deposit activity:** Low engagement with the protocol as a liquidity provider.
- **Short active duration:** Many low scorers have brief or sporadic activity, possibly indicating bot-like or opportunistic usage.

### Behavior of Wallets in the Higher Range (900–1000)
- **Regular deposits:** Consistent supply of assets to the protocol demonstrates reliability.
- **Full or high ratio of repayments to borrows:** These wallets repay what they borrow, showing responsible usage.
- **No or very few liquidations:** Indicates good risk management and avoidance of exploitative practices using ml_credit_scorer.py.
- **Longer active duration:** High scorers tend to have a sustained, ongoing relationship with the protocol.
- **Responsible and consistent protocol usage:** These wallets behave in a way that benefits both themselves and the protocol ecosystem.

---

## 2. Characteristics of Low Scorers
- Many borrows, few/no repayments
- High liquidation rate
- Little or no deposit activity
- Short active duration

## 3. Characteristics of High Scorers
- Regular deposits
- Full or high ratio of repayments to borrows
- No or very few liquidations
- Longer active duration
- Responsible and consistent protocol usage

## 4. Example Wallets

- **Lowest scoring wallets (score 0):**
    - 0x0000000000e189dd664b9ab08a33c4839953852c
    - 0x00001bc47f0973f794f79c16121cee879e272d6a
    - 0x0012a7f00af8a643ba5a6aa187f915b4c13289df
    - ...

- **Highest scoring wallet (score 1000):**
    - 0x00bb88a8309759a7c9f0a5c8e3a9364e8f564a8d

---

## 5. Plots

![Score Distribution](score_distribution.png)

---

## Conclusion

The machine learning model used for scoring is a Random Forest classifier. Random Forest was chosen for its robustness, interpretability, and strong performance on tabular data such as engineered wallet features. The model successfully distinguishes between responsible and risky wallet behaviors, with higher scores for reliable users and lower scores for risky or exploitative usage. The normalization step ensures the entire 0–1000 range is used for clear interpretation.
