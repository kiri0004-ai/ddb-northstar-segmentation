import pandas as pd

campaigns = pd.read_csv(
    "./../NorthStar_Data/NorthStar_Campaigns_v2.csv",
    encoding="utf-8-sig"
)

transactions = pd.read_excel(
    "./../NorthStar_Data/NorthStar_Data_v2.xlsx",
    sheet_name="Transactions"
)

print("Transaction lines:", len(transactions))
print("Distinct invoices:", transactions["Invoice"].nunique())
print("Distinct customers:", transactions["CustomerID"].nunique())
print("Total NetRevenue:", round(transactions["NetRevenue"].sum(), 2))
print("Campaign records:", len(campaigns))