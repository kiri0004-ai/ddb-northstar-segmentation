import pandas as pd
import numpy as np

tx  = pd.read_excel("./../NorthStar_Data/NorthStar_Data_v2.xlsx", sheet_name="Transactions")
cmp = pd.read_csv("./../NorthStar_Data/NorthStar_Campaigns_v2.csv")

# --- type coercion first (Excel formulas may be strings) ---
num_cols = ["Quantity", "UnitPrice", "NetRevenue", "DiscountPct", "UnitCost", "RecordedAge", "CalculatedAge", "RecordedTenureYears", "CalculatedTenureYears"]
for c in num_cols:
    tx[c] = pd.to_numeric(tx[c], errors="coerce")
tx["InvoiceDate"]  = pd.to_datetime(tx["InvoiceDate"],  errors="coerce")
tx["DateOfBirth"]  = pd.to_datetime(tx["DateOfBirth"],  errors="coerce")

N = len(tx)

def row(variable, finding, count, effect, priority):
    pct = f"{count / N:.1%}" if isinstance(count, (int, np.integer)) else "—"
    return dict(variable=variable, finding=finding, count=count, pct=pct, effect=effect, priority=priority)

issues = []

# 1) Missing values (top offenders only, KISS)
for c in ["Email", "MarketingConsent", "DiscountPct", "CampaignID"]:
    n = tx[c].isna().sum()
    if n:
        issues.append(row(c, "blank / null", n,
            "affects contactability, campaign attribution, or discount calculation", "high" if c in ("Email","CampaignID") else "medium"))

# 2) Invalid dates
issues.append(row("InvoiceDate", "non-parseable date", tx["InvoiceDate"].isna().sum(),
                  "row cannot be placed in time → excluded from time-based analysis", "high"))

# 3) Return consistency: negative Quantity ⇔ Invoice starts with 'C'
neg   = tx["Quantity"] < 0
c_inv = tx["Invoice"].astype(str).str.startswith("C")
bad   = (neg ^ c_inv).sum()
issues.append(row("Quantity vs Invoice", "return flag mismatch (negative qty without C, or vice versa)", int(bad),
                  "return rate may be miscomputed", "high"))

# 4) Zero/negative revenue on non-return lines
bad_rev = ((tx["NetRevenue"] <= 0) & ~c_inv).sum()
issues.append(row("NetRevenue", "≤ 0 on non-return line", int(bad_rev),
                  "revenue aggregation distorted", "medium"))

# 5) Duplicates
issues.append(row("RowID", "duplicated primary key", int(tx["RowID"].duplicated().sum()),
                  "row counts inflated", "high"))
issues.append(row("full row", "exact duplicate records", int(tx.duplicated().sum()),
                  "over-count of lines/revenue", "high"))

# 6) Inconsistencies in categorical values
for c in ["PreferredChannel", "SalesChannel", "Country", "LoyaltyTier"]:
    n_unique = tx[c].nunique(dropna=True)
    issues.append(row(c, f"{n_unique} distinct raw labels (check case/whitespace)", 0,
                      "grouping may split what should be one category", "medium"))

# 7) Relationship: CampaignID in tx must exist in campaign table
orphan = set(tx["CampaignID"].dropna()) - set(cmp["CampaignID"])
issues.append(row("CampaignID", f"orphan campaign IDs {sorted(orphan)}", len(orphan),
                  "campaign-level ROI cannot be computed for these", "high"))

# 8) Time relevance
print("InvoiceDate range:", tx["InvoiceDate"].min(), "→", tx["InvoiceDate"].max())
print("Latest full month vs latest partial month:", tx["InvoiceDate"].dt.to_period("M").value_counts().head(3).to_string())

report = pd.DataFrame(issues)
print("\nData-quality findings:\n", report.to_string(index=False))
