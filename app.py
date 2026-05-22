import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

# ── Config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Funnel Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ── Load data ─────────────────────────────────────────────
@st.cache_data
def load_data():
    funnel   = pd.read_csv(os.path.join(DATA_DIR, "funnel_summary.csv"))
    segments = pd.read_csv(os.path.join(DATA_DIR, "segment_summary.csv"))
    hourly   = pd.read_csv(os.path.join(DATA_DIR, "hourly_conversion.csv"))
    cohorts  = pd.read_csv(os.path.join(DATA_DIR, "cohort_data.csv"))
    ab_res   = pd.read_csv(os.path.join(DATA_DIR, "ab_test_results.csv"))
    ab_sum   = pd.read_csv(os.path.join(DATA_DIR, "ab_test_summary.csv"))
    dau      = pd.read_csv(os.path.join(DATA_DIR, "dau.csv"), parse_dates=["date"])
    items    = pd.read_csv(os.path.join(DATA_DIR, "item_stats.csv"))
    return funnel, segments, hourly, cohorts, ab_res, ab_sum, dau, items

funnel, segments, hourly, cohorts, ab_res, ab_sum, dau, items = load_data()

# ── Sidebar navigation ────────────────────────────────────
st.sidebar.title("📊 Funnel Analytics")
st.sidebar.markdown("Retailrocket · 2.5M events · 4.5 months")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Funnel Overview", "📉 Drop-off Analysis", "🔬 Segmentation", "🧪 A/B Test Results", "💡 Recommendations"],
)

st.sidebar.markdown("---")
st.sidebar.caption("Data: Retailrocket Dataset (Kaggle)")
st.sidebar.caption("Built with Python · Pandas · Streamlit · Plotly")


# ══════════════════════════════════════════════════════════
# PAGE 1 — FUNNEL OVERVIEW
# ══════════════════════════════════════════════════════════
if page == "🏠 Funnel Overview":
    st.title("🏠 Funnel Overview")
    st.markdown("End-to-end conversion from browse to purchase across **1.4M unique visitors**.")

    # KPI row
    viewers  = int(funnel.loc[funnel.stage == "view",        "unique_users"].values[0])
    carters  = int(funnel.loc[funnel.stage == "addtocart",   "unique_users"].values[0])
    buyers   = int(funnel.loc[funnel.stage == "transaction", "unique_users"].values[0])
    overall  = round(buyers / viewers * 100, 2)
    cart_ab  = round((carters - buyers) / carters * 100, 1)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Visitors",    f"{viewers:,}")
    c2.metric("Added to Cart",     f"{carters:,}",  f"{carters/viewers*100:.1f}% of visitors")
    c3.metric("Purchased",         f"{buyers:,}",   f"{buyers/viewers*100:.2f}% of visitors")
    c4.metric("Overall Conversion",f"{overall}%")
    c5.metric("Cart Abandonment",  f"{cart_ab}%")

    st.markdown("---")

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("Conversion Funnel")
        stages     = ["View", "Add to Cart", "Purchase"]
        values     = [viewers, carters, buyers]
        colors     = ["#4C9BE8", "#F5A623", "#2ECC71"]

        fig_funnel = go.Figure(go.Funnel(
            y           = stages,
            x           = values,
            textinfo    = "value+percent previous",
            marker      = dict(color=colors),
            connector   = dict(line=dict(color="#ccc", width=1)),
        ))
        fig_funnel.update_layout(
            margin      = dict(l=10, r=10, t=10, b=10),
            height      = 360,
            font        = dict(size=14),
        )
        st.plotly_chart(fig_funnel, use_container_width=True)

    with col_right:
        st.subheader("Drop-off Between Stages")
        drop_labels = ["View → Cart", "Cart → Purchase"]
        drop_vals   = [
            round((viewers - carters) / viewers * 100, 1),
            round((carters - buyers)  / carters * 100, 1),
        ]
        fig_drop = go.Figure(go.Bar(
            x             = drop_labels,
            y             = drop_vals,
            marker_color  = ["#E74C3C", "#C0392B"],
            text          = [f"{v}%" for v in drop_vals],
            textposition  = "outside",
        ))
        fig_drop.update_layout(
            yaxis=dict(title="Drop-off %", range=[0, 105]),
            margin=dict(l=10, r=10, t=10, b=10),
            height=360,
        )
        st.plotly_chart(fig_drop, use_container_width=True)

    st.markdown("---")
    st.subheader("Daily Active Users (DAU)")
    fig_dau = px.area(
        dau, x="date", y="dau",
        labels={"dau": "Daily Active Users", "date": ""},
        color_discrete_sequence=["#4C9BE8"],
    )
    fig_dau.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=260)
    st.plotly_chart(fig_dau, use_container_width=True)


# ══════════════════════════════════════════════════════════
# PAGE 2 — DROP-OFF ANALYSIS
# ══════════════════════════════════════════════════════════
elif page == "📉 Drop-off Analysis":
    st.title("📉 Drop-off Analysis")
    st.markdown("Where exactly are users leaving — and how bad is each stage?")

    viewers = int(funnel.loc[funnel.stage == "view",        "unique_users"].values[0])
    carters = int(funnel.loc[funnel.stage == "addtocart",   "unique_users"].values[0])
    buyers  = int(funnel.loc[funnel.stage == "transaction", "unique_users"].values[0])

    view_to_cart   = round((viewers - carters) / viewers * 100, 1)
    cart_to_buy    = round((carters - buyers)  / carters * 100, 1)

    st.markdown("### Stage-by-stage drop-off")
    c1, c2 = st.columns(2)
    c1.metric("View → Cart drop-off",     f"{view_to_cart}%",  "−" + f"{viewers - carters:,} users lost", delta_color="inverse")
    c2.metric("Cart → Purchase drop-off", f"{cart_to_buy}%",   "−" + f"{carters - buyers:,} users lost",  delta_color="inverse")

    st.markdown("---")
    st.markdown("### Hourly drop-off pattern")

    fig_hourly = go.Figure()
    fig_hourly.add_trace(go.Scatter(
        x=hourly["hour"], y=hourly["conv_rate_pct"],
        mode="lines+markers", name="Conversion rate %",
        line=dict(color="#2ECC71", width=2),
        marker=dict(size=6),
    ))
    fig_hourly.add_trace(go.Bar(
        x=hourly["hour"], y=hourly["visitors"] / hourly["visitors"].max() * hourly["conv_rate_pct"].max(),
        name="Visitor volume (scaled)", opacity=0.25,
        marker_color="#4C9BE8",
        yaxis="y",
    ))
    fig_hourly.update_layout(
        xaxis=dict(title="Hour of Day (UTC)", tickmode="linear", dtick=2),
        yaxis=dict(title="Conversion Rate %"),
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=10, r=10, t=30, b=10),
        height=360,
    )
    st.plotly_chart(fig_hourly, use_container_width=True)

    st.info("📌 **Peak conversion at 17:00 (0.852%)** — 2.6× higher than the worst hour (12:00 at 0.325%). "
            "Schedule promotions and push notifications for the 17:00–21:00 window.")

    st.markdown("---")
    st.markdown("### Top 10 most viewed vs most purchased items")

    top_viewed    = items.sort_values("view_count",    ascending=False).head(10)
    top_purchased = items.sort_values("purchase_count",ascending=False).head(10)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Most Viewed**")
        st.dataframe(top_viewed[["itemid","view_count","cart_count","purchase_count"]].reset_index(drop=True))
    with col2:
        st.markdown("**Most Purchased**")
        st.dataframe(top_purchased[["itemid","purchase_count","view_count","cart_count"]].reset_index(drop=True))


# ══════════════════════════════════════════════════════════
# PAGE 3 — SEGMENTATION
# ══════════════════════════════════════════════════════════
elif page == "🔬 Segmentation":
    st.title("🔬 Segmentation")
    st.markdown("Conversion rates broken down by time of day, day of week, and month.")

    seg_type = st.selectbox("Segment by", ["Hour of Day", "Day of Week", "Month"])

    seg_map = {"Hour of Day": "hour", "Day of Week": "day_of_week", "Month": "month"}
    seg_key = seg_map[seg_type]
    seg_df  = segments[segments["segment_type"] == seg_key].copy()

    fig_seg = go.Figure()
    fig_seg.add_trace(go.Bar(
        x             = seg_df["segment_label"],
        y             = seg_df["conv_rate_pct"],
        marker_color  = "#4C9BE8",
        text          = seg_df["conv_rate_pct"].apply(lambda x: f"{x:.3f}%"),
        textposition  = "outside",
        name          = "Conversion rate",
    ))
    fig_seg.update_layout(
        yaxis  = dict(title="Conversion Rate %"),
        xaxis  = dict(title=seg_type),
        margin = dict(l=10, r=10, t=20, b=10),
        height = 380,
    )
    st.plotly_chart(fig_seg, use_container_width=True)

    st.markdown("---")
    st.markdown("### Cart abandonment by segment")
    fig_ab = go.Figure(go.Bar(
        x            = seg_df["segment_label"],
        y            = seg_df["cart_abandonment_pct"],
        marker_color = "#E74C3C",
        text         = seg_df["cart_abandonment_pct"].apply(lambda x: f"{x}%"),
        textposition = "outside",
    ))
    fig_ab.update_layout(
        yaxis  = dict(title="Cart Abandonment %", range=[0, 100]),
        xaxis  = dict(title=seg_type),
        margin = dict(l=10, r=10, t=20, b=10),
        height = 340,
    )
    st.plotly_chart(fig_ab, use_container_width=True)

    st.markdown("---")
    st.markdown("### Full segment table")
    st.dataframe(
        seg_df[["segment_label","visitors","carters","buyers","conv_rate_pct","cart_abandonment_pct"]]
        .rename(columns={
            "segment_label"       : seg_type,
            "conv_rate_pct"       : "Conv %",
            "cart_abandonment_pct": "Abandonment %",
        })
        .reset_index(drop=True),
        use_container_width=True,
    )

    st.markdown("---")
    st.markdown("### Weekly cohort retention")
    cohort_pivot = cohorts.pivot(index="cohort_week", columns="activity_week", values="active_users").fillna(0)
    # Normalize to retention %
    cohort_pct = cohort_pivot.div(cohort_pivot.iloc[:, 0], axis=0).mul(100).round(1)
    fig_cohort = px.imshow(
        cohort_pct,
        color_continuous_scale="Blues",
        labels=dict(x="Activity Week", y="Cohort Week", color="Retention %"),
        aspect="auto",
    )
    fig_cohort.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=420)
    st.plotly_chart(fig_cohort, use_container_width=True)
    st.caption("Each row is a cohort (first week of visit). Each column is a subsequent week. Color = % of cohort still active.")


# ══════════════════════════════════════════════════════════
# PAGE 4 — A/B TEST RESULTS
# ══════════════════════════════════════════════════════════
elif page == "🧪 A/B Test Results":
    st.title("🧪 A/B Test Results")
    st.markdown("**Experiment:** New checkout flow (guest checkout + progress bar) vs. existing flow.")
    st.markdown("**Population:** Visitors who added to cart — did they complete purchase?")

    control   = ab_res[ab_res["group"] == "Control"].iloc[0]
    treatment = ab_res[ab_res["group"] == "Treatment"].iloc[0]
    summary   = ab_sum.iloc[0]

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Control Conversion",   f"{control['conv_rate_pct']:.2f}%")
    c2.metric("Treatment Conversion", f"{treatment['conv_rate_pct']:.2f}%",
              f"+{summary['relative_uplift_pct']:.1f}% relative uplift")
    c3.metric("P-value",  f"{summary['p_value']:.6f}")
    c4.metric("Z-statistic", f"{summary['z_statistic']:.2f}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Conversion Rate: Control vs Treatment")
        fig_ab = go.Figure(go.Bar(
            x             = ["Control", "Treatment"],
            y             = [control["conv_rate_pct"], treatment["conv_rate_pct"]],
            marker_color  = ["#95A5A6", "#2ECC71"],
            text          = [f"{control['conv_rate_pct']:.2f}%", f"{treatment['conv_rate_pct']:.2f}%"],
            textposition  = "outside",
        ))
        fig_ab.update_layout(
            yaxis  = dict(title="Conversion Rate %", range=[0, treatment["conv_rate_pct"] * 1.25]),
            margin = dict(l=10, r=10, t=10, b=10),
            height = 340,
        )
        st.plotly_chart(fig_ab, use_container_width=True)

    with col2:
        st.subheader("95% Confidence Interval")
        diff    = treatment["conv_rate_pct"] - control["conv_rate_pct"]
        ci_low  = summary["ci_lower_pct"]
        ci_high = summary["ci_upper_pct"]

        fig_ci = go.Figure()
        fig_ci.add_trace(go.Scatter(
            x    = [ci_low, ci_high],
            y    = [1, 1],
            mode = "lines",
            line = dict(color="#2ECC71", width=4),
            name = "95% CI",
        ))
        fig_ci.add_trace(go.Scatter(
            x      = [diff],
            y      = [1],
            mode   = "markers",
            marker = dict(color="#E74C3C", size=14, symbol="diamond"),
            name   = "Observed difference",
        ))
        fig_ci.add_vline(x=0, line_dash="dash", line_color="gray", annotation_text="No effect")
        fig_ci.update_layout(
            xaxis  = dict(title="Difference in conversion rate (pp)"),
            yaxis  = dict(visible=False),
            margin = dict(l=10, r=10, t=10, b=40),
            height = 340,
            showlegend=True,
        )
        st.plotly_chart(fig_ci, use_container_width=True)

    st.markdown("---")
    verdict = summary["verdict"]
    if verdict == "Roll out":
        st.success(f"✅ **Statistically significant (p < 0.05).** The new checkout flow produces a "
                   f"**{summary['relative_uplift_pct']:.1f}% relative uplift**. "
                   f"95% CI: [{ci_low:.2f}pp, {ci_high:.2f}pp]. Safe to roll out to 100% of users.")
    else:
        st.warning("⚠️ Result is not statistically significant. Collect more data before deciding.")

    st.markdown("---")
    st.subheader("Raw Results")
    st.dataframe(ab_res, use_container_width=True)


# ══════════════════════════════════════════════════════════
# PAGE 5 — RECOMMENDATIONS
# ══════════════════════════════════════════════════════════
elif page == "💡 Recommendations":
    st.title("💡 Recommendations")
    st.markdown("Data-driven actions ranked by estimated impact.")

    viewers = int(funnel.loc[funnel.stage == "view",        "unique_users"].values[0])
    carters = int(funnel.loc[funnel.stage == "addtocart",   "unique_users"].values[0])
    buyers  = int(funnel.loc[funnel.stage == "transaction", "unique_users"].values[0])

    recos = [
        {
            "priority": "🔴 Critical",
            "title"   : "Fix Browse → Cart (97.4% drop-off)",
            "insight" : f"Only {carters/viewers*100:.1f}% of {viewers:,} visitors add anything to cart. "
                        "This is the largest loss in the funnel — dwarfs every other problem.",
            "action"  : "A/B test: add persistent 'Add to Cart' CTAs on product pages, "
                        "show social proof (reviews, ratings), and surface trending items on the homepage.",
            "metric"  : "Target: lift view→cart rate from 2.6% to 4%+",
        },
        {
            "priority": "🔴 Critical",
            "title"   : "Introduce Guest Checkout",
            "insight" : f"69.6% of cart users ({carters - buyers:,} people) abandon before purchase. "
                        "Forced account creation is the #1 industry cause of checkout abandonment.",
            "action"  : "Add a 'Continue as Guest' option at checkout entry. A/B test showed "
                        "a simulated +13.8% uplift from checkout improvements.",
            "metric"  : "Target: reduce cart abandonment from 69.6% to under 60%",
        },
        {
            "priority": "🟠 High",
            "title"   : "Target Evening Hours (17:00–21:00)",
            "insight" : "Conversion at 17:00 (0.852%) is 2.6× higher than 12:00 (0.325%). "
                        "Visitor volume is also highest in this window.",
            "action"  : "Schedule push notifications, email campaigns, and paid ad spend "
                        "to peak in the 17:00–21:00 UTC window.",
            "metric"  : "Target: shift 20% of daily ad budget to evening hours",
        },
        {
            "priority": "🟠 High",
            "title"   : "Cart Abandonment Re-engagement",
            "insight" : f"{carters - buyers:,} users added to cart but never purchased. "
                        "These are your highest-intent users — they just need a nudge.",
            "action"  : "Trigger automated cart reminder email/push after 30 minutes of inactivity. "
                        "Include product image, price, and a discount if still unpurchased after 24h.",
            "metric"  : "Industry benchmark: cart reminders recover 5–15% of abandoned carts",
        },
        {
            "priority": "🟡 Medium",
            "title"   : "Investigate Item 187946",
            "insight" : "Most-viewed item (3,409 views) but does not appear in top purchases. "
                        "High interest, low conversion — a product page problem.",
            "action"  : "Review the product page: check price competitiveness, image quality, "
                        "review count, and availability. A/B test the product description.",
            "metric"  : "Target: bring item 187946 into top 20 purchased items",
        },
        {
            "priority": "🟡 Medium",
            "title"   : "Improve Weekend Retention",
            "insight" : "Saturday conversion (0.524%) is 38% lower than Wednesday (0.845%). "
                        "Weekend visitors are less likely to buy.",
            "action"  : "Test weekend-specific promotions: flash sales, free shipping thresholds, "
                        "or curated weekend collections to improve weekend intent.",
            "metric"  : "Target: close weekend conversion gap by 50%",
        },
    ]

    for r in recos:
        with st.expander(f"{r['priority']} — {r['title']}", expanded=True):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**📊 Insight:** {r['insight']}")
                st.markdown(f"**🛠 Action:** {r['action']}")
            with col2:
                st.info(f"🎯 {r['metric']}")
