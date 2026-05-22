# E-Commerce Funnel Analytics

End-to-end funnel analysis on **2.75M real user events** from the Retailrocket dataset. Covers data cleaning, SQL funnel queries, cohort retention, A/B testing, and a live interactive dashboard.

🔗 **[Live Dashboard →](https://ecommerce-funnel-analytics.streamlit.app/)**

---

## What This Project Does

Most e-commerce analytics projects stop at "here's a chart." This one goes further:

- Cleans raw event data and removes bot traffic (1,351 bots, 219K rows eliminated)
- Runs SQL funnel queries with window functions to trace user journeys
- Segments conversion by hour, day of week, and month to find actionable patterns
- Simulates an A/B test with a two-proportion z-test and confidence intervals
- Serves all findings in a 5-page Streamlit dashboard with Plotly visualisations

---

## Key Findings

| Metric | Value |
|---|---|
| Total visitors | 1,402,830 |
| Overall conversion rate | 0.80% |
| View → Cart drop-off | 97.4% |
| Cart abandonment | 69.6% |
| Best converting hour | 17:00 (0.852%) |
| Best converting day | Wednesday (0.845%) |
| A/B test uplift (new checkout) | +13.8% relative, p < 0.001 |

**Biggest insight:** The critical drop is at browse → cart (97.4%), not at checkout. Most analytics focus on cart abandonment — but the real problem is that users never add anything in the first place.

---

## Dashboard Pages

| Page | Description |
|---|---|
| 🏠 Funnel Overview | KPI cards, funnel chart, drop-off bars, DAU trend |
| 📉 Drop-off Analysis | Hourly conversion curve, top items by views vs purchases |
| 🔬 Segmentation | Conversion by hour/day/month, cohort retention heatmap |
| 🧪 A/B Test Results | Control vs treatment, CI plot, statistical verdict |
| 💡 Recommendations | 6 prioritised actions with targets and business rationale |

---

## Project Structure

```
ecommerce-funnel-analytics/
├── app.py                        # Streamlit dashboard (5 pages)
├── requirements.txt
├── scripts/
│   ├── 01_load_and_clean.py      # Data loading, deduplication, bot removal
│   ├── 02_funnel_sql.py          # SQL funnel queries, cohort retention
│   ├── 03_segmentation.py        # Drop-off by hour, day, month, top items
│   └── 04_ab_test.py             # Two-proportion z-test simulation
└── data/
    ├── funnel_summary.csv
    ├── segment_summary.csv
    ├── hourly_conversion.csv
    ├── cohort_data.csv
    ├── dau.csv
    ├── item_stats.csv
    ├── ab_test_results.csv
    └── ab_test_summary.csv
```

---

## How to Run Locally

```bash
git clone https://github.com/HarshV202/ecommerce-funnel-analytics.git
cd ecommerce-funnel-analytics
pip install -r requirements.txt
streamlit run app.py
```

To regenerate the data from scratch, download the [Retailrocket dataset from Kaggle](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset) and run the four scripts in order.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python + Pandas | Data loading, cleaning, feature engineering |
| SQLite + SQL | Funnel queries, window functions, cohort analysis |
| SciPy | Two-proportion z-test for A/B testing |
| Streamlit | Interactive multi-page dashboard |
| Plotly | Funnel charts, bar charts, heatmaps, CI plots |

---

## Dataset

**Retailrocket E-Commerce Dataset** — [Kaggle](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset)

- 2,756,101 raw events across 4.5 months (May–Sep 2015)
- 1.4M unique anonymised visitors
- Three event types: `view`, `addtocart`, `transaction`
- Raw data not included in this repo (too large — run the scripts to regenerate)
