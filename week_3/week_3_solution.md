# Week 3 Assignment Help: Data Exploration and Visualisation for NorthStar

I'll help you work through this assignment step by step. Let me break down each task and provide guidance on how to approach it.

---

## Task 1: Describe the Data

### Compact Profile of Transactions Table

Based on the data provided, here's a summary of the key variables:

**Numeric Variables:**

| Variable | Description | Key Statistics |
|----------|-------------|----------------|
| Quantity | Units purchased per line | Range: -16 to 288; Mean likely ~20-30; Many small purchases (1-12 units) and some bulk orders (40-288) |
| UnitPrice | Price per unit (GBP) | Range: £0.29-£15.95; Median ~£1.65-£2.95 |
| GrossRevenue | Quantity × UnitPrice | Varies widely; Some high-value orders (£100+) |
| DiscountPct | Discount applied | 0-11%; Most transactions 0-7% |
| NetRevenue | Revenue after discount | Includes negatives for returns |
| CostOfGoodsSold | Cost calculation | Needed for profit analysis |
| GrossProfit | NetRevenue - COGS | Varies; Some negative margins |
| InvoiceDeliveryCost | Delivery cost | £0, £3.50-£11.50 depending on channel |

**Categorical Variables:**

| Variable | Categories | Notes |
|----------|------------|-------|
| ProductCategory | Other, Stationery & Craft, Home & Decor, Kitchen & Dining, Bags & Accessories, Garden & Outdoor, Seasonal, Toys & Gifts | "Other" appears frequently - may need review |
| Returned | Yes/No | Returns have negative quantities and invoice starting with "C" |
| Country | UK (majority), Germany, Spain, France, Thailand, Brazil, Italy, Austria, Korea, Channel Islands, European Community | Mostly UK customers |
| LoyaltyMember | Yes/No | Mix of members and non-members |
| LoyaltyTier | None, Bronze, Silver, Gold, Platinum | Tiered loyalty program |
| PreferredChannel | Email, Website, Store, Mobile app | Various preferences |
| PaymentMethod | PayPal, Credit card, Debit card, Bank transfer, Cash | Multiple options |
| SalesChannel | Website, Store, Mobile App | Three main channels |
| MarketingConsent | Yes/No/Blank | Some missing values |

**Date Variables:**

| Variable | Description |
|----------|-------------|
| InvoiceDate | Range: 2024-09-29 to 2026-09-29 (approximately 2 years) |
| DateOfBirth | Customer birth dates |
| CustomerSince | When customer joined |

**Identifier Variables:**

| Variable | Description |
|----------|-------------|
| RowID | Unique per row (T00001-T00151+) |
| Invoice | Invoice number; Repeats for multi-item orders; "C" prefix = returns |
| StockCode | Product identifier; Repeats across transactions |
| CustomerID | Customer identifier; Repeats across purchases |

### Unexpected/Overlooked Observations to Flag:

1. **Negative Quantities on Returns**: Row T00050 (Invoice C559347) shows -12 quantity with -£14.40 NetRevenue. This is a return that needs separate handling.

2. **Invoice Dates Beyond Campaign Periods**: Some invoices occur outside their linked campaign windows - check campaign effectiveness.

3. **Age Discrepancies**: Row T00019 shows RecordedAge=66 but CalculatedAge=61 (5-year difference). Row T00037 shows RecordedAge=35 but CalculatedAge=47 (12-year difference). This data quality issue may affect demographic analysis.

4. **Tenure Discrepancies**: Row T00014 shows CustomerSince=2026-12-17 (future date) with CalculatedTenureYears=-0.2. Data entry error.

5. **Missing Email Values**: Several customers have blank email fields (e.g., T00001, T00076, T00113) - may affect email campaign targeting.

6. **Blank MarketingConsent**: Some records have blank values (T00010, T00029, T00030, T00062, T00114, T00115).

### Compact Profile of Campaigns Table

| Variable | Type | Description |
|----------|------|-------------|
| CampaignID | Identifier | CMP001-CMP006 (6 campaigns) |
| CampaignName | Text | Descriptive names |
| StartDate/EndDate | Date | Campaign periods from Nov 2024 to Oct 2026 |
| ContactChannel | Categorical | Email (3), Store (1), Mobile App (2) |
| AudienceDefinition | Text | Targeting criteria |
| FixedCreativeCost | Numeric | £950-£1,600 |
| MediaCost | Numeric | £180-£600 |
| PlannedContactCost | Numeric | £0-£50 |
| TotalCampaignCost | Numeric | £1,152-£2,200 |

**Observation**: CMP003 (Loyalty Weekend) has £0 PlannedContactCost - in-store campaign. Total costs range from £1,152 to £2,200.

---

## Task 2: Prepare Customer-Level Data

Here's the Python/pandas code to create your customer DataFrame:

```python
import pandas as pd
import numpy as np

# Load your checked transaction data
df = pd.read_excel('NorthStar_Data_v2.xlsx', sheet_name='Transactions')

# Filter to usable CustomerIDs (based on Week 2 decisions)
# Assuming you decided to keep customers with valid IDs
df_clean = df[df['CustomerID'].notna()].copy()

# Identify returns (Invoice starting with 'C')
df_clean['is_return'] = df_clean['Invoice'].astype(str).str.startswith('C')

# For purchases only (exclude returns for purchase count and last purchase date)
df_purchases = df_clean[~df_clean['is_return']].copy()

# Create customer-level summary
customer_df = df_clean.groupby('CustomerID').agg(
    # Last purchase date (exclude returns)
    LastPurchaseDate=('InvoiceDate', lambda x: x[~df_clean.loc[x.index, 'is_return']].max() if any(~df_clean.loc[x.index, 'is_return']) else pd.NaT),
    
    # Purchase count (distinct non-return invoices)
    PurchaseCount=('Invoice', lambda x: df_clean.loc[x.index][~df_clean.loc[x.index, 'is_return']]['Invoice'].nunique()),
    
    # Net revenue (include returns as negatives)
    NetRevenue=('NetRevenue', 'sum')
).reset_index()

# Alternative cleaner approach:
# Purchases only
purchases = df_clean[~df_clean['is_return']]
last_purchase = purchases.groupby('CustomerID')['InvoiceDate'].max().rename('LastPurchaseDate')
purchase_count = purchases.groupby('CustomerID')['Invoice'].nunique().rename('PurchaseCount')
net_revenue = df_clean.groupby('CustomerID')['NetRevenue'].sum().rename('NetRevenue')

# Combine
customer_summary = pd.concat([last_purchase, purchase_count, net_revenue], axis=1).reset_index()

print(f"Total customers: {len(customer_summary)}")
print(f"Customers with purchases: {customer_summary['LastPurchaseDate'].notna().sum()}")
print(f"Total purchase count: {customer_summary['PurchaseCount'].sum()}")
print(f"Total net revenue: £{customer_summary['NetRevenue'].sum():,.2f}")
```

### Verification Check:
- Sum of PurchaseCount should equal number of distinct non-return invoices
- Sum of NetRevenue should equal total NetRevenue in transaction data

### Customer Measures Summary:

| Measure | Expected Pattern |
|---------|------------------|
| LastPurchaseDate | Range from 2024-2026; Some customers may have only returns (no purchase date) |
| PurchaseCount | Most customers: 1-3 purchases; Some frequent buyers: 5+ |
| NetRevenue | Wide range; Some negative (return-heavy customers) |

---

## Task 3: Two Crosstabulations

### Crosstabulation 1: Loyalty Tier vs. Purchase Channel

**Question**: Do loyalty members shop through different channels than non-members?

| | Website | Store | Mobile App | **Total** |
|---|---|---|---|---|
| **Platinum** | Count/% | Count/% | Count/% | 100% |
| **Gold** | Count/% | Count/% | Count/% | 100% |
| **Silver** | Count/% | Count/% | Count/% | 100% |
| **Bronze** | Count/% | Count/% | Count/% | 100% |
| **None** | Count/% | Count/% | Count/% | 100% |
| **Total** | 100% | 100% | 100% | |

**What to count**: Number of transactions (or customers) by loyalty tier and sales channel.

**Expected finding**: Higher tiers may prefer mobile app or website; non-members may skew toward store.

```python
# Crosstab code
crosstab1 = pd.crosstab(
    df_clean['LoyaltyTier'], 
    df_clean['SalesChannel'],
    margins=True
)
crosstab1_pct = pd.crosstab(
    df_clean['LoyaltyTier'], 
    df_clean['SalesChannel'],
    normalize='index'
) * 100
print(crosstab1)
print(crosstab1_pct.round(1))
```

---

### Crosstabulation 2: Marketing Consent vs. Preferred Channel

**Question**: Are customers who consent to marketing more likely to prefer email?

| | Email | Website | Store | Mobile app | **Total** |
|---|---|---|---|---|---|
| **Consent = Yes** | Count/% | Count/% | Count/% | Count/% | 100% |
| **Consent = No** | Count/% | Count/% | Count/% | Count/% | 100% |
| **Consent = Blank** | Count/% | Count/% | Count/% | Count/% | 100% |
| **Total** | 100% | 100% | 100% | 100% | |

**What to count**: Number of customers by marketing consent and preferred channel.

**Expected finding**: Consent=Yes should correlate with Email preference; but some consenting customers may prefer other channels (opportunity for channel expansion).

```python
# Fill blank marketing consent
df_clean['MarketingConsent'] = df_clean['MarketingConsent'].fillna('Blank')

crosstab2 = pd.crosstab(
    df_clean['MarketingConsent'], 
    df_clean['PreferredChannel'],
    margins=True
)
crosstab2_pct = pd.crosstab(
    df_clean['MarketingConsent'], 
    df_clean['PreferredChannel'],
    normalize='index'
) * 100
print(crosstab2)
print(crosstab2_pct.round(1))
```

---

## Task 4: Three Different Visualisations

### Visualisation 1: Histogram - Distribution of Net Revenue per Transaction

**Why this type fits**: NetRevenue is a continuous numeric variable. A histogram shows the distribution, revealing skewness and outliers.

**What it shows**: Most transactions likely cluster at low values (£0-£50), with a long tail of high-value orders.

```python
import matplotlib.pyplot as plt
import seaborn as sns

fig, ax = plt.subplots(figsize=(10, 6))
# Exclude extreme outliers for visibility
df_plot = df_clean[df_clean['NetRevenue'].between(-50, 200)]
ax.hist(df_plot['NetRevenue'], bins=50, edgecolor='white', alpha=0.7)
ax.axvline(df_clean['NetRevenue'].median(), color='red', linestyle='--', label=f"Median: £{df_clean['NetRevenue'].median():.2f}")
ax.set_xlabel('Net Revenue per Line Item (£)')
ax.set_ylabel('Frequency')
ax.set_title('Distribution of Net Revenue per Transaction Line\nNorthStar Transaction Data (2024-2026)')
ax.legend()
plt.tight_layout()
plt.savefig('histogram_netrevenue.png', dpi=150)
```

**Finding**: If median is ~£10-15 and mean is higher, distribution is right-skewed. High-value outliers need investigation.

**Limitation**: Returns (negative values) create a small secondary cluster below zero.

---

### Visualisation 2: Bar Chart - Transaction Count by Product Category

**Why this type fits**: ProductCategory is nominal categorical data. A bar chart compares frequencies across categories clearly.

**What it shows**: Which categories dominate transaction volume.

```python
fig, ax = plt.subplots(figsize=(10, 6))
category_counts = df_clean['ProductCategory'].value_counts()
colors = sns.color_palette('viridis', len(category_counts))
bars = ax.barh(category_counts.index, category_counts.values, color=colors)
ax.set_xlabel('Number of Transaction Lines')
ax.set_ylabel('Product Category')
ax.set_title('Transaction Volume by Product Category\nNorthStar Transaction Data (2024-2026)')
# Add value labels
for bar, val in zip(bars, category_counts.values):
    ax.text(val + 1, bar.get_y() + bar.get_height()/2, f'{val:,}', va='center')
plt.tight_layout()
plt.savefig('bar_category.png', dpi=150)
```

**Finding**: "Other" and "Home & Decor" likely dominate. "Other" being largest may indicate categorisation issues.

**What NorthStar could learn**: Focus marketing on top categories; investigate "Other" composition.

---

### Visualisation 3: Box Plot - Net Revenue by Loyalty Tier

**Why this type fits**: Comparing a numeric variable (NetRevenue) across a categorical grouping (LoyaltyTier). Box plots show median, quartiles, and outliers.

**What it shows**: Whether higher loyalty tiers spend more per transaction.

```python
fig, ax = plt.subplots(figsize=(10, 6))
# Order tiers logically
tier_order = ['None', 'Bronze', 'Silver', 'Gold', 'Platinum']
df_plot = df_clean[df_clean['NetRevenue'].between(-50, 300)]  # Exclude extreme outliers
sns.boxplot(data=df_plot, x='LoyaltyTier', y='NetRevenue', order=tier_order, ax=ax, palette='Blues')
ax.set_xlabel('Loyalty Tier')
ax.set_ylabel('Net Revenue per Transaction Line (£)')
ax.set_title('Net Revenue Distribution by Loyalty Tier\nNorthStar Transaction Data (2024-2026)')
ax.axhline(0, color='red', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('boxplot_loyalty.png', dpi=150)
```

**Finding**: If medians increase with tier, loyalty program is effective. If not, investigate.

**Limitation**: Box plots hide sample size differences between tiers.

---

### Revised Visualisation (Choose One to Improve)

**Example Revision**: The histogram may be hard to read with returns included. Revise to:

```python
# Revised: Separate positive and negative values
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: Purchases only
purchases = df_clean[df_clean['NetRevenue'] > 0]
axes[0].hist(purchases['NetRevenue'].clip(upper=200), bins=40, edgecolor='white', color='steelblue')
axes[0].set_title('Distribution of Positive Net Revenue (Purchases)')
axes[0].set_xlabel('Net Revenue (£)')
axes[0].set_ylabel('Frequency')

# Right: Returns only
returns = df_clean[df_clean['NetRevenue'] < 0]
axes[1].hist(returns['NetRevenue'], bins=20, edgecolor='white', color='coral')
axes[1].set_title('Distribution of Negative Net Revenue (Returns)')
axes[1].set_xlabel('Net Revenue (£)')
axes[1].set_ylabel('Frequency')

plt.suptitle('Net Revenue Distribution: Purchases vs Returns\nNorthStar Transaction Data', fontsize=14)
plt.tight_layout()
plt.savefig('histogram_revised.png', dpi=150)
```

**What changed**: Split positive and negative values into separate panels. This makes each distribution clearer and highlights that returns are a small proportion with distinct patterns.

---

## Report Section 3: Summary

### Main Findings:

1. **Data spans ~2 years** (Sept 2024 - Sept 2026) with ~150 transaction lines in sample. Full dataset likely larger.

2. **Most transactions are UK-based** with small international presence (Germany, Spain, France, etc.).

3. **Product mix**: "Other" category dominates - needs investigation. Home & Decor and Kitchen & Dining are significant.

4. **Loyalty tiers**: Mix of None through Platinum. Higher tiers may show different channel preferences.

5. **Returns exist** (~2-3% of lines) with negative revenues. These require separate tracking.

6. **Data quality issues**: Age discrepancies (recorded vs calculated), future CustomerSince dates, missing emails.

### Limitations:

- Sample size limited in provided data (may be subset)
- Age and tenure fields have inconsistencies
- Some customers have missing demographic data
- Campaign attribution unclear for many transactions

### Question for Week 4:

**"Which customer segments (based on RFM and behaviour) should NorthStar prioritise for retention vs. growth campaigns, and how do their channel preferences differ?"**

This question links Week 3 exploration to Week 4 segmentation and has clear commercial value.

---

## Appendix: Full Variable Profile (for report appendix)

| Variable | Type | N Used | Missing | Key Stats / Categories |
|----------|------|--------|---------|------------------------|
| CustomerID | ID | ~100+ | 0 (if filtered) | Repeats 1-5+ times |
| Invoice | ID | 150+ | 0 | C-prefix = returns |
| StockCode | ID | ~100 | 0 | Product identifier |
| ProductCategory | Nominal | 150 | 0 | 8 categories |
| Quantity | Ratio | 150 | 0 | Range: -16 to 288 |
| UnitPrice | Ratio | 150 | 0 | Range: £0.29-£15.95 |
| NetRevenue | Ratio | 150 | 0 | Range: -£17 to £200+ |
| InvoiceDate | Date | 150 | 0 | 2024-09-29 to 2026-09-29 |
| Returned | Nominal | 150 | 0 | Yes/No |
| Country | Nominal | 150 | 0 | 12 countries |
| LoyaltyTier | Ordinal | 150 | 0 | None/Bronze/Silver/Gold/Platinum |
| PreferredChannel | Nominal | 150 | 0 | 4 channels |
| MarketingConsent | Nominal | 150 | ~6 | Yes/No/Blank |

---

Would you like me to help you with any specific part of this analysis, such as writing the full report narrative, creating additional visualisations, or running specific calculations?