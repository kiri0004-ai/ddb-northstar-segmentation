FILES

NorthStar_Data_v2.xlsx contains Transactions, Campaigns and README sheets.
NorthStar_Transactions_v2.csv contains the same transaction data.
NorthStar_Campaigns_v2.csv contains the same campaign data.

Choose the workbook or the two CSV files. They are alternative formats of
the same data, not additional transactions. No particular tool is required.

Keep the supplied files unchanged and work on a copy. Check the data before
using it and record relevant treatment choices. Coverage figures in the case
describe the intended business entities. Exact identifier counts in an
unchecked extract may differ. Investigate differences rather than forcing
the totals to match. Do not remove repeated invoice or customer IDs simply
because they repeat.


FIELD GUIDE

RowID: Identifier for a supplied transaction line.
Invoice: Invoice identifier. The C prefix denotes a return rather than a
  purchase. Check the identifier and supporting evidence before classification.
StockCode: Product identifier.
Description: Recorded product description.
ProductCategory: Recorded product category.
Quantity: Units on the line. Returns use non-positive quantities.
InvoiceDate: Recorded invoice date and time. Use calendar dates for RFM.
UnitPrice: Price per unit in GBP, excluding VAT and delivery charges.
GrossRevenue: Quantity multiplied by UnitPrice.
DiscountPct: Recorded discount as a decimal proportion (0.06 means 6%).
NetRevenue: Gross revenue after the recorded discount, including negative
  return lines. This is revenue, not profit.
Returned: Recorded indication of returned merchandise. No return reason
  is supplied.
CustomerID: Internal identifier linking transactions to a recorded customer.
FirstName: Recorded customer first name.
LastName: Recorded customer last name.
Email: Recorded customer email address.
DateOfBirth: Recorded date of birth.
RecordedAge: Age stored in the customer data.
CalculatedAge: Supplied comparison age. Check its consistency and reference
  date before relying on it. Neither age field describes age at every purchase.
Gender: Recorded customer gender.
CustomerSince: Recorded start date of the customer relationship.
RecordedTenureYears: Stored length of the customer relationship in years.
CalculatedTenureYears: Supplied comparison tenure. Check its consistency
  and reference date before relying on it.
Country: Recorded customer country.
City: Recorded customer city.
PostalCode: Recorded customer postal code. Keep as text.
MarketingConsent: Recorded consent status when the extract was created.
  Missing means unknown. Consent history and wording are not supplied.
LoyaltyMember: Recorded current loyalty membership status.
LoyaltyTier: Recorded current loyalty tier. Qualification rules and history
  are not supplied. A non-member may have no tier.
PreferredChannel: Customer's recorded preferred interaction channel.
  It is not the channel of a particular purchase.
PaymentMethod: Recorded payment method.
SalesChannel: Recorded invoice purchase channel: Store, Website or Mobile App.
UnitCost: Synthetic estimated product cost per unit in GBP.
CostOfGoodsSold: Quantity multiplied by UnitCost. Returns can be negative.
GrossProfit: NetRevenue minus CostOfGoodsSold. Excludes delivery, campaign,
  payment, tax and overhead costs. This is not net profit.
GrossMarginPct: GrossProfit divided by NetRevenue when NetRevenue is positive.
  Blank otherwise. The workbook calculates the full ratio; the CSV rounds
  the ratio to four decimal places.
InvoiceDeliveryCost: Synthetic company delivery cost in GBP for an invoice,
  repeated across its lines. Aggregate once per invoice, not once per line.
  Store invoices have a recorded delivery cost of zero.
CampaignID: Recorded campaign or promotion code at invoice level, when
  available. A blank does not prove that no campaign exposure occurred.

CAMPAIGN TABLE

CampaignID: Identifier linking a campaign to recorded transaction codes.
CampaignName: Campaign name.
StartDate and EndDate: Campaign period, including both dates.
ContactChannel: Campaign contact channel.
AudienceDefinition: Description of the campaign's intended audience.
FixedCreativeCost: Fixed creative cost in GBP.
MediaCost: Media cost in GBP.
PlannedContactCost: Total planned contact cost in GBP, not a per-customer rate.
TotalCampaignCost: FixedCreativeCost + MediaCost + PlannedContactCost.

Campaign costs belong to the campaign, not each transaction. Do not sum a
campaign cost again for every matched product line. Campaign codes support
descriptive analysis; they do not show whether a campaign caused a purchase.