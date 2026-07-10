# =============================================================================
# BUSINESS INTELLIGENCE & SALES ANALYTICS PLATFORM
# Notebook 02 — Customer Analytics: RFM Segmentation & Cohort Analysis
# =============================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import os, warnings
warnings.filterwarnings("ignore")

ROOT    = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(ROOT, "data")
RPT_DIR  = os.path.join(ROOT, "reports")
os.makedirs(RPT_DIR, exist_ok=True)

PALETTE = {"primary":"#2563eb","success":"#10b981","danger":"#ef4444",
           "warn":"#f59e0b","purple":"#8b5cf6","muted":"#64748b"}

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(os.path.join(DATA_DIR,"superstore.csv"), parse_dates=["order_date","ship_date"])
SNAPSHOT = df["order_date"].max() + pd.Timedelta(days=1)

print("="*60)
print("CUSTOMER ANALYTICS")
print("="*60)
print(f"Snapshot Date  : {SNAPSHOT.date()}")
print(f"Total Customers: {df['customer_id'].nunique():,}")

# =============================================================================
# RFM ANALYSIS
# =============================================================================
rfm = df.groupby("customer_id").agg(
    last_order  = ("order_date", "max"),
    frequency   = ("order_id",   "count"),
    monetary    = ("sales",      "sum")
).reset_index()

rfm["recency"] = (SNAPSHOT - rfm["last_order"]).dt.days

# Score 1-5 (5 = best)
rfm["R"] = pd.qcut(rfm["recency"],   5, labels=[5,4,3,2,1]).astype(int)
rfm["F"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
rfm["M"] = pd.qcut(rfm["monetary"],  5, labels=[1,2,3,4,5]).astype(int)
rfm["RFM_Score"] = rfm["R"].astype(str) + rfm["F"].astype(str) + rfm["M"].astype(str)
rfm["RFM_Total"] = rfm["R"] + rfm["F"] + rfm["M"]

# Segment
def segment(row):
    r, f, m = row["R"], row["F"], row["M"]
    if r >= 4 and f >= 4 and m >= 4: return "Champions"
    if r >= 3 and f >= 3:             return "Loyal Customers"
    if r >= 4 and f <= 2:             return "New Customers"
    if r >= 3 and f >= 2 and m >= 3:  return "Potential Loyalists"
    if r == 2 and f >= 3:             return "At Risk"
    if r <= 2 and f >= 3:             return "Cant Lose Them"
    if r <= 2 and f <= 2:             return "Lost"
    return "Hibernating"

rfm["Segment"] = rfm.apply(segment, axis=1)

seg_summary = rfm.groupby("Segment").agg(
    Customers=("customer_id","count"),
    Avg_Recency=("recency","mean"),
    Avg_Frequency=("frequency","mean"),
    Avg_Monetary=("monetary","mean"),
    Total_Revenue=("monetary","sum")
).round(1).reset_index().sort_values("Total_Revenue", ascending=False)

print("\nRFM SEGMENT SUMMARY")
print("-"*70)
print(seg_summary.to_string(index=False))

# Plot 1 — RFM Segments
fig, axes = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle("RFM Customer Segmentation", fontsize=14, fontweight="bold")

seg_colors = {
    "Champions":"#10b981","Loyal Customers":"#2563eb",
    "Potential Loyalists":"#8b5cf6","New Customers":"#06b6d4",
    "At Risk":"#f59e0b","Cant Lose Them":"#f97316",
    "Lost":"#ef4444","Hibernating":"#94a3b8"
}
colors = [seg_colors.get(s,"#94a3b8") for s in seg_summary["Segment"]]

axes[0].barh(seg_summary["Segment"], seg_summary["Customers"], color=colors, alpha=0.85)
axes[0].set_title("Customers per Segment")
axes[0].set_xlabel("Number of Customers")
for bar, val in zip(axes[0].patches, seg_summary["Customers"]):
    axes[0].text(bar.get_width()+1, bar.get_y()+bar.get_height()/2,
                 str(val), va="center", fontsize=9)

axes[1].barh(seg_summary["Segment"], seg_summary["Total_Revenue"]/1e6, color=colors, alpha=0.85)
axes[1].set_title("Revenue per Segment (₹M)")
axes[1].set_xlabel("Revenue (₹M)")

plt.tight_layout()
plt.savefig(os.path.join(RPT_DIR,"08_rfm_segments.png"), dpi=150, bbox_inches="tight")
plt.show()
print("✅ Plot 8: RFM Segments saved")

# Plot 2 — RFM Scatter
fig, ax = plt.subplots(figsize=(10, 7))
for seg, grp in rfm.groupby("Segment"):
    ax.scatter(grp["recency"], grp["frequency"],
               s=grp["monetary"]/200, alpha=0.6,
               label=seg, color=seg_colors.get(seg,"gray"))
ax.set_xlabel("Recency (days since last order)")
ax.set_ylabel("Frequency (number of orders)")
ax.set_title("RFM Scatter Plot\n(bubble size = monetary value)", fontsize=13, fontweight="bold")
ax.legend(loc="upper right", fontsize=8)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(RPT_DIR,"09_rfm_scatter.png"), dpi=150, bbox_inches="tight")
plt.show()
print("✅ Plot 9: RFM Scatter saved")

# =============================================================================
# COHORT ANALYSIS
# =============================================================================
df["cohort_month"]  = df.groupby("customer_id")["order_date"].transform("min").dt.to_period("M")
df["order_month"]   = df["order_date"].dt.to_period("M")
df["cohort_index"]  = (df["order_month"] - df["cohort_month"]).apply(lambda x: x.n)

cohort = df.groupby(["cohort_month","cohort_index"])["customer_id"].nunique().reset_index()
cohort_pivot = cohort.pivot(index="cohort_month", columns="cohort_index", values="customer_id")
cohort_size  = cohort_pivot.iloc[:,0]
retention    = cohort_pivot.divide(cohort_size, axis=0) * 100

# Plot 3 — Cohort Heatmap
fig, ax = plt.subplots(figsize=(16, 8))
sns.heatmap(
    retention.iloc[:, :12].round(1),
    annot=True, fmt=".0f", cmap="YlOrRd_r",
    ax=ax, linewidths=0.5,
    cbar_kws={"label": "Retention %"}
)
ax.set_title("Customer Cohort Retention Heatmap\n(% of cohort still active by month)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Months Since First Purchase")
ax.set_ylabel("Cohort (First Purchase Month)")
plt.tight_layout()
plt.savefig(os.path.join(RPT_DIR,"10_cohort_retention.png"), dpi=150, bbox_inches="tight")
plt.show()
print("✅ Plot 10: Cohort Retention saved")

# =============================================================================
# CUSTOMER LIFETIME VALUE
# =============================================================================
clv = df.groupby("customer_id").agg(
    total_revenue = ("sales","sum"),
    total_orders  = ("order_id","count"),
    avg_order_val = ("sales","mean"),
    first_order   = ("order_date","min"),
    last_order    = ("order_date","max"),
).reset_index()
clv["tenure_days"] = (clv["last_order"] - clv["first_order"]).dt.days
clv["clv_score"]   = clv["total_revenue"] * (clv["total_orders"] / clv["tenure_days"].clip(lower=1))
clv = clv.merge(rfm[["customer_id","Segment"]], on="customer_id", how="left")

# Save enriched customer data
clv.to_csv(os.path.join(DATA_DIR,"customers_enriched.csv"), index=False)
rfm.to_csv(os.path.join(DATA_DIR,"rfm_scores.csv"), index=False)

print("\n" + "="*60)
print("CUSTOMER ANALYTICS COMPLETE")
print("="*60)
print(f"RFM Segments identified : {rfm['Segment'].nunique()}")
print(f"Top segment by revenue  : {seg_summary.iloc[0]['Segment']}")
print(f"Avg customer LTV        : ₹{clv['total_revenue'].mean():,.0f}")
print(f"Top 10% customers drive : {clv.nlargest(int(len(clv)*0.1),'total_revenue')['total_revenue'].sum()/clv['total_revenue'].sum()*100:.0f}% of revenue")
print(f"\nFiles saved:")
print(f"  → data/customers_enriched.csv")
print(f"  → data/rfm_scores.csv")
