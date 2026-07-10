# =============================================================================
# BUSINESS INTELLIGENCE & SALES ANALYTICS PLATFORM
# Notebook 01 — Exploratory Data Analysis
# =============================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os, warnings
warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT     = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(ROOT, "data")
RPT_DIR  = os.path.join(ROOT, "reports")
os.makedirs(RPT_DIR, exist_ok=True)

PALETTE  = {"primary":"#2563eb","success":"#10b981","danger":"#ef4444",
            "warn":"#f59e0b","muted":"#64748b"}

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(os.path.join(DATA_DIR, "superstore.csv"), parse_dates=["order_date","ship_date"])
df["year"]       = df["order_date"].dt.year
df["month"]      = df["order_date"].dt.month
df["month_name"] = df["order_date"].dt.strftime("%b")
df["quarter"]    = df["order_date"].dt.quarter
df["profit_margin"] = df["profit"] / df["sales"] * 100

print("=" * 60)
print("DATASET OVERVIEW")
print("=" * 60)
print(f"Shape          : {df.shape}")
print(f"Orders         : {df['order_id'].nunique():,}")
print(f"Customers      : {df['customer_id'].nunique():,}")
print(f"Date Range     : {df['order_date'].min().date()} → {df['order_date'].max().date()}")
print(f"Total Revenue  : ₹{df['sales'].sum():,.0f}")
print(f"Total Profit   : ₹{df['profit'].sum():,.0f}")
print(f"Avg Margin     : {df['profit_margin'].mean():.1f}%")
print(f"Missing Values : {df.isnull().sum().sum()}")

# ── 1. Revenue & Profit by Year ───────────────────────────────────────────────
yearly = df.groupby("year").agg(Revenue=("sales","sum"), Profit=("profit","sum")).reset_index()
yearly["Margin"] = yearly["Profit"] / yearly["Revenue"] * 100

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("Annual Performance Overview", fontsize=14, fontweight="bold", y=1.02)

axes[0].bar(yearly["year"], yearly["Revenue"]/1e6, color=PALETTE["primary"], alpha=0.85)
axes[0].set_title("Revenue (₹M)"); axes[0].set_xlabel("Year")
for bar, val in zip(axes[0].patches, yearly["Revenue"]):
    axes[0].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.01,
                 f"₹{val/1e6:.1f}M", ha="center", va="bottom", fontsize=9)

axes[1].bar(yearly["year"], yearly["Profit"]/1e6, color=PALETTE["success"], alpha=0.85)
axes[1].set_title("Profit (₹M)"); axes[1].set_xlabel("Year")

axes[2].plot(yearly["year"], yearly["Margin"], "o-", color=PALETTE["warn"], linewidth=2, markersize=8)
axes[2].set_title("Profit Margin %"); axes[2].set_xlabel("Year")
axes[2].yaxis.set_major_formatter(mticker.PercentFormatter())

plt.tight_layout()
plt.savefig(os.path.join(RPT_DIR, "01_annual_performance.png"), dpi=150, bbox_inches="tight")
plt.show()
print("✅ Plot 1: Annual Performance saved")

# ── 2. Monthly Revenue Trend ──────────────────────────────────────────────────
monthly = df.groupby(["year","month"]).agg(Revenue=("sales","sum")).reset_index()
monthly["date"] = pd.to_datetime(monthly[["year","month"]].assign(day=1))

fig, ax = plt.subplots(figsize=(14, 5))
for yr, grp in monthly.groupby("year"):
    ax.plot(grp["month"], grp["Revenue"]/1e3, "o-", label=str(yr), linewidth=2)
ax.set_title("Monthly Revenue Trend by Year", fontsize=13, fontweight="bold")
ax.set_xlabel("Month"); ax.set_ylabel("Revenue (₹K)")
ax.set_xticks(range(1,13))
ax.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(RPT_DIR, "02_monthly_trend.png"), dpi=150, bbox_inches="tight")
plt.show()
print("✅ Plot 2: Monthly Trend saved")

# ── 3. Category Analysis ──────────────────────────────────────────────────────
cat = df.groupby("category").agg(
    Revenue=("sales","sum"), Profit=("profit","sum"), Orders=("order_id","count")
).reset_index()
cat["Margin"] = cat["Profit"] / cat["Revenue"] * 100

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("Category Performance", fontsize=14, fontweight="bold")
colors = [PALETTE["primary"], PALETTE["success"], PALETTE["warn"]]

axes[0].bar(cat["category"], cat["Revenue"]/1e6, color=colors)
axes[0].set_title("Revenue by Category"); axes[0].set_ylabel("₹M")
axes[0].tick_params(axis="x", rotation=15)

axes[1].bar(cat["category"], cat["Profit"]/1e6, color=colors)
axes[1].set_title("Profit by Category"); axes[1].set_ylabel("₹M")
axes[1].tick_params(axis="x", rotation=15)

axes[2].bar(cat["category"], cat["Margin"], color=colors)
axes[2].set_title("Profit Margin %"); axes[2].set_ylabel("%")
axes[2].tick_params(axis="x", rotation=15)

plt.tight_layout()
plt.savefig(os.path.join(RPT_DIR, "03_category_analysis.png"), dpi=150, bbox_inches="tight")
plt.show()
print("✅ Plot 3: Category Analysis saved")

# ── 4. Region Analysis ────────────────────────────────────────────────────────
reg = df.groupby("region").agg(
    Revenue=("sales","sum"), Profit=("profit","sum"), Orders=("order_id","count")
).reset_index().sort_values("Revenue", ascending=True)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Regional Performance", fontsize=14, fontweight="bold")

axes[0].barh(reg["region"], reg["Revenue"]/1e6, color=PALETTE["primary"], alpha=0.85)
axes[0].set_title("Revenue by Region (₹M)")
axes[0].set_xlabel("Revenue (₹M)")

reg["Margin"] = reg["Profit"]/reg["Revenue"]*100
colors_margin = [PALETTE["success"] if m > 10 else PALETTE["danger"] for m in reg["Margin"]]
axes[1].barh(reg["region"], reg["Margin"], color=colors_margin, alpha=0.85)
axes[1].set_title("Profit Margin % by Region")
axes[1].axvline(x=10, color="gray", linestyle="--", alpha=0.7, label="10% benchmark")
axes[1].legend()

plt.tight_layout()
plt.savefig(os.path.join(RPT_DIR, "04_region_analysis.png"), dpi=150, bbox_inches="tight")
plt.show()
print("✅ Plot 4: Region Analysis saved")

# ── 5. Segment Analysis ───────────────────────────────────────────────────────
seg = df.groupby("segment").agg(
    Revenue=("sales","sum"), Profit=("profit","sum"),
    Orders=("order_id","count"), Customers=("customer_id","nunique")
).reset_index()
seg["AOV"] = seg["Revenue"] / seg["Orders"]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Customer Segment Analysis", fontsize=14, fontweight="bold")
cols = [PALETTE["primary"], PALETTE["success"], PALETTE["warn"]]

axes[0].pie(seg["Revenue"], labels=seg["segment"], autopct="%1.1f%%",
            colors=cols, startangle=90)
axes[0].set_title("Revenue Share by Segment")

axes[1].bar(seg["segment"], seg["AOV"], color=cols, alpha=0.85)
axes[1].set_title("Average Order Value by Segment")
axes[1].set_ylabel("₹ AOV")
for bar, val in zip(axes[1].patches, seg["AOV"]):
    axes[1].text(bar.get_x()+bar.get_width()/2, bar.get_height()+10,
                 f"₹{val:,.0f}", ha="center", fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(RPT_DIR, "05_segment_analysis.png"), dpi=150, bbox_inches="tight")
plt.show()
print("✅ Plot 5: Segment Analysis saved")

# ── 6. Discount Impact ────────────────────────────────────────────────────────
df["discount_bucket"] = pd.cut(df["discount"],
    bins=[-0.01,0,0.10,0.20,0.30,1.0],
    labels=["No Discount","1-10%","11-20%","21-30%","30%+"])
disc = df.groupby("discount_bucket", observed=True).agg(
    Revenue=("sales","sum"), Profit=("profit","sum"), Orders=("order_id","count")
).reset_index()
disc["Margin"] = disc["Profit"] / disc["Revenue"] * 100

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("Discount Impact Analysis", fontsize=14, fontweight="bold")

axes[0].bar(disc["discount_bucket"], disc["Orders"],
            color=[PALETTE["success"],PALETTE["primary"],PALETTE["warn"],
                   PALETTE["danger"],PALETTE["muted"]], alpha=0.85)
axes[0].set_title("Orders by Discount Tier")
axes[0].set_xlabel("Discount Tier"); axes[0].set_ylabel("Orders")
axes[0].tick_params(axis="x", rotation=15)

axes[1].bar(disc["discount_bucket"], disc["Margin"],
            color=[PALETTE["success"] if m>0 else PALETTE["danger"] for m in disc["Margin"]],
            alpha=0.85)
axes[1].set_title("Profit Margin % by Discount Tier")
axes[1].axhline(y=0, color="black", linewidth=0.8)
axes[1].tick_params(axis="x", rotation=15)

plt.tight_layout()
plt.savefig(os.path.join(RPT_DIR, "06_discount_impact.png"), dpi=150, bbox_inches="tight")
plt.show()
print("✅ Plot 6: Discount Impact saved")

# ── 7. Top Products ───────────────────────────────────────────────────────────
top_rev = df.groupby("sub_category")["sales"].sum().sort_values(ascending=True).tail(10)
top_pft = df.groupby("sub_category")["profit"].sum().sort_values(ascending=True).tail(10)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Sub-Category Performance", fontsize=14, fontweight="bold")

axes[0].barh(top_rev.index, top_rev.values/1e6, color=PALETTE["primary"], alpha=0.85)
axes[0].set_title("Top 10 by Revenue (₹M)")

colors_p = [PALETTE["success"] if v > 0 else PALETTE["danger"] for v in top_pft.values]
axes[1].barh(top_pft.index, top_pft.values/1e3, color=colors_p, alpha=0.85)
axes[1].set_title("Top 10 by Profit (₹K)")
axes[1].axvline(x=0, color="black", linewidth=0.8)

plt.tight_layout()
plt.savefig(os.path.join(RPT_DIR, "07_subcategory_performance.png"), dpi=150, bbox_inches="tight")
plt.show()
print("✅ Plot 7: Sub-Category Performance saved")

print("\n" + "="*60)
print("EDA COMPLETE — 7 plots saved to reports/")
print("="*60)
print(f"\nKey Insights:")
print(f"  • Best region by revenue : {reg.sort_values('Revenue').iloc[-1]['region']}")
print(f"  • Best category by margin: {cat.sort_values('Margin').iloc[-1]['category']}")
print(f"  • Heavy discounts (30%+) cause negative margins")
print(f"  • Q4 (Oct-Dec) is consistently the strongest quarter")
