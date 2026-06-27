"""
Sample Data Generator for LeadPredict (v2 — Realistic Patterns).

Generates 10,000 synthetic lead records with rich, realistic sales-cycle patterns.

Classes:
    0 = COLD   — Dead lead, no interest, low engagement
    1 = REJECTED — Actively said no, some engagement but lost
    2 = SUCCESSFUL — Converted, high engagement and positive signals

Key improvements over v1:
    - 10,000 samples (was 2,500)
    - lead_source and industry are predictive of outcome
    - call_duration_minutes strongly correlates with success
    - meetings_done / meetings_scheduled ratio matters
    - employee_prev_conversion_rate increases success probability
    - ~10% noise makes it non-trivial
"""

import numpy as np
import pandas as pd
import os

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
RNG = np.random.default_rng(seed=42)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
NUM_SAMPLES = 10000
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "lead_data.csv")

LEAD_SOURCES = [
    "Google Ads", "Facebook", "LinkedIn", "Referral",
    "Organic", "Cold Call", "Email Campaign",
]

INDUSTRIES = [
    "Technology", "Healthcare", "Finance", "Education",
    "E-commerce", "Real Estate", "Manufacturing",
]

CATEGORICAL_FEATURES = ["lead_source", "industry"]

# ---------------------------------------------------------------------------
# Outcome-dependent source/industry distributions
# ---------------------------------------------------------------------------
# lead_source distribution per outcome group
SOURCE_DIST = {
    "successful": {
        "Referral": 0.30, "Organic": 0.25, "LinkedIn": 0.15,
        "Email Campaign": 0.13, "Google Ads": 0.10,
        "Facebook": 0.05, "Cold Call": 0.02,
    },
    "rejected": {
        "Google Ads": 0.25, "Facebook": 0.20, "LinkedIn": 0.16,
        "Email Campaign": 0.15, "Organic": 0.10,
        "Cold Call": 0.08, "Referral": 0.06,
    },
    "cold": {
        "Cold Call": 0.32, "Facebook": 0.25, "Google Ads": 0.20,
        "LinkedIn": 0.10, "Email Campaign": 0.07,
        "Organic": 0.04, "Referral": 0.02,
    },
}

# industry distribution per outcome group
IND_DIST = {
    "successful": {
        "Technology": 0.22, "Healthcare": 0.18, "Finance": 0.16,
        "Education": 0.14, "E-commerce": 0.12,
        "Real Estate": 0.09, "Manufacturing": 0.09,
    },
    "rejected": {
        "Finance": 0.18, "E-commerce": 0.17, "Real Estate": 0.16,
        "Manufacturing": 0.15, "Healthcare": 0.13,
        "Education": 0.12, "Technology": 0.09,
    },
    "cold": {
        "Real Estate": 0.20, "Manufacturing": 0.18, "Finance": 0.17,
        "E-commerce": 0.15, "Education": 0.12,
        "Healthcare": 0.10, "Technology": 0.08,
    },
}

# ---------------------------------------------------------------------------
# Noise model: ~10% label flips
# ---------------------------------------------------------------------------
NOISE_MAP = {
    "cold":      {0: 0.90, 1: 0.07, 2: 0.03},
    "rejected":  {0: 0.06, 1: 0.90, 2: 0.04},
    "successful": {0: 0.03, 1: 0.07, 2: 0.90},
}

OUTCOME_KEYS = {0: "cold", 1: "rejected", 2: "successful"}


def _add_noise(outcome_group: str) -> int:
    """Apply ~10% noise to flip the intended label."""
    probs = NOISE_MAP[outcome_group]
    labels = list(probs.keys())
    weights = list(probs.values())
    return int(RNG.choice(labels, p=weights))


def _weighted_choice(options: list[str], weights: dict[str, float]) -> str:
    """Pick from options using the given weight dict (normalised)."""
    w = np.array([weights[opt] for opt in options], dtype=float)
    w /= w.sum()
    return str(RNG.choice(options, p=w))


# ---------------------------------------------------------------------------
# Main generation function
# ---------------------------------------------------------------------------

def _clamp(val, lo, hi):
    return int(max(lo, min(hi, val)))


def generate_lead_data(n: int = NUM_SAMPLES) -> pd.DataFrame:
    """Generate *n* synthetic lead records with realistic sales-cycle patterns.

    Returns a pandas DataFrame ready for ML training.
    """
    records: list[dict] = []

    # Base distribution: 30% successful, 35% rejected, 35% cold
    outcome_groups = RNG.choice(
        ["cold", "rejected", "successful"],
        size=n,
        p=[0.35, 0.35, 0.30],
    )

    for outcome_group in outcome_groups:
        # --- Source & Industry (predictive) ---
        lead_source = _weighted_choice(LEAD_SOURCES, SOURCE_DIST[outcome_group])
        industry = _weighted_choice(INDUSTRIES, IND_DIST[outcome_group])
        company_size = int(np.round(RNG.lognormal(mean=4.5, sigma=1.5)))
        company_size = max(1, min(company_size, 5000))

        # --- Employee features ---
        if outcome_group == "successful":
            tenure = int(RNG.integers(100, 1000))
            prev_conv = round(RNG.uniform(0.30, 0.60), 4)
        elif outcome_group == "rejected":
            tenure = int(RNG.integers(60, 800))
            prev_conv = round(RNG.uniform(0.15, 0.40), 4)
        else:  # cold
            tenure = int(RNG.integers(30, 600))
            prev_conv = round(RNG.uniform(0.05, 0.22), 4)

        # --- Engagement features ---
        if outcome_group == "successful":
            # HIGH engagement across the board
            website_visits = int(RNG.integers(20, 50))
            emails_opened = int(RNG.integers(10, 20))
            emails_clicked = int(RNG.integers(4, 10))
            calls_made = int(RNG.integers(6, 15))
            calls_connected = int(RNG.integers(4, 10))
            meetings_scheduled = int(RNG.integers(3, 5))
            # meetings_done close to scheduled (ratio > 0.8)
            meetings_done = int(RNG.integers(
                int(meetings_scheduled * 0.8), meetings_scheduled + 1
            ))
            days_since = int(RNG.integers(45, 365))
            follow_ups = int(RNG.integers(10, 30))

            # call_duration_minutes: HIGH — average call is 12-20 min, many calls
            avg_call_len = RNG.uniform(12, 22)
            call_dur = int(avg_call_len * calls_connected)
            call_dur = _clamp(call_dur, 60, 300)

            # Bool signals — strongly positive
            demo = int(RNG.choice([0, 1], p=[0.08, 0.92]))
            budget = int(RNG.choice([0, 1], p=[0.10, 0.90]))
            dm_contacted = int(RNG.choice([0, 1], p=[0.06, 0.94]))
            competitor = int(RNG.choice([0, 1], p=[0.65, 0.35]))  # mostly not considering

        elif outcome_group == "rejected":
            # MODERATE engagement with stalling signals
            website_visits = int(RNG.integers(8, 40))
            emails_opened = int(RNG.integers(4, 16))
            emails_clicked = int(RNG.integers(1, 7))
            calls_made = int(RNG.integers(4, 12))
            calls_connected = int(RNG.integers(2, 7))
            meetings_scheduled = int(RNG.integers(1, 4))
            # Low meeting completion ratio (< 0.4)
            max_done = max(0, int(meetings_scheduled * 0.4))
            meetings_done = int(RNG.integers(0, max_done + 1))
            days_since = int(RNG.integers(30, 200))
            follow_ups = int(RNG.integers(6, 22))

            # call_duration_minutes: MODERATE but inconsistent
            avg_call_len = RNG.uniform(6, 12)
            call_dur = int(avg_call_len * calls_connected)
            call_dur = _clamp(call_dur, 10, 60)

            # Bool signals — mixed, competitor high
            demo = int(RNG.choice([0, 1], p=[0.40, 0.60]))
            budget = int(RNG.choice([0, 1], p=[0.40, 0.60]))
            dm_contacted = int(RNG.choice([0, 1], p=[0.30, 0.70]))
            competitor = int(RNG.choice([0, 1], p=[0.25, 0.75]))  # mostly considering

        else:  # cold
            # LOW everything
            website_visits = int(RNG.integers(0, 10))
            emails_opened = int(RNG.integers(0, 5))
            emails_clicked = int(RNG.integers(0, 2))
            calls_made = int(RNG.integers(0, 5))
            calls_connected = int(max(0, int(RNG.integers(0, min(3, calls_made + 1)))))
            meetings_scheduled = int(RNG.integers(0, 1))
            meetings_done = 0
            days_since = int(RNG.integers(1, 80))
            follow_ups = int(RNG.integers(0, 8))

            # call_duration_minutes: VERY LOW
            call_dur = int(RNG.exponential(scale=5))
            call_dur = min(call_dur, 20)

            # Bool signals — mostly absent
            demo = int(RNG.choice([0, 1], p=[0.92, 0.08]))
            budget = int(RNG.choice([0, 1], p=[0.65, 0.35]))
            dm_contacted = int(RNG.choice([0, 1], p=[0.75, 0.25]))
            competitor = int(RNG.choice([0, 1], p=[0.50, 0.50]))

        # --- Enforce consistency constraints ---
        if calls_made == 0:
            calls_connected = 0
            call_dur = 0
        if calls_connected > calls_made:
            calls_connected = calls_made
        if meetings_scheduled == 0:
            meetings_done = 0
        if meetings_done > meetings_scheduled:
            meetings_done = meetings_scheduled
        if emails_opened == 0:
            emails_clicked = 0
        if emails_clicked > emails_opened:
            emails_clicked = emails_opened

        # --- Apply label noise (~10% flips) ---
        outcome = _add_noise(outcome_group)

        row = {
            "lead_source": lead_source,
            "industry": industry,
            "company_size": company_size,
            "website_visits": website_visits,
            "emails_opened": emails_opened,
            "emails_clicked": emails_clicked,
            "calls_made": calls_made,
            "calls_connected": calls_connected,
            "call_duration_minutes": call_dur,
            "meetings_scheduled": meetings_scheduled,
            "meetings_done": meetings_done,
            "days_since_first_contact": days_since,
            "follow_ups_total": follow_ups,
            "demo_requested": demo,
            "budget_available": budget,
            "decision_maker_contacted": dm_contacted,
            "competitor_considering": competitor,
            "employee_tenure_days": tenure,
            "employee_prev_conversion_rate": prev_conv,
            "outcome": outcome,
        }
        records.append(row)

    df = pd.DataFrame(records)

    # ---- Distribution check ----
    print(f"Generated {len(df)} records.")
    print(f"Class distribution:\n{df['outcome'].value_counts().sort_index()}")
    print(f"\nClass proportions:\n{df['outcome'].value_counts(normalize=True).sort_index()}")

    # Quick sanity: call_duration_minutes vs outcome
    print(f"\ncall_duration_minutes by outcome:")
    print(df.groupby("outcome")["call_duration_minutes"].describe())

    # meeting completion ratio sanity
    df_check = df.copy()
    df_check["meeting_ratio"] = df_check["meetings_done"] / np.maximum(df_check["meetings_scheduled"], 1)
    print(f"\nMeeting completion ratio by outcome:")
    print(df_check.groupby("outcome")["meeting_ratio"].describe())

    return df


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    df = generate_lead_data()
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nData saved to {OUTPUT_PATH}")
