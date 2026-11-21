# week2_task3.py — KISS, working copy + change log + before/after
import pandas as pd
import numpy as np

tx  = pd.read_excel("./../NorthStar_Data/NorthStar_Data_v2.xlsx", sheet_name="Transactions")

# ---------- helper: baseline checks (same rules as Week 1) ----------
def headline(df):
    return {
        "Lines":               len(df),
        "DistinctInvoices":    df["Invoice"].nunique(),
        "DistinctCustomers":   df.loc[df["CustomerID"].notna(), "CustomerID"].nunique(),
        "TotalNetRevenue":     round(float(df["NetRevenue"].sum()), 2),
    }

before = headline(tx)

# ---------- working copy ----------
clean = tx.copy()
log   = []   # change log rows (issue, rule, rows affected, reason)

# Rule 1: standardise PreferredChannel labels
mapping = {"mobile app": "Mobile App", "email": "Email", "store": "Store", "website": "Website"}
old = clean["PreferredChannel"].copy()
clean["PreferredChannel"] = (clean["PreferredChannel"].astype(str)
                                                .str.strip()
                                                .str.lower()
                                                .map(mapping))
changed = (old.astype(str).str.strip().str.lower() != clean["PreferredChannel"].astype(str).str.lower()).sum()
log.append(("PreferredChannel label variants", "lower+map to canonical labels", int(changed),
            "prevents segment fragmentation"))

# Rule 2: flag missing Email (do NOT invent addresses)
clean["Email_missing"] = clean["Email"].isna()
log.append(("Missing Email", "flag, do not impute", int(clean["Email_missing"].sum()),
            "imputing emails would create fake contactability"))

# Rule 3: flag missing CampaignID as 'Organic'
clean["CampaignID"] = clean["CampaignID"].fillna("Organic")
log.append(("Missing CampaignID", "fill literal 'Organic'", int((tx['CampaignID'].isna()).sum()),
            "keeps the row, makes attribution honest"))

# Rule 4: recompute NetRevenue where missing / negative-trap
mask = clean["NetRevenue"].isna()
clean.loc[mask, "NetRevenue"] = (
    clean.loc[mask, "Quantity"] * clean.loc[mask, "UnitPrice"]
    * (1 - pd.to_numeric(clean.loc[mask, "DiscountPct"], errors="coerce").fillna(0))
)
log.append(("NetRevenue missing", "recompute Qty×Unit×(1−Disc)", int(mask.sum()),
            "formulas from source Excel do not always survive export"))

# Rule 5: keep returns — do NOT drop negative quantities
log.append(("Returns (negative qty)", "keep", int((clean["Quantity"] < 0).sum()),
            "returns are real events; dropping them inflates revenue"))

# Rule 6: drop exact full-row duplicates only (not duplicate CustomerIDs)
dups = clean.duplicated().sum()
clean = clean.drop_duplicates()
log.append(("Full-row duplicates", "drop exact duplicates", int(dups),
            "keeps legitimate multi-line invoices intact"))

# ---------- before / after ----------
after = headline(clean)
print("Before:", before)
print("After :", after)
print("\nChange log:\n", pd.DataFrame(log, columns=["issue","rule","rows","why"]).to_string(index=False))
