"""
column_map.py
─────────────
Dutch → English column name translations for the CBS 2022 kerncijfers buurten
dataset. Kept separate so it can be imported by both the ETL script and any
downstream notebooks without duplication.
"""

# Maps original CBS column names to descriptive English equivalents.
# Only columns that are used downstream are included; others are left as-is.
COLUMN_TRANSLATIONS: dict[str, str] = {
    "WijkenEnBuurten":                        "neighbourhood_code",
    "Gemeentenaam_1":                         "municipality_name",
    "SoortRegio_2":                           "region_type",
    "Codering_3":                             "region_code",
    "IndelingswijzigingGemeenteWijkBuurt_4":  "boundary_change_indicator",
    # ── Demographics ──────────────────────────────────────────────────────────
    "AantalInwoners_5":                       "population_total",
    "Mannen_6":                               "population_male",
    "Vrouwen_7":                              "population_female",
    "k_0Tot15Jaar_8":                         "age_0_14",
    "k_15Tot25Jaar_9":                        "age_15_24",
    "k_25Tot45Jaar_10":                       "age_25_44",
    "k_45Tot65Jaar_11":                       "age_45_64",
    "k_65JaarOfOuder_12":                     "age_65_plus",
    # ── Marital status ────────────────────────────────────────────────────────
    "Ongehuwd_13":                            "marital_never_married",
    "Gehuwd_14":                              "marital_married",
    "Gescheiden_15":                          "marital_divorced",
    "Verweduwd_16":                           "marital_widowed",
    # ── Migration background ──────────────────────────────────────────────────
    "WestersTotaal_17":                       "migration_western_total",
    "NietWestersTotaal_18":                   "migration_nonwestern_total",
    "Marokko_19":                             "migration_moroccan",
    "NederlandseAntillenEnAruba_20":          "migration_antilles_aruba",
    "Suriname_21":                            "migration_surinamese",
    "Turkije_22":                             "migration_turkish",
    "OverigNietWesters_23":                   "migration_other_nonwestern",
    # ── Births & deaths ───────────────────────────────────────────────────────
    "GeboorteTotaal_24":                      "births_total",
    "GeboorteRelatief_25":                    "birth_rate_per1000",
    "SterfteTotaal_26":                       "deaths_total",
    "SterfteRelatief_27":                     "death_rate_per1000",
    # ── Households ───────────────────────────────────────────────────────────
    "HuishoudensTotaal_28":                   "households_total",
    "Eenpersoonshuishoudens_29":              "households_single_person",
    "HuishoudensZonderKinderen_30":           "households_without_children",
    "HuishoudensMetKinderen_31":              "households_with_children",
    "GemiddeldeHuishoudensgrootte_32":        "household_size_avg",
    "Bevolkingsdichtheid_33":                 "population_density_km2",
    # ── Housing ──────────────────────────────────────────────────────────────
    "Woningvoorraad_34":                      "housing_stock",
    "GemiddeldeWOZWaardeVanWoningen_35":      "woz_value_avg_x1000eur",
    "PercentageEengezinswoning_36":           "pct_single_family_homes",
    "PercentageMeergezinswoning_37":          "pct_multi_family_homes",
    "PercentageBewoond_38":                   "pct_occupied_dwellings",
    "PercentageOnbewoond_39":                 "pct_unoccupied_dwellings",
    "Koopwoningen_40":                        "pct_owner_occupied",
    "HuurwoningenTotaal_41":                  "pct_rental_total",
    "InBezitWoningcorporatie_42":             "pct_social_housing",
    "InBezitOverigeVerhuurders_43":           "pct_private_landlord",
    "EigendomOnbekend_44":                    "pct_ownership_unknown",
    "BouwjaarVoor2000_45":                    "pct_built_before_2000",
    "BouwjaarVanaf2000_46":                   "pct_built_from_2000",
    "Huurwoning_53":                          "pct_rental_dwelling",
    "EigenWoning_54":                         "pct_owner_dwelling",
    # ── Education ────────────────────────────────────────────────────────────
    "OpleidingsniveauLaag_64":                "pct_education_low",
    "OpleidingsniveauMiddelbaar_65":          "pct_education_medium",
    "OpleidingsniveauHoog_66":               "pct_education_high",
    # ── Income & wealth ───────────────────────────────────────────────────────
    "AantalInkomensontvangers_70":            "n_income_recipients",
    "GemiddeldInkomenPerInkomensontvanger_71":"income_avg_per_recipient_x1000eur",
    "GemiddeldInkomenPerInwoner_72":          "income_avg_per_resident_x1000eur",
    "k_40PersonenMetLaagsteInkomen_73":       "pct_bottom40_income_persons",
    "k_20PersonenMetHoogsteInkomen_74":       "pct_top20_income_persons",
    "GemGestandaardiseerdInkomenVanHuish_75": "income_standardised_avg_x1000eur",
    "k_40HuishoudensMetLaagsteInkomen_76":    "pct_bottom40_income_households",
    "k_20HuishoudensMetHoogsteInkomen_77":    "pct_top20_income_households",
    "HuishoudensMetEenLaagInkomen_78":        "pct_low_income_households",
    "HuishOnderOfRondSociaalMinimum_79":      "pct_at_social_minimum",
    "HuishoudensTot110VanSociaalMinimum_80":  "pct_up_to_110pct_social_minimum",
    "HuishoudensTot120VanSociaalMinimum_81":  "pct_up_to_120pct_social_minimum",
    "MediaanVermogenVanParticuliereHuish_82": "median_household_wealth_x1000eur",
    # ── Benefits & social support ─────────────────────────────────────────────
    "PersonenPerSoortUitkeringBijstand_83":   "n_social_assistance_recipients",
    "PersonenPerSoortUitkeringAO_84":         "n_disability_benefit_recipients",
    "PersonenPerSoortUitkeringWW_85":         "n_unemployment_benefit_recipients",
    "PersonenPerSoortUitkeringAOW_86":        "n_state_pension_recipients",
    "JongerenMetJeugdzorgInNatura_87":        "n_youth_care_recipients",
    "PercentageJongerenMetJeugdzorg_88":      "pct_youth_care",
    "WmoClienten_89":                         "n_wmo_clients",
    "WmoClientenRelatief_90":                 "wmo_clients_per1000",
    # ── Geography ────────────────────────────────────────────────────────────
    "OppervlakteTotaal_111":                  "area_total_ha",
    "OppervlakteLand_112":                    "area_land_ha",
    "OppervlakteWater_113":                   "area_water_ha",
    "MateVanStedelijkheid_116":               "urbanisation_degree",
    "Omgevingsadressendichtheid_117":         "address_density_km2",
}

# Columns used as identifiers — excluded from numeric coercion.
ID_COLUMNS: set[str] = {
    "ID",
    "WijkenEnBuurten",
    "Gemeentenaam_1",
    "SoortRegio_2",
    "Codering_3",
}
