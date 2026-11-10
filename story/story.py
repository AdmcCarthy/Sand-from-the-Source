"""Metrics and derived tables for Sand from the Source. Every number in the prose comes from here, with its method,
source and confidence. Inputs are the extracts in story/data written by scripts/make_extracts.py."""

from subscout import metric

S2S = "s2s"
HYDRO = "hydrosheds"
HOFF = "hoffmann"


def datasets(d):
    c = d["catchments"]
    sys_ = c[c.kind == "system"].copy()
    sys_["label"] = sys_["name"]
    grp = c.groupby("cluster_name", dropna=True).agg(n=("system", "size"), area=("area_km2", "sum"), qs=("qs_mt_yr", "sum"),
                                                     sand=("sand_supply_mt_yr", "sum"), quality=("sand_quality", "mean")).reset_index()
    grp["sand_share"] = grp["sand"] / grp["qs"]
    yields = sys_.sort_values("yield_t_km2_yr", ascending=False)[["label", "yield_t_km2_yr", "glauconite_prone_shelf", "frame"]].copy()
    yields["flag"] = yields["glauconite_prone_shelf"].map({True: "low supply", False: ""})
    return {"groups": grp, "yields": yields.head(30)}


def metrics(d):
    c = d["catchments"]
    sys_ = c[c.kind == "system"]
    f = d["frames"]["frames"]
    qs = c["qs_mt_yr"].sum()
    qs_cal = c["qs_cal_mt_yr"].sum()
    sand = c["sand_supply_mt_yr"].sum()
    big = c[c.area_km2 > 2000]
    glomma = c[c.name == "Glomma"].iloc[0] if (c.name == "Glomma").any() else None
    nor = c[c.frame == "norwegian_sea"]
    checks = f["north_sea"]["checks"]
    glomma_known = next((x["known_mt_yr"] for x in checks if x["river"] == "Glomma"), None)
    return {
        "n_catchments": metric(len(c), "Catchments (river systems over 4,000 km² and coastal groups) on the North Sea and Norwegian Sea frames", source=HYDRO, confidence="observed"),
        "n_systems": metric(len(sys_), "River systems among them", source=HYDRO, confidence="observed"),
        "area_mkm2": metric(c["area_km2"].sum() / 1e6, "Total catchment area, million km²", source=HYDRO, confidence="observed"),
        "qs_total": metric(qs, "BQART sediment flux summed over the catchments, Mt a year", source=S2S, confidence="derived"),
        "qs_cal_total": metric(qs_cal, "The same flux scaled to monitored river loads, Mt a year", source=S2S, confidence="derived"),
        "sand_share": metric(sand / qs if qs else 0, "Share of the flux from sand-prone sources", source=S2S, confidence="derived"),
        "sand_total": metric(sand, "Sand supply proxy summed, Mt a year", source=S2S, confidence="derived"),
        "median_yield": metric(c["yield_t_km2_yr"].median(), "Median sediment yield of the catchments, t per km² a year (BQART)", source=S2S, confidence="derived"),
        "glauconite_share": metric(big["glauconite_prone_shelf"].mean(), "Share of catchments over 2,000 km² whose yield is under 10 t per km² a year", source=S2S, confidence="interpreted"),
        "glomma_qs": metric(float(glomma["qs_mt_yr"]) if glomma is not None else 0, "BQART flux for the Glomma, Mt a year", source=S2S, confidence="derived"),
        "glomma_known": metric(glomma_known or 0, "Monitored Glomma load used for the check, Mt a year (order of magnitude, from the NVE record)", source=S2S, confidence="observed"),
        "nor_shield": metric((nor["frac_igneous_felsic"] + nor["frac_gneiss_quartzite"]).mul(nor["area_km2"]).sum() / nor["area_km2"].sum(),
                             "Area-weighted share of granite, felsic volcanics, gneiss and quartzite in the Norwegian Sea catchments", source=S2S, confidence="derived"),
        "nor_carbonate": metric(nor["frac_carbonate"].mul(nor["area_km2"]).sum() / nor["area_km2"].sum(), "Area-weighted carbonate share, Norwegian Sea catchments", source=S2S, confidence="derived"),
        "quality_max": metric(c["sand_quality"].max(), "Highest sand quality proxy among the catchments", source=S2S, confidence="derived"),
        "quality_median": metric(c["sand_quality"].median(), "Median sand quality proxy", source=S2S, confidence="derived"),
        "n_groups": metric(c["cluster_name"].nunique(), "Composition groups found by k-means", source=S2S, confidence="derived"),
        "rhine_monitored": metric(1.0, "Monitored Rhine load at the German-Dutch border, Mt a year, near a natural baseline of about 1 Mt a year", source=HOFF, confidence="observed"),
    }
