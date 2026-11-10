"""Metrics and derived tables for Sand from the Source. Every number in the prose comes from here, with its method,
source and confidence. Inputs are the extracts in story/data written by scripts/make_extracts.py."""

from subscout import metric

S2S = "s2s"
HYDRO = "hydrosheds"
HOFF = "hoffmann"
TERRAINS = ["Britain and Ireland", "Norway", "Sweden and Finland", "Continental lowlands", "France and Iberia",
            "Alps, Italy and the Balkans", "Eastern Europe", "Iceland"]


def datasets(d):
    c = d["catchments"]
    comp = d["compare"].copy()
    comp = comp[comp["terrain"].isin(TERRAINS)].set_index("terrain").loc[[t for t in TERRAINS if t in set(comp["terrain"])]].reset_index()
    comp["yield_label"] = comp["terrain"]
    comp["quality_pct"] = comp["quality_area_weighted"] * 100
    comp["sand_share_pct"] = comp["sand_share"] * 100
    comp["shield_pct"] = comp["shield_share"] * 100
    comp["clastic_pct"] = comp["clastic_share"] * 100
    comp["carbonate_pct"] = comp["carbonate_share"] * 100
    comp["cover_pct"] = comp["cover_share"] * 100
    comp["mud_pct"] = comp["mud_share"] * 100
    comp["other_pct"] = (100 - comp["shield_pct"] - comp["clastic_pct"] - comp["carbonate_pct"] - comp["cover_pct"]).clip(lower=0)
    comp["total_pct"] = comp["shield_pct"] + comp["clastic_pct"] + comp["carbonate_pct"] + comp["cover_pct"] + comp["other_pct"]
    sys_ = c[c.kind == "system"].copy()
    return {"compare_t": comp, "systems": sys_}


def _t(d, terrain, col):
    comp = d["compare"].set_index("terrain")
    return float(comp.loc[terrain, col]) if terrain in comp.index else 0.0


def metrics(d):
    c = d["catchments"]
    sys_ = c[c.kind == "system"]
    f = d["frames"]["frames"]
    qs = c["qs_mt_yr"].sum()
    qs_cal = c["qs_cal_mt_yr"].sum()
    sand = c["sand_supply_mt_yr"].sum()
    big = c[c.area_km2 > 2000]
    glomma = c[c.name == "Glomma"].iloc[0] if (c.name == "Glomma").any() else None
    checks = f["ne_europe"]["checks"] if "ne_europe" in f else f["north_sea"]["checks"]
    known = {x["river"]: x for x in checks}
    m = {
        "n_catchments": metric(len(c), "Catchments (river systems over 4,000 km² and coastal groups) between Iceland and the Caspian, each whole and counted once", source=HYDRO, confidence="observed"),
        "n_systems": metric(len(sys_), "River systems among them", source=HYDRO, confidence="observed"),
        "area_mkm2": metric(c["area_km2"].sum() / 1e6, "Total catchment area, million km²", source=HYDRO, confidence="observed"),
        "qs_total": metric(qs, "BQART sediment flux summed over the catchments, Mt a year", source=S2S, confidence="derived"),
        "qs_cal_total": metric(qs_cal, "The same flux scaled to monitored river loads, Mt a year", source=S2S, confidence="derived"),
        "sand_share": metric(sand / qs if qs else 0, "Share of the flux from sand-prone sources", source=S2S, confidence="derived"),
        "sand_total": metric(sand, "Sand supply proxy summed, Mt a year", source=S2S, confidence="derived"),
        "median_yield": metric(c["yield_t_km2_yr"].median(), "Median sediment yield of the catchments, t per km² a year (BQART)", source=S2S, confidence="derived"),
        "glauconite_share": metric(big["glauconite_prone_shelf"].mean(), "Share of catchments over 2,000 km² whose yield is under 10 t per km² a year", source=S2S, confidence="interpreted"),
        "glomma_qs": metric(float(glomma["qs_mt_yr"]) if glomma is not None else 0, "BQART flux for the Glomma, Mt a year", source=S2S, confidence="derived"),
        "glomma_known": metric(known.get("Glomma", {}).get("known_mt_yr", 0), "Monitored Glomma load used for the check, Mt a year (order of magnitude, from the NVE record)", source=S2S, confidence="observed"),
        "rhine_qs": metric(known.get("Rhine", {}).get("model_mt_yr", 0), "BQART flux for the Rhine, Mt a year", source=S2S, confidence="derived"),
        "rhine_ratio": metric(known.get("Rhine", {}).get("ratio_model_over_known", 0), "Rhine model flux over monitored load", source=S2S, confidence="derived"),
        "n_groups": metric(c["cluster_name"].nunique(), "Composition groups found by k-means", source=S2S, confidence="derived"),
        "quality_max": metric(c["sand_quality"].max(), "Highest sand quality proxy among the catchments", source=S2S, confidence="derived"),
        "quality_median": metric(c["sand_quality"].median(), "Median sand quality proxy", source=S2S, confidence="derived"),
        "rhine_monitored": metric(1.0, "Monitored Rhine load at the German-Dutch border, Mt a year, near a natural baseline of about 1 Mt a year", source=HOFF, confidence="observed"),
    }
    for key, terrain in (("brit", "Britain and Ireland"), ("nor", "Norway"), ("swe", "Sweden and Finland"), ("low", "Continental lowlands"),
                         ("fr", "France and Iberia"), ("alp", "Alps, Italy and the Balkans"), ("east", "Eastern Europe"), ("ice", "Iceland")):
        m[f"{key}_yield"] = metric(_t(d, terrain, "yield_median"), f"Median BQART yield, {terrain}, t per km² a year", source=S2S, confidence="derived")
        m[f"{key}_quality"] = metric(_t(d, terrain, "quality_area_weighted"), f"Area-weighted sand quality proxy, {terrain}", source=S2S, confidence="derived")
        m[f"{key}_sand_share"] = metric(_t(d, terrain, "sand_share"), f"Sand share of the flux, {terrain}", source=S2S, confidence="derived")
        m[f"{key}_shield"] = metric(_t(d, terrain, "shield_share"), f"Area share of granite, felsic volcanics, gneiss and quartzite, {terrain}", source=S2S, confidence="derived")
        m[f"{key}_clastic"] = metric(_t(d, terrain, "clastic_share"), f"Area share of clastic sedimentary rock, {terrain}", source=S2S, confidence="derived")
        m[f"{key}_carbonate"] = metric(_t(d, terrain, "carbonate_share"), f"Area share of carbonate rock, {terrain}", source=S2S, confidence="derived")
        m[f"{key}_cover"] = metric(_t(d, terrain, "cover_share"), f"Area share of unconsolidated cover, {terrain}", source=S2S, confidence="derived")
        m[f"{key}_mud"] = metric(_t(d, terrain, "mud_share"), f"Area share of mud-prone clastic rock (shale, mudstone, slate, marl), {terrain}", source=S2S, confidence="derived")
        m[f"{key}_mixed"] = metric(_t(d, terrain, "mixed_share"), f"Area share of clastic rock mapped as interbedded sandstone and mudstone, {terrain}", source=S2S, confidence="derived")
        m[f"{key}_mud_led"] = metric(_t(d, terrain, "mud_led_share"), f"Area share of interbedded clastic rock the survey names mudstone first, {terrain}", source=S2S, confidence="derived")
        m[f"{key}_sand_led"] = metric(_t(d, terrain, "sand_led_share"), f"Area share of interbedded clastic rock the survey names sandstone first, {terrain}", source=S2S, confidence="derived")
        m[f"{key}_schist"] = metric(_t(d, terrain, "schist_share"), f"Area share of schist and phyllite, {terrain}", source=S2S, confidence="derived")
        m[f"{key}_mafic"] = metric(_t(d, terrain, "mafic_share"), f"Area share of mafic and metavolcanic rock, {terrain}", source=S2S, confidence="derived")
        m[f"{key}_qs"] = metric(_t(d, terrain, "qs_mt_yr"), f"BQART flux summed, {terrain}, Mt a year", source=S2S, confidence="derived")
        m[f"{key}_n"] = metric(int(_t(d, terrain, "n")), f"Catchments, {terrain}", source=HYDRO, confidence="observed")
    return m
