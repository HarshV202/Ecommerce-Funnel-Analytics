import pandas as pd
import numpy as np
from scipy import stats
import os

INPUT  = r"C:\Users\Harsh\Desktop\Analytics Project\cleaned_events.csv"
OUTDIR = r"C:\Users\Harsh\Desktop\Analytics Project"

np.random.seed(42)

print("=" * 55)
print("STEP 4 — A/B TEST SIMULATION")
print("=" * 55)

# ── Load visitors who reached cart stage ──────────────────
# The experiment targets users who added to cart — did they purchase?
print("\n[1/5] Loading cart-stage visitors …")
df = pd.read_csv(INPUT)

cart_visitors = df[df["event"] == "addtocart"]["visitorid"].unique()
print(f"      Cart visitors (experiment pool): {len(cart_visitors):,}")

# ── Assign groups deterministically via hash ──────────────
print("\n[2/5] Assigning Control / Treatment groups …")
# Using modulo on visitorid — deterministic, no randomness needed
control_ids   = [v for v in cart_visitors if int(v) % 2 == 0]
treatment_ids = [v for v in cart_visitors if int(v) % 2 == 1]
print(f"      Control   : {len(control_ids):,} visitors")
print(f"      Treatment : {len(treatment_ids):,} visitors")

# ── Measure baseline conversion (who actually purchased) ──
print("\n[3/5] Measuring baseline conversion rates …")
buyers = set(df[df["event"] == "transaction"]["visitorid"].unique())

control_buyers   = len([v for v in control_ids   if v in buyers])
treatment_buyers = len([v for v in treatment_ids if v in buyers])

control_conv   = control_buyers   / len(control_ids)
treatment_conv = treatment_buyers / len(treatment_ids)

print(f"      Control   conversions: {control_buyers:,} / {len(control_ids):,}  = {control_conv*100:.3f}%")
print(f"      Treatment conversions: {treatment_buyers:,} / {len(treatment_ids):,}  = {treatment_conv*100:.3f}%")

# ── Apply +15% uplift to Treatment ────────────────────────
# Simulate what the new checkout would have produced
print("\n[4/5] Applying +15% uplift to Treatment group …")
UPLIFT = 0.15
simulated_treatment_conv = control_conv * (1 + UPLIFT)

# Simulate treatment buyer count using the new rate
np.random.seed(42)
simulated_treatment_buyers = np.random.binomial(
    n   = len(treatment_ids),
    p   = simulated_treatment_conv
)

print(f"      Simulated Treatment conv rate : {simulated_treatment_conv*100:.3f}%")
print(f"      Simulated Treatment buyers    : {simulated_treatment_buyers:,}")

# ── Two-proportion z-test ─────────────────────────────────
print("\n[5/5] Running two-proportion z-test …")

n_control   = len(control_ids)
n_treatment = len(treatment_ids)
x_control   = control_buyers
x_treatment = simulated_treatment_buyers

p_control   = x_control   / n_control
p_treatment = x_treatment / n_treatment
p_pooled    = (x_control + x_treatment) / (n_control + n_treatment)

# z-statistic
se = np.sqrt(p_pooled * (1 - p_pooled) * (1/n_control + 1/n_treatment))
z_stat = (p_treatment - p_control) / se

# p-value (two-tailed)
p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

# 95% confidence interval for the difference
diff = p_treatment - p_control
se_diff = np.sqrt(
    (p_control   * (1 - p_control)   / n_control) +
    (p_treatment * (1 - p_treatment) / n_treatment)
)
ci_lower = diff - 1.96 * se_diff
ci_upper = diff + 1.96 * se_diff

# Relative uplift
relative_uplift = (p_treatment - p_control) / p_control * 100

# Verdict
significant = p_value < 0.05

print(f"""
      ┌─────────────────────────────────────────┐
      │           A/B TEST RESULTS              │
      ├─────────────────────────────────────────┤
      │ Control conv. rate   : {p_control*100:.3f}%          │
      │ Treatment conv. rate : {p_treatment*100:.3f}%          │
      │ Relative uplift      : +{relative_uplift:.1f}%            │
      │ Z-statistic          : {z_stat:.4f}             │
      │ P-value              : {p_value:.6f}          │
      │ 95% CI (difference)  : [{ci_lower*100:.3f}%, {ci_upper*100:.3f}%]│
      │ Significant (p<0.05) : {"✅ YES" if significant else "❌ NO"}                 │
      └─────────────────────────────────────────┘
""")

if significant:
    print("      ✅ Result is statistically significant.")
    print(f"      The new checkout flow drives a {relative_uplift:.1f}% relative")
    print(f"      improvement in conversion. Safe to roll out.")
else:
    print("      ❌ Result is NOT statistically significant.")
    print("      Need more data or a larger effect to conclude.")

# ── Save results ──────────────────────────────────────────
results = pd.DataFrame([{
    "group"                  : "Control",
    "visitors"               : n_control,
    "buyers"                 : x_control,
    "conv_rate_pct"          : round(p_control * 100, 4),
    "simulated"              : False,
}, {
    "group"                  : "Treatment",
    "visitors"               : n_treatment,
    "buyers"                 : x_treatment,
    "conv_rate_pct"          : round(p_treatment * 100, 4),
    "simulated"              : True,
}])

summary = pd.DataFrame([{
    "uplift_applied_pct"     : UPLIFT * 100,
    "relative_uplift_pct"    : round(relative_uplift, 2),
    "z_statistic"            : round(z_stat, 4),
    "p_value"                : round(p_value, 6),
    "ci_lower_pct"           : round(ci_lower * 100, 4),
    "ci_upper_pct"           : round(ci_upper * 100, 4),
    "significant"            : significant,
    "verdict"                : "Roll out" if significant else "Inconclusive",
}])

results.to_csv(os.path.join(OUTDIR, "ab_test_results.csv"), index=False)
summary.to_csv(os.path.join(OUTDIR, "ab_test_summary.csv"), index=False)

print(f"\n✅  Step 4 complete.")
print(f"    - ab_test_results.csv")
print(f"    - ab_test_summary.csv\n")