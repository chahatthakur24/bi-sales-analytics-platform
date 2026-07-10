# =============================================================================
# DATA PREPROCESSING — Standardize Kaggle Superstore column names
# Run this ONCE before running any notebooks
# =============================================================================
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__))

df = pd.read_csv(os.path.join(DATA_DIR, "superstore.csv"))

print("Original columns:", list(df.columns))
print("Shape:", df.shape)

# ── Rename Kaggle columns to match notebook expectations ──────────────────────
df = df.rename(columns={
    "Row ID":        "row_id",
    "Order ID":      "order_id",
    "Order Date":    "order_date",
    "Ship Date":     "ship_date",
    "Ship Mode":     "ship_mode",
    "Customer ID":   "customer_id",
    "Customer Name": "customer_name",
    "Segment":       "segment",
    "Country":       "country",
    "City":          "city",
    "State":         "state",
    "Postal Code":   "postal_code",
    "Region":        "region",
    "Product ID":    "product_id",
    "Category":      "category",
    "Sub-Category":  "sub_category",
    "Product Name":  "product_name",
    "Sales":         "sales",
    "Quantity":      "quantity",
    "Discount":      "discount",
    "Profit":        "profit",
})

# ── Add missing columns notebooks expect ─────────────────────────────────────
import numpy as np
np.random.seed(42)

# unit_price — derive from sales, quantity, discount
df["unit_price"] = (df["sales"] / df["quantity"] / (1 - df["discount"].clip(upper=0.99))).round(2)

# returned — simulate 5% return rate
df["returned"] = np.random.choice(["Yes", "No"], size=len(df), p=[0.05, 0.95])

# ── Parse dates ───────────────────────────────────────────────────────────────
df["order_date"] = pd.to_datetime(df["order_date"])
df["ship_date"]  = pd.to_datetime(df["ship_date"])

# ── Save ──────────────────────────────────────────────────────────────────────
df.to_csv(os.path.join(DATA_DIR, "superstore.csv"), index=False)

print("\nStandardized columns:", list(df.columns))
print(f"Shape: {df.shape}")
print(f"Date range: {df['order_date'].min().date()} → {df['order_date'].max().date()}")
print(f"Orders: {df['order_id'].nunique():,}")
print(f"Customers: {df['customer_id'].nunique():,}")
print(f"Revenue: ${df['sales'].sum():,.0f}")
print(f"\n✅ superstore.csv standardized and ready!")
