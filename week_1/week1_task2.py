import pandas as pd

TX_PATH = "./../NorthStar_Data/NorthStar_Data_v2.xlsx"
CMP_PATH = "./../NorthStar_Data/NorthStar_Campaigns_v2.csv"
SHEET = "Transactions"

tx = pd.read_excel(TX_PATH, sheet_name=SHEET)
cmp = pd.read_csv(CMP_PATH)

# --- normalise types (Excel formulas can arrive as NaN) ---
for c in ["Quantity", "UnitPrice", "NetRevenue", "DiscountPct", "UnitCost"]:
    tx[c] = pd.to_numeric(tx[c], errors="coerce")
tx["InvoiceDate"] = pd.to_datetime(tx["InvoiceDate"], errors="coerce")

# --- fallback: recompute NetRevenue when missing ---
mask = tx["NetRevenue"].isna()
tx.loc[mask, "NetRevenue"] = (
        tx.loc[mask, "Quantity"]
        * tx.loc[mask, "UnitPrice"]
        * (1 - tx.loc[mask, "DiscountPct"].fillna(0))
)

# --- 1) Extract checks (Week 1, page 2 table) ---
checks = {
    "Transaction lines": len(tx),
    "Distinct invoices (incl. returns)": tx["Invoice"].nunique(),
    "Distinct customers (non-missing)": tx.loc[tx["CustomerID"].notna(), "CustomerID"].nunique(),
    "Total NetRevenue (incl. returns)": round(float(tx["NetRevenue"].sum()), 2),
    "Campaign records": len(cmp),
}
for k, v in checks.items():
    print(f"{k:<35} {v}")

# returns sanity check
returns = tx["Invoice"].astype(str).str.startswith("C")
print(f"\nReturn lines: {returns.sum()}  ({returns.mean():.1%} of lines)")
print(f"Return NetRevenue: {tx.loc[returns, 'NetRevenue'].sum():.2f}")

# --- 2) RFM feasibility check (built for real in Week 4) ---
snapshot = tx["InvoiceDate"].max() + pd.Timedelta(days=1)
rfm = (
    tx[tx["CustomerID"].notna()]
    .groupby("CustomerID")
    .agg(Recency=("InvoiceDate", lambda s: (snapshot - s.max()).days),
         Frequency=("Invoice", "nunique"),
         Monetary=("NetRevenue", "sum"))
)
print("\nRFM snapshot:", snapshot.date())
print(rfm.describe().round(2).to_string())

# --- 3) Observation A: NetRevenue by SalesChannel ---
obs_a = (tx.groupby("SalesChannel")["NetRevenue"]
         .agg(Revenue="sum", Lines="size")
         .round(2)
         .sort_values("Revenue", ascending=False))
print("\nObservation A — NetRevenue by SalesChannel:\n", obs_a.to_string())

# --- 4) Observation B: distinct customers per LoyaltyTier ---
loyal = tx.drop_duplicates("CustomerID")[["CustomerID", "LoyaltyTier"]]
obs_b = loyal["LoyaltyTier"].value_counts(dropna=False).rename("Customers")
print("\nObservation B — distinct customers per LoyaltyTier:\n", obs_b.to_string())
