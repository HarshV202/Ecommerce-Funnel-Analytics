
import pandas as pd
import os

# ── CHANGE THESE TWO PATHS ────────────────────────────────
INPUT  = r"C:\Users\Harsh\Desktop\Analytics Project\events.csv"
OUTPUT = r"C:\Users\Harsh\Desktop\Analytics Project\cleaned_events.csv"
# ─────────────────────────────────────────────────────────

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

print("=" * 55)
print("STEP 1 — LOAD & CLEAN")
print("=" * 55)

# ── 1. Load ───────────────────────────────────────────────
print("\n[1/7] Loading events.csv …")
df = pd.read_csv(INPUT)
print(f"      Rows loaded : {len(df):,}")
print(f"      Columns     : {list(df.columns)}")

# ── 2. Basic inspection ───────────────────────────────────
print("\n[2/7] Null check …")
print(df.isnull().sum().to_string())

# ── 3. Parse timestamp ────────────────────────────────────
print("\n[3/7] Converting Unix ms → datetime (UTC) …")
df["datetime"]    = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
df["date"]        = df["datetime"].dt.date
df["hour"]        = df["datetime"].dt.hour
df["day_of_week"] = df["datetime"].dt.day_name()
df["week"]        = df["datetime"].dt.isocalendar().week.astype(int)
df["month"]       = df["datetime"].dt.month
print(f"      Date range  : {df['datetime'].min().date()} → {df['datetime'].max().date()}")

# ── 4. Remove exact duplicates ────────────────────────────
print("\n[4/7] Removing exact duplicate rows …")
before = len(df)
df.drop_duplicates(inplace=True)
print(f"      Dropped     : {before - len(df):,} duplicates")
print(f"      Remaining   : {len(df):,}")

# ── 5. Bot removal (top 0.1% by event count) ─────────────
print("\n[5/7] Removing bot-like visitors (top 0.1% by event count) …")
event_counts = df.groupby("visitorid").size()
threshold    = event_counts.quantile(0.999)
bots         = event_counts[event_counts > threshold].index
before       = len(df)
df           = df[~df["visitorid"].isin(bots)]
print(f"      Threshold   : {threshold:.0f} events/visitor")
print(f"      Bots found  : {len(bots):,} visitors")
print(f"      Rows dropped: {before - len(df):,}")
print(f"      Remaining   : {len(df):,}")

# ── 6. Feature engineering ────────────────────────────────
print("\n[6/7] Engineering features …")

purchasers     = df[df["event"] == "transaction"]["visitorid"].unique()
df["is_purchaser"] = df["visitorid"].isin(purchasers).astype(int)

stage_map  = {"view": 1, "addtocart": 2, "transaction": 3}
df["stage"] = df["event"].map(stage_map)

event_counts_clean = df["event"].value_counts()
print(f"\n      Event breakdown after cleaning:")
for evt, cnt in event_counts_clean.items():
    print(f"        {evt:<15}: {cnt:>10,}")

total_visitors = df["visitorid"].nunique()
cart_visitors  = df[df["event"] == "addtocart"]["visitorid"].nunique()
buyer_visitors = df[df["event"] == "transaction"]["visitorid"].nunique()
overall_conv   = buyer_visitors / total_visitors * 100
cart_abandon   = (cart_visitors - buyer_visitors) / cart_visitors * 100

print(f"\n      Unique visitors : {total_visitors:,}")
print(f"      Added to cart   : {cart_visitors:,}")
print(f"      Purchased       : {buyer_visitors:,}")
print(f"      Overall conv.   : {overall_conv:.2f}%")
print(f"      Cart abandonment: {cart_abandon:.1f}%")

# ── 7. Save ───────────────────────────────────────────────
print("\n[7/7] Saving cleaned_events.csv …")
df.to_csv(OUTPUT, index=False)
size_mb = os.path.getsize(OUTPUT) / 1e6
print(f"      Saved to    : {OUTPUT}")
print(f"      File size   : {size_mb:.1f} MB")
print(f"      Final rows  : {len(df):,}")
print(f"      Columns     : {list(df.columns)}")

print("\n✅  Step 1 complete. cleaned_events.csv is ready for Step 2.\n")