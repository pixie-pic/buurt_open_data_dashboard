"""
variables.py
────────────
Defines the set of CBS variables surfaced in the dashboard, as (column_key,
display_label) pairs. Order here determines order in the variable dropdown.

To add or remove a variable from the dashboard, edit DASHBOARD_VARIABLES only.
The column key must already exist (or be derivable) after the ETL rename step.
"""

# Each tuple is (english_column_key, human_readable_label).
DASHBOARD_VARIABLES: list[tuple[str, str]] = [
    # ── Demographics ──────────────────────────────────────────────────────────
    ("population_total",                  "Total population"),
    ("population_male",                   "Male population"),
    ("population_female",                 "Female population"),
    ("age_0_14",                          "Age 0–14"),
    ("age_65_plus",                       "Age 65+"),
    # ── Households ───────────────────────────────────────────────────────────
    ("households_total",                  "Total households"),
    ("household_size_avg",                "Average household size"),
    ("population_density_km2",            "Population density"),
    # ── Housing ──────────────────────────────────────────────────────────────
    ("woz_value_avg_x1000eur",            "Avg WOZ property value (×€1,000)"),
    ("pct_single_family_homes",           "% single-family homes"),
    ("pct_social_housing",                "% social housing"),
    ("pct_owner_occupied",                "% owner-occupied"),
    ("pct_built_before_2000",             "% built before 2000"),
    # ── Education ────────────────────────────────────────────────────────────
    ("pct_education_low",                 "% low education"),
    ("pct_education_high",                "% high education"),
    # ── Income & wealth ───────────────────────────────────────────────────────
    ("income_avg_per_recipient_x1000eur", "Avg income per recipient (×€1,000)"),
    ("income_avg_per_resident_x1000eur",  "Avg income per resident (×€1,000)"),
    ("median_household_wealth_x1000eur",  "Median household wealth (×€1,000)"),
    ("pct_low_income_households",         "% low-income households"),
    ("pct_at_social_minimum",             "% at social minimum"),
    # ── Benefits & social support ─────────────────────────────────────────────
    ("n_social_assistance_recipients",    "Social assistance recipients"),
    ("n_disability_benefit_recipients",   "Disability benefit recipients"),
    ("n_unemployment_benefit_recipients", "Unemployment benefit recipients"),
    ("n_state_pension_recipients",        "State pension recipients (AOW)"),
    ("pct_youth_care",                    "% youth receiving care"),
    ("wmo_clients_per1000",               "WMO clients per 1,000"),
    # ── Geography ────────────────────────────────────────────────────────────
    ("area_total_ha",                     "Total area (ha)"),
    ("urbanisation_degree",               "Degree of urbanisation"),
    ("address_density_km2",               "Address density per km²"),
]
