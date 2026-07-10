# =============================================================================
# BUSINESS INTELLIGENCE & SALES ANALYTICS PLATFORM
# Notebook 03 — Sales Forecasting (Holt-Winters + Trend Decomposition)
# =============================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose
import joblib, os, warnings
warnings.filterwarnings("ignore")

ROOT     = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(ROOT, "data")
RPT_DIR  = os.path.join(ROOT, "reports")
MDL_DIR  = os.path.join(ROOT, "models")
os.makedirs(RPT_DIR, exist_ok=True)
os.makedirs(MDL_DIR, exist_ok=True)

PALETTE = {"primary":"#2563eb","success":"#10b981","danger":"#ef4444","warn":"#f59e0b"}

# ── Load & prepare monthly series ─────────────────────────────────────────────
df = pd.read_csv(os.path.join(DATA_DIR,"superstore.csv"), parse_dates=["order_date"])
monthly = df.groupby(df["order_date"].dt.to_period("M")).agg(
    Revenue=("sales","sum"),
    Orders=("order_id","count"),
    Profit=("profit","sum")
).reset_index()
monthly["order_date"] = monthly["order_date"].dt.to_timestamp()
monthly = monthly.sort_values("order_date").reset_index(drop=True)

print("="*60)
print("SALES FORECASTING")
print("="*60)
print(f"Monthly data points : {len(monthly)}")
print(f"Date range          : {monthly['order_date'].min().date()} → {monthly['order_date'].max().date()}")

# ── Train/test split (last 3 months = test) ───────────────────────────────────
train = monthly.iloc[:-3]
test  = monthly.iloc[-3:]
ts_train = train.set_index("order_date")["Revenue"]

# ── Holt-Winters Model ────────────────────────────────────────────────────────
model = ExponentialSmoothing(
    ts_train,
    trend="add",
    seasonal="add",
    seasonal_periods=12
).fit(optimized=True)

forecast_test    = model.forecast(3)
forecast_future  = model.forecast(6)  # 6 months ahead

# Metrics
actual = test["Revenue"].values
preds  = forecast_test.values
mape   = np.mean(np.abs((actual - preds) / actual)) * 100
mae    = np.mean(np.abs(actual - preds))

print(f"\nHolt-Winters Model Performance:")
print(f"  MAPE : {mape:.1f}%")
print(f"  MAE  : ₹{mae:,.0f}")
print(f"  Accuracy : {100-mape:.1f}%")

# ── Plot 1: Forecast ──────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(monthly["order_date"], monthly["Revenue"]/1e6,
        "o-", color=PALETTE["primary"], label="Actual", linewidth=2, markersize=4)
ax.plot(test["order_date"], forecast_test.values/1e6,
        "s--", color=PALETTE["danger"], label="Forecast (test)", linewidth=2, markersize=6)

# Future forecast dates
last_date = monthly["order_date"].max()
future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=6, freq="MS")
ax.plot(future_dates, forecast_future.values/1e6,
        "^--", color=PALETTE["warn"], label="Forecast (next 6 months)", linewidth=2, markersize=6)

# Confidence interval (simple ±10%)
ax.fill_between(future_dates,
                forecast_future.values/1e6 * 0.90,
                forecast_future.values/1e6 * 1.10,
                alpha=0.15, color=PALETTE["warn"], label="90% Confidence Interval")

ax.axvline(x=test["order_date"].iloc[0], color="gray", linestyle=":", alpha=0.7)
ax.set_title(f"Monthly Revenue Forecast — Holt-Winters\nMAPE: {mape:.1f}% | Accuracy: {100-mape:.1f}%",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Month"); ax.set_ylabel("Revenue (₹M)")
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(RPT_DIR,"11_revenue_forecast.png"), dpi=150, bbox_inches="tight")
plt.show()
print("✅ Plot 11: Revenue Forecast saved")

# ── Plot 2: Decomposition ─────────────────────────────────────────────────────
decomp = seasonal_decompose(ts_train, model="additive", period=12, extrapolate_trend="freq")
fig, axes = plt.subplots(4, 1, figsize=(14, 10))
fig.suptitle("Time Series Decomposition — Revenue", fontsize=13, fontweight="bold")

axes[0].plot(decomp.observed/1e6,  color=PALETTE["primary"]);  axes[0].set_ylabel("Observed (₹M)")
axes[1].plot(decomp.trend/1e6,     color=PALETTE["success"]);  axes[1].set_ylabel("Trend (₹M)")
axes[2].plot(decomp.seasonal/1e3,  color=PALETTE["warn"]);     axes[2].set_ylabel("Seasonal (₹K)")
axes[3].plot(decomp.resid/1e3,     color=PALETTE["danger"]);   axes[3].set_ylabel("Residual (₹K)")
axes[3].axhline(y=0, color="black", linewidth=0.8)
for ax in axes: ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(RPT_DIR,"12_decomposition.png"), dpi=150, bbox_inches="tight")
plt.show()
print("✅ Plot 12: Decomposition saved")

# ── Save forecast + model ─────────────────────────────────────────────────────
forecast_df = pd.DataFrame({
    "month":           future_dates,
    "forecast_revenue":forecast_future.values.round(0),
    "lower_bound":     (forecast_future.values * 0.90).round(0),
    "upper_bound":     (forecast_future.values * 1.10).round(0),
})
forecast_df.to_csv(os.path.join(DATA_DIR,"revenue_forecast.csv"), index=False)
joblib.dump(model, os.path.join(MDL_DIR,"holt_winters_model.pkl"))

print("\n" + "="*60)
print("FORECASTING COMPLETE")
print("="*60)
print(f"Model accuracy   : {100-mape:.1f}%")
print(f"\n6-Month Revenue Forecast:")
for _, row in forecast_df.iterrows():
    print(f"  {row['month'].strftime('%b %Y')} : ₹{row['forecast_revenue']:>10,.0f}  "
          f"(₹{row['lower_bound']:,.0f} – ₹{row['upper_bound']:,.0f})")
print(f"\nFiles saved:")
print(f"  → data/revenue_forecast.csv")
print(f"  → models/holt_winters_model.pkl")
