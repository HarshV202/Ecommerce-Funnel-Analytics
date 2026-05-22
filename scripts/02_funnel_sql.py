import pandas as pd
import sqlite3
import os

INPUT  = r"C:\Users\Harsh\Desktop\Analytics Project\cleaned_events.csv"
OUTDIR = r"C:\Users\Harsh\Desktop\Analytics Project"
DB     = r"C:\Users\Harsh\Desktop\Analytics Project\events.db"

os.makedirs(OUTDIR, exist_ok=True)

print("=" * 55)
print("STEP 2 — SQL FUNNEL ANALYSIS")
print("=" * 55)

# ── Load CSV → SQLite ─────────────────────────────────────
print("\n[1/6] Loading cleaned_events.csv into SQLite …")
df = pd.read_csv(INPUT)
conn = sqlite3.connect(DB)
df.to_sql("events", conn, if_exists="replace", index=False)
print(f"      Rows in DB  : {len(df):,}")
print(f"      DB saved to : {DB}")

# ── Q1. Unique users at each funnel stage ─────────────────
print("\n[2/6] Q1 — Unique users at each funnel stage …")
q1 = """
SELECT
    event,
    COUNT(DISTINCT visitorid) AS unique_users
FROM events
GROUP BY event
ORDER BY unique_users DESC;
"""
funnel_raw = pd.read_sql(q1, conn)
print(funnel_raw.to_string(index=False))

# ── Q2. Stage-to-stage conversion rates ───────────────────
print("\n[3/6] Q2 — Stage-to-stage conversion rates …")
q2 = """
WITH stage_counts AS (
    SELECT event, COUNT(DISTINCT visitorid) AS users
    FROM events
    GROUP BY event
),
totals AS (
    SELECT users AS total_visitors
    FROM stage_counts WHERE event = 'view'
)
SELECT
    s.event,
    s.users,
    ROUND(100.0 * s.users / t.total_visitors, 2) AS pct_of_visitors
FROM stage_counts s, totals t
ORDER BY s.users DESC;
"""
conv_table = pd.read_sql(q2, conn)
print(conv_table.to_string(index=False))

# Stage-to-stage drop-off
viewers   = conv_table.loc[conv_table.event=='view',       'users'].values[0]
carters   = conv_table.loc[conv_table.event=='addtocart',  'users'].values[0]
buyers    = conv_table.loc[conv_table.event=='transaction','users'].values[0]
print(f"\n      View → Cart      : {carters/viewers*100:.1f}% converted  ({100-carters/viewers*100:.1f}% dropped)")
print(f"      Cart → Purchase  : {buyers/carters*100:.1f}% converted  ({100-buyers/carters*100:.1f}% dropped)")
print(f"      View → Purchase  : {buyers/viewers*100:.2f}% overall conversion")

# ── Q3. Cart abandonment rate ─────────────────────────────
print("\n[4/6] Q3 — Cart abandonment rate …")
q3 = """
WITH cart_users AS (
    SELECT COUNT(DISTINCT visitorid) AS carters
    FROM events WHERE event = 'addtocart'
),
buyers AS (
    SELECT COUNT(DISTINCT visitorid) AS purchasers
    FROM events WHERE event = 'transaction'
)
SELECT
    carters,
    purchasers,
    ROUND(100.0 * (carters - purchasers) / carters, 1) AS cart_abandonment_pct
FROM cart_users, buyers;
"""
abandon = pd.read_sql(q3, conn)
print(abandon.to_string(index=False))

# ── Q4. Window function — first & last event per visitor ──
print("\n[5/6] Q4 — User journey with window functions (sample 10 buyers) …")
q4 = """
WITH ranked AS (
    SELECT
        visitorid,
        event,
        datetime,
        ROW_NUMBER() OVER (PARTITION BY visitorid ORDER BY timestamp ASC)  AS rn_first,
        ROW_NUMBER() OVER (PARTITION BY visitorid ORDER BY timestamp DESC) AS rn_last
    FROM events
),
first_events AS (
    SELECT visitorid, event AS first_event, datetime AS first_seen
    FROM ranked WHERE rn_first = 1
),
last_events AS (
    SELECT visitorid, event AS last_event, datetime AS last_seen
    FROM ranked WHERE rn_last = 1
)
SELECT
    f.visitorid,
    f.first_event,
    f.first_seen,
    l.last_event,
    l.last_seen
FROM first_events f
JOIN last_events l ON f.visitorid = l.visitorid
WHERE l.last_event = 'transaction'
LIMIT 10;
"""
journeys = pd.read_sql(q4, conn)
print(journeys.to_string(index=False))

# ── Q5. Weekly cohort retention ───────────────────────────
print("\n[6/6] Q5 — Weekly cohort retention …")
q5 = """
WITH first_seen AS (
    SELECT
        visitorid,
        MIN(date) AS cohort_date
    FROM events
    GROUP BY visitorid
),
cohorts AS (
    SELECT
        strftime('%Y-W%W', fs.cohort_date)           AS cohort_week,
        strftime('%Y-W%W', e.date)                   AS activity_week,
        COUNT(DISTINCT e.visitorid)                  AS active_users
    FROM events e
    JOIN first_seen fs ON e.visitorid = fs.visitorid
    GROUP BY 1, 2
)
SELECT *
FROM cohorts
ORDER BY cohort_week, activity_week
LIMIT 30;
"""
cohorts = pd.read_sql(q5, conn)
print(cohorts.to_string(index=False))
cohorts.to_csv(os.path.join(OUTDIR, "cohort_data.csv"), index=False)

# ── Save funnel summary ───────────────────────────────────
funnel_summary = pd.DataFrame({
    "stage"        : ["view", "addtocart", "transaction"],
    "unique_users" : [viewers, carters, buyers],
    "pct_of_viewers": [100.0, round(carters/viewers*100,2), round(buyers/viewers*100,2)],
    "drop_off_pct" : [0, round(100-carters/viewers*100,1), round(100-buyers/carters*100,1)]
})
funnel_summary.to_csv(os.path.join(OUTDIR, "funnel_summary.csv"), index=False)

conn.close()
print(f"\n✅  Step 2 complete.")
print(f"    funnel_summary.csv → {OUTDIR}")
print(f"    cohort_data.csv    → {OUTDIR}")
print(f"    events.db          → {DB}\n")