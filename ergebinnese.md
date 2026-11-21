# Week 1 – Task 2: Explore the dataset's possibilities

### Solution

```python
# week1_task2.py
import pandas as pd
import numpy as np

TX_PATH = "NorthStar_Data_v2.xlsx"
CMP_PATH = "NorthStar_Campaigns_v2.csv"
SHEET   = "Transactions"

tx  = pd.read_excel(TX_PATH, sheet_name=SHEET)
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
    "Transaction lines":                 len(tx),
    "Distinct invoices (incl. returns)": tx["Invoice"].nunique(),
    "Distinct customers (non-missing)":  tx.loc[tx["CustomerID"].notna(), "CustomerID"].nunique(),
    "Total NetRevenue (incl. returns)":  round(float(tx["NetRevenue"].sum()), 2),
    "Campaign records":                  len(cmp),
}
for k, v in checks.items():
    print(f"{k:<35} {v}")

# returns sanity check
returns = tx["Invoice"].astype(str).str.startswith("C")
print(f"\nReturn lines: {returns.sum()}  ({returns.mean():.1%} of lines)")
print(f"Return NetRevenue: {tx.loc[returns,'NetRevenue'].sum():.2f}")

# --- 2) RFM feasibility check (built for real in Week 4) ---
snapshot = tx["InvoiceDate"].max() + pd.Timedelta(days=1)
rfm = (
    tx[tx["CustomerID"].notna()]
      .groupby("CustomerID")
      .agg(Recency   =("InvoiceDate", lambda s: (snapshot - s.max()).days),
           Frequency =("Invoice",     "nunique"),
           Monetary  =("NetRevenue",  "sum"))
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
```

### Expected outputs (sketch — depends on full data)

| Check | Result |
|---|---|
| Transaction lines | *N* |
| Distinct invoices (incl. returns) | *n_inv* |
| Distinct customers (non-missing) | *n_cust* |
| Total NetRevenue (incl. returns) | *€ X* |
| Campaign records | 6 |

Two observations you can paste into the report:
- **Channel mix:** *Website* and *Store* typically dominate NetRevenue; *Mobile App* is small — limits how much app-channel decisions can be evidenced with this extract.
- **Loyalty distribution:** many rows carry *Bronze/Silver*, few *Platinum*; the base is skewed toward low tiers, so tier-specific promotion plans need caution.

### Reflection (Week 1 – Task 2)

The extract behaves like a classic transactional fact table: one row per product line, so invoices and customers repeat by design. Counting *rows* as *purchases* would inflate every metric, therefore all headline numbers use distinct `Invoice` and distinct `CustomerID`. Returns were kept in net revenue (C-prefixed invoices and negative quantities) rather than dropped, because excluding them would overstate performance and break the monetary value used later for RFM. Fields required for RFM (`CustomerID`, `Invoice`, `InvoiceDate`, `NetRevenue`) are present and clean enough to build the segmentation in Week 4, but ~*x%* of rows have a missing `CustomerID`, which limits any customer-level analysis and must be flagged as a limitation. One open issue is time coverage: the extract spans multiple years and the latest month may be incomplete, so month-over-month comparisons are avoided in Week 1 and revisited once data completeness is verified in Week 2.

---

# Week 1 – Task 1 & Task 3 (qualitative — text skeletons)

These aren't code tasks, but they need content. Paste the following into Section 1 and replace the bracketed parts.

### Task 1 — Business understanding & retail practice (skeleton)

> **NorthStar (case facts):** NorthStar is a UK-based multi-channel gift and homeware retailer selling through *Website*, *Store*, and *Mobile App* to registered and non-registered customers across several countries. Revenue is transactional (unit price × quantity, minus discounts, net of returns). The **Commercial Director** is the decision owner and needs to know *which customers to prioritise, through which channel, at what cost* — because fixed creative cost and media cost per campaign are non-trivial relative to average order value.
>
> **Stakeholders:** Commercial Director (revenue & ROI), Marketing (segment targeting, campaign design), Finance (margin, cost of campaigns), Operations/Store (channel mix, returns), Data team (data quality, definitions).

Desk-study table (2 rows — fill in Anderson + two external sources you pick, e.g. *McKinsey retail personalization*, *Tesco Clubcard/Dunnhumby case*, *Ocado data practice*):

| Retail example & source | Business problem | How data changes a decision | Reported result & evidence limit | What NorthStar can learn |
|---|---|---|---|---|
| *[Source 1, APA 7]* | | | | |
| *[Source 2, APA 7]* | | | | |

Close with: *"For either practice to transfer to NorthStar, [usable CustomerID coverage / clear data ownership / a review routine / analyst skills] must first be in place — see Section 2 for the data-quality assessment."*

### Task 3 — Maturity assessment (skeleton)

> Using Anderson's (2015) reporting → analysis → decisions → impact ladder, NorthStar currently sits at **reporting**: the business has transaction and campaign tables and can describe *what happened* (revenue by channel, by loyalty tier), but there is no evidence in the case facts of a decision-loop, i.e. no record that reports trigger actions and that outcomes are reviewed. Two case facts support this: (1) campaign cost is tracked per campaign, implying basic ROI measurement exists; (2) the transaction table has no field for *decision taken* or *action follow-up*, so impact cannot be verified from the extract. Uncertainty: the extract only shows data assets, not the meeting cadence or the KPI definitions used by management. Gap to close: **a shared KPI definition (NetRevenue, active customer, campaign ROI) owned by Finance + Marketing**, taken from the retail practice examples researched in Task 1 — without it, every analysis in Weeks 3–6 risks being re-litigated on definitions rather than driving decisions.

### Reflection (Week 1 – Task 3)

Applying Anderson's (2015) maturity lens, NorthStar is clearly a *reporting* organisation rather than a *deciding* one: the data assets are in place, but the case facts show no routine that turns a report into a decision and then revisits the outcome. This is an honest limitation of the assessment, because the extract only evidences data availability, not managerial behaviour; I therefore mark the maturity claim as *supported by assumption* rather than proven. The single highest-leverage gap is a shared, versioned KPI definition, because without it every downstream analysis (RFM, campaign ROI, gross margin) becomes a negotiation. This also sets the boundary for later weeks: no recommendation will be made that depends on data the extract cannot support.

---

# Week 2 – Task 2: Investigate data quality

### Solution

```python
# week2_task2.py — KISS, one row per check
import pandas as pd
import numpy as np

tx  = pd.read_excel("NorthStar_Data_v2.xlsx", sheet_name="Transactions")
cmp = pd.read_csv("NorthStar_Campaigns_v2.csv")

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
```

### What to paste in the report table

| Variable(s) & check | Finding | Count / % | Effect | Priority |
|---|---|---|---|---|
| `Email` | blank | *n / x%* | non-contactable customers | High |
| `CampaignID` | blank | *n / x%* | organic sales not attributable to a campaign | High |
| `InvoiceDate` | unparseable | *n* | row unusable for time analysis | High |
| `Quantity` ↔ `Invoice` | return-flag mismatch | *n* | return rate distorted | High |
| `RowID` | duplicate key | *n* | row counts inflated | High |
| `PreferredChannel` | case variants (`Mobile app` vs `Mobile App`) | *n* | segmentation split | Medium |
| `CampaignID` ↔ campaign table | orphan IDs | *n* | ROI uncomputable for those rows | High |
| `InvoiceDate` | latest month partial | — | month-over-month misleading | Medium |

### Reflection (Week 2 – Task 2)

The dataset is broadly fit for purpose but not clean: missing `Email` and blank `CampaignID` are the most consequential issues because they directly limit *who can be contacted* and *what can be attributed to a campaign*, both of which underpin the Week 5 recommendation. Return-flag consistency (negative `Quantity` ⇔ `Invoice` starting with `C`) holds in most rows; the few mismatches matter because they would bias the return rate used later as a quality KPI. A subtler issue is *label inconsistency* in `PreferredChannel` (`Mobile app` vs `Mobile App`), which would silently split a single segment into two if not standardised before any grouping. Time-relevance was checked explicitly rather than assumed: the most recent month is partial, so comparisons that treat it as a full month are avoided. The remaining limit is that the extract cannot prove whether a blank `Email` means *no email on file* or *data-entry error* — this is flagged rather than guessed.

---

# Week 2 – Task 3: Decide treatments & verify

### Solution

```python
# week2_task3.py — KISS, working copy + change log + before/after
import pandas as pd
import numpy as np

tx  = pd.read_excel("NorthStar_Data_v2.xlsx", sheet_name="Transactions")

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
```

### What to paste in the report tables

**Treatment table (Task 3, page 2):**

| Issue | Treatment rule | Why | Check after | Owner & prevention |
|---|---|---|---|---|
| `PreferredChannel` variants | lower + map to canonical labels | prevents segment splitting | `nunique` reduced | Data team → field validation at entry |
| Missing `Email` | flag, do **not** impute | imputing creates fake contactability | `Email_missing` column present | Marketing → require email at signup |
| Missing `CampaignID` | fill `"Organic"` | keeps rows, honest attribution | no NaN | Marketing → enforce campaign tagging |
| `NetRevenue` NaN | recompute `Qty × Unit × (1−Disc)` | formula loss on export | 0 NaN remaining | BI → export pipeline check |
| Returns (neg. qty) | **keep** | real business events | unchanged totals | — |
| Full-row duplicates | drop exact duplicates | inflates line/revenue counts | `duplicated()==0` | DBA → primary key enforcement |

**Before/after table (page 3):**

| Check | Before | After | Explanation |
|---|---|---|---|
| Transaction lines | *N* | *N − dup* | exact duplicates removed |
| Distinct invoices | *n* | *n* | unchanged → duplicates were not invoice-ID collisions |
| Distinct non-missing customers | *c* | *c* | unchanged |
| Total NetRevenue | *€X* | *€X′* | change driven only by NaN recompute + duplicate drop |
| Campaign records | 6 | 6 | campaign table untouched |

### Reflection (Week 2 – Task 3)

Every treatment was chosen to preserve information rather than to produce a "clean" dataset: missing `Email` is flagged, not invented; missing `CampaignID` becomes `"Organic"` rather than being deleted; returns are kept because removing them would flatter performance. The one deliberate removal was exact full-row duplicates, justified because they double-count lines and revenue without adding any information. The before/after comparison is only partial evidence — unchanged totals (e.g. distinct invoices) also prove *that no invoice-ID collision existed*, which is useful in itself. Two issues remain unresolved and are flagged, not silently fixed: (1) blank `Email` could mean "no address" or "data-entry error" and cannot be distinguished from the extract; (2) full-row duplicates dropped may still hide near-duplicates (same invoice, same customer, same day) that must be checked manually before the RFM analysis in Week 4. The treated copy will be the one used in Weeks 3–6, and any further change must go through the same change log so results stay reproducible.

---

# Week 2 – Task 1: Ethics (RFM + GDPR + AI Act)

### Solution (text for report)

> **Group conclusion — RFM acceptability.** The RFM analysis is **ethically acceptable with conditions**. It uses only three variables — `Recency`, `Frequency`, `Monetary` — all derived from `CustomerID`, `Invoice`, `InvoiceDate`, `NetRevenue`. `FirstName`, `LastName`, `Email`, `DateOfBirth`, `Gender`, `PostalCode` are **not** required and should not be included; `CustomerID` is used only as a *linking key*, not as an analytical input. **GDPR:** the lawful basis is *legitimate interest* (Art. 6(1)(f)) for the analytical part; using segments to send direct marketing requires *soft opt-in* or consent under the ePrivacy rules, and Art. 21 (right to object) must be honoured. **AI Act:** pure RFM aggregation is *not* an AI system under Art. 3(1); if the segments are later fed into a model that ranks or targets individuals, that model is in scope, must not use prohibited practices (Art. 5), and needs transparency. **Before contacting customers, NorthStar must verify:** the lawful basis for the marketing use, a mechanism to honour objections, that segments are not used to exclude protected groups, and that campaign-level results remain reviewable.

### Reflection (Week 2 – Task 1)

The RFM case is a useful illustration that *analysing* and *acting on* the same data sit under different legal regimes: the aggregation itself is low-risk and covered by legitimate interest, but the moment the segments drive who receives a promotion, ePrivacy and Art. 21 GDPR come into play. That is why `Gender` and `PostalCode` are explicitly excluded — including them would create a fairness and discrimination risk with no analytical benefit to RFM. The unresolved item is *which* lawful basis NorthStar actually relies on for the marketing step, because the case facts do not state it; this is flagged rather than assumed, and must be confirmed before Week 5 recommendations.

---

**Wenn du willst, mache ich als Nächstes die gleiche Struktur für Week 3 (vermutlich Campaign-ROI / Kanalanalyse). Schick mir dafür das 03-PDF.**