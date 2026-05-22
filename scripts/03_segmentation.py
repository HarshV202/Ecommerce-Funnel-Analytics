import pandas as pd
import os

INPUT  = r"C:\Users\Harsh\Desktop\Analytics Project\cleaned_events.csv"
OUTDIR = r"C:\Users\Harsh\Desktop\Analytics Project"

print("=" * 55)
print("STEP 3 — DROP-OFF & SEGMENTATION ANALYSIS")
print("=" * 55)

# ── Load ──────────────────────────────────────────────────
print("\n[1/7] Loading cleaned_events.csv …")
df = pd.read_csv(INPUT, parse_dates=["datetime"])
print(f"      Rows: {len(df):,}")

# ── Helper ────────────────────────────────────────────────
def funnel_metrics(slice_df):
    """Return conversion metrics for any subset of the data."""
    visitors = slice_df["visitorid"].nunique()
    buyers   = slice_df[slice_df["event"] == "transaction"]["visitorid"].nunique()
    carters  = slice_df[slice_df["event"] == "addtocart"]["visitorid"].nunique()
    cart_ab  = round((carters - buyers) / carters * 100, 1) if carters > 0 else 0
    conv     = round(buyers / visitors * 100, 3) if visitors > 0 else 0
    return {
        "visitors"            : visitors,
        "carters"             : carters,
        "buyers"              : buyers,
        "conv_rate_pct"       : conv,
        "cart_abandonment_pct": cart_ab,
    }

# ── 1. Hourly conversion ──────────────────────────────────
print("\n[2/7] Hourly conversion …")
hourly_rows = []
for hour in range(24):
    metrics = funnel_metrics(df[df["hour"] == hour])
    metrics["hour"] = hour
    hourly_rows.append(metrics)

hourly = pd.DataFrame(hourly_rows)[
    ["hour", "visitors", "carters", "buyers", "conv_rate_pct", "cart_abandonment_pct"]
]
print(hourly.to_string(index=False))
hourly.to_csv(os.path.join(OUTDIR, "hourly_conversion.csv"), index=False)

best_hour  = hourly.loc[hourly["conv_rate_pct"].idxmax(), "hour"]
worst_hour = hourly.loc[hourly["conv_rate_pct"].idxmin(), "hour"]
print(f"\n      Best converting hour : {best_hour}:00  ({hourly['conv_rate_pct'].max()}%)")
print(f"      Worst converting hour: {worst_hour}:00  ({hourly['conv_rate_pct'].min()}%)")

# ── 2. Day-of-week conversion ─────────────────────────────
print("\n[3/7] Day-of-week conversion …")
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day_rows  = []
for day in day_order:
    metrics = funnel_metrics(df[df["day_of_week"] == day])
    metrics["day_of_week"] = day
    day_rows.append(metrics)

days = pd.DataFrame(day_rows)[
    ["day_of_week", "visitors", "carters", "buyers", "conv_rate_pct", "cart_abandonment_pct"]
]
print(days.to_string(index=False))

best_day  = days.loc[days["conv_rate_pct"].idxmax(), "day_of_week"]
worst_day = days.loc[days["conv_rate_pct"].idxmin(), "day_of_week"]
print(f"\n      Best day  : {best_day}  ({days['conv_rate_pct'].max()}%)")
print(f"      Worst day : {worst_day}  ({days['conv_rate_pct'].min()}%)")

# ── 3. Monthly conversion ─────────────────────────────────
print("\n[4/7] Monthly conversion …")
month_names = {5: "May", 6: "Jun", 7: "Jul", 8: "Aug", 9: "Sep"}
month_rows  = []
for month in sorted(df["month"].unique()):
    metrics = funnel_metrics(df[df["month"] == month])
    metrics["month"]      = month
    metrics["month_name"] = month_names.get(month, str(month))
    month_rows.append(metrics)

months = pd.DataFrame(month_rows)[
    ["month", "month_name", "visitors", "carters", "buyers", "conv_rate_pct", "cart_abandonment_pct"]
]
print(months.to_string(index=False))

# ── 4. Top products ───────────────────────────────────────
print("\n[5/7] Top products by views, carts, and purchases …")
views_df = df[df["event"] == "view"]
cart_df  = df[df["event"] == "addtocart"]
txn_df   = df[df["event"] == "transaction"]

top_viewed    = views_df["itemid"].value_counts().head(10).reset_index()
top_viewed.columns = ["itemid", "view_count"]

top_carted    = cart_df["itemid"].value_counts().head(10).reset_index()
top_carted.columns = ["itemid", "cart_count"]

top_purchased = txn_df["itemid"].value_counts().head(10).reset_index()
top_purchased.columns = ["itemid", "purchase_count"]

item_stats = (
    top_viewed
    .merge(top_carted,    on="itemid", how="outer")
    .merge(top_purchased, on="itemid", how="outer")
    .fillna(0)
    .astype({"view_count": int, "cart_count": int, "purchase_count": int})
    .sort_values("view_count", ascending=False)
)
print("\n      Top 10 most viewed items:")
print(top_viewed.to_string(index=False))
print("\n      Top 10 most purchased items:")
print(top_purchased.to_string(index=False))
item_stats.to_csv(os.path.join(OUTDIR, "item_stats.csv"), index=False)

# ── 5. DAU ────────────────────────────────────────────────
print("\n[6/7] Daily Active Users (DAU) …")
dau = df.groupby("date")["visitorid"].nunique().reset_index()
dau.columns = ["date", "dau"]
print(f"      Average DAU : {dau['dau'].mean():.0f}")
print(f"      Peak DAU    : {dau['dau'].max():,}  on {dau.loc[dau['dau'].idxmax(), 'date']}")
print(f"      Min DAU     : {dau['dau'].min():,}  on {dau.loc[dau['dau'].idxmin(), 'date']}")
dau.to_csv(os.path.join(OUTDIR, "dau.csv"), index=False)

# ── 6. Items per session ──────────────────────────────────
print("\n[7/7] Items per session …")
session_items = (
    df[df["event"] == "view"]
    .groupby(["visitorid", "date"])["itemid"]
    .nunique()
    .reset_index()
)
session_items.columns = ["visitorid", "date", "items_viewed"]
avg_items = session_items["items_viewed"].mean()
print(f"      Avg items viewed per session : {avg_items:.2f}")

# ── Build segment_summary ─────────────────────────────────
hourly["segment_type"]  = "hour"
hourly["segment_label"] = hourly["hour"].astype(str) + ":00"
days["segment_type"]    = "day_of_week"
days["segment_label"]   = days["day_of_week"]
months["segment_type"]  = "month"
months["segment_label"] = months["month_name"]

segment_summary = pd.concat([
    hourly[["segment_type", "segment_label", "visitors", "carters", "buyers", "conv_rate_pct", "cart_abandonment_pct"]],
    days[["segment_type", "segment_label", "visitors", "carters", "buyers", "conv_rate_pct", "cart_abandonment_pct"]],
    months[["segment_type", "segment_label", "visitors", "carters", "buyers", "conv_rate_pct", "cart_abandonment_pct"]],
], ignore_index=True)

segment_summary.to_csv(os.path.join(OUTDIR, "segment_summary.csv"), index=False)

print(f"\n✅  Step 3 complete. Files saved to: {OUTDIR}")
print("    - segment_summary.csv")
print("    - hourly_conversion.csv")
print("    - item_stats.csv")
print("    - dau.csv\n")