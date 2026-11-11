"""Write the small public extracts for the story from the private sibling repos.

Reads source-to-sink/data/derived/europe/ (every drainage system from Iceland to the Caspian edge, whole, with composition, budget
and groups; rivers; slope flow; outlets) and Relief/data/out/<frame>_wide/ (the landscape region: hillshade, base maps and the 0 m
land band), cuts the Europe set to each frame's map extent, and writes story/data/. One catchment set serves every frame, so a
system is never cut at a frame edge and a zoomed-out map is as complete as a close one. See DATA-LICENCE.md. Everything written
is derived and generalised; no raw survey map is copied.
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
import shapely
from PIL import Image
from shapely.geometry import box, mapping

ROOT = Path(__file__).resolve().parents[1]
S2S = ROOT.parent / "source-to-sink" / "data" / "derived"
EU = S2S / "europe"
RELIEF = ROOT.parent / "Relief" / "data" / "out"
OUT = ROOT / "story" / "data"
FRAMES = ["ne_europe", "north_sea", "norwegian_sea"]
# The map behind each frame is Relief's landscape (2 : 1) region in the frame's own projection, wider than the catchment frame (Idiom
# house/screens.md): the catchments fill the old frame, the margin is context. Images are 2,400 px wide, twice the page frame.
RELIEF_REGION = {fr: f"{fr}_wide" for fr in FRAMES}
IMG_W = 2400
KEEP = ["system", "name", "kind", "frame", "area_km2", "size_class", "cluster", "cluster_name", "mapped_frac", "composition_source",
        "sand_quality", "sand_share", "qs_mt_yr", "qs_cal_mt_yr", "sand_supply_mt_yr", "sand_cal_mt_yr", "yield_t_km2_yr", "relief_max_m",
        "temp_c", "q_km3_yr", "q_source", "lithology_factor", "glauconite_prone_shelf", "discharge_cms", "mainstem_km",
        "frac_igneous_felsic", "frac_igneous_mafic", "frac_gneiss_quartzite", "frac_schist", "frac_clastic", "frac_carbonate", "frac_unconsolidated", "frac_other",
        "age_Cenozoic", "age_Mesozoic", "age_Paleozoic", "age_Neoproterozoic", "age_Older_Proterozoic", "age_Archean", "age_unread",
        "grain_clastic_sand", "grain_clastic_mud", "grain_clastic_mixed", "grain_clastic_mixed_sand", "grain_clastic_mixed_mud"]


def topo_to_geojson(path: Path, obj: str, keep: list[str] | None = None) -> dict:
    """TopoJSON to GeoJSON without a dependency: delta-decoded arcs on the quantised transform. SubScout's page has no
    topojson-client, so the story ships GeoJSON in the frame CRS."""
    t = json.loads(path.read_text(encoding="utf-8"))
    tr = t.get("transform")
    arcs = []
    for arc in t["arcs"]:
        pts, x, y = [], 0, 0
        for dx, dy in arc:
            x += dx; y += dy
            pts.append([round(x * tr["scale"][0] + tr["translate"][0], 1), round(y * tr["scale"][1] + tr["translate"][1], 1)] if tr else [x, y])
        arcs.append(pts)

    def ring(idxs):
        out = []
        for i in idxs:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            out.extend(a if not out else a[1:])
        return out

    feats = []
    for g in t["objects"][obj]["geometries"]:
        props = g.get("properties") or {}
        if keep:
            props = {k: props.get(k) for k in keep}
        if g["type"] == "Polygon":
            geom = {"type": "Polygon", "coordinates": [ring(r) for r in g["arcs"]]}
        elif g["type"] == "MultiPolygon":
            geom = {"type": "MultiPolygon", "coordinates": [[ring(r) for r in poly] for poly in g["arcs"]]}
        elif g["type"] == "LineString":
            geom = {"type": "LineString", "coordinates": ring(g["arcs"])}
        elif g["type"] == "MultiLineString":
            geom = {"type": "MultiLineString", "coordinates": [ring(a) for a in g["arcs"]]}
        else:
            continue
        feats.append({"type": "Feature", "properties": props, "geometry": geom})
    return {"type": "FeatureCollection", "features": feats}


def clean(v):
    """JSON-safe property value: NaN and infinities become null."""
    if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
        return None
    return v


def cut_to_frame(fc: dict, src_crs: str, dst_crs: str, extent: list[float], thin: int = 1, min_cells: int = 0) -> dict:
    """The features of a Europe layer that touch a frame's extent, in the frame's projection, coordinates to the metre."""
    feats = [f for f in fc["features"] if f.get("geometry")]
    if not feats:
        return {"type": "FeatureCollection", "features": []}
    g = gpd.GeoDataFrame.from_features(feats, crs=src_crs).to_crs(dst_crs)
    keep = g.intersects(box(*extent)).to_numpy()
    out = []
    for i, (geom, f) in enumerate(zip(shapely.set_precision(g.geometry.values, 1.0, mode="pointwise"), feats)):
        props = f["properties"]
        if not keep[i] or geom is None or geom.is_empty:
            continue
        if thin > 1 and i % thin:
            continue
        if min_cells and (props.get("cells") or 0) < min_cells:
            continue
        out.append({"type": "Feature", "properties": {k: clean(v) for k, v in props.items()}, "geometry": mapping(geom)})
    return {"type": "FeatureCollection", "features": out}


def terrain_of(lon: float | None, lat: float | None) -> str:
    """The source terrain of a catchment, by its centroid: the ground it drains, in the groups the story compares."""
    if lon is None:
        return "unplaced"
    if lon < -12 and lat > 62:
        return "Iceland"
    if lon < 2.5 and 49.5 <= lat < 61.5 and lon > -11:
        return "Britain and Ireland"
    # the Scandinavian divide runs north-east from Trondelag: Norway lies west of it
    if lat >= 57.5 and lon < 12.5 or lat >= 63 and lon < 12 + (lat - 63) * 1.9:
        return "Norway"
    if lat >= 55.3 and 12.5 <= lon < 32 and (lat >= 60 or lon < 19.5):
        return "Sweden and Finland"
    if lat < 42 and lon >= 26 or lat < 37 or lat >= 66 and lon >= 32:
        return "Beyond Europe"  # Anatolia, the Caucasus, North Africa, the Kola coast: left out of the comparison
    if lon < 8 and lat < 49.5:
        return "France and Iberia"
    if lat < 48:
        return "Alps, Italy and the Balkans"
    if lon >= 32 or lon >= 27 and lat < 52:
        return "Eastern Europe"
    return "Continental lowlands"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {"frames": {}}
    eu = json.loads((EU / "layers.json").read_text(encoding="utf-8"))
    eu_crs = eu["crs"]
    systems = pd.read_csv(EU / "systems.csv")
    sys_keep = ["system", "name", "kind", "area_km2", "log10_area", "size_class", "cluster", "cluster_name", "mapped_frac", "sand_quality",
                "qs_mt_yr", "qs_cal_mt_yr", "sand_supply_mt_yr", "yield_t_km2_yr", "glauconite_prone_shelf", "discharge_cms"]
    eu_systems = topo_to_geojson(EU / "systems.topojson", "systems", sys_keep)
    eu_rivers = topo_to_geojson(EU / "rivers.topojson", "rivers", ["system", "log_discharge"])
    eu_outlets = json.loads((EU / "outlets.geojson").read_text(encoding="utf-8"))
    eu_flow = json.loads((EU / "slope_flow.geojson").read_text(encoding="utf-8"))
    flow_crs = json.loads((RELIEF / eu["relief"]["region"] / "demo" / "meta.json").read_text(encoding="utf-8"))["crs"]  # the lines are in Relief's frame CRS
    for fr in FRAMES:
        lay = json.loads((S2S / fr / "layers.json").read_text(encoding="utf-8"))
        rr = RELIEF_REGION[fr]
        man = json.loads((RELIEF / rr / "manifest.json").read_text(encoding="utf-8"))
        ext, fcrs = man["extent"], man["crs"]
        # the Europe set cut to this frame's map: whole systems, so nothing stops at an old frame edge
        cat = cut_to_frame(eu_systems, eu_crs, fcrs, ext)
        (OUT / f"{fr}_catchments.geojson").write_text(json.dumps(cat, separators=(",", ":")), encoding="utf-8")
        (OUT / f"{fr}_rivers.geojson").write_text(json.dumps(cut_to_frame(eu_rivers, eu_crs, fcrs, ext), separators=(",", ":")), encoding="utf-8")
        (OUT / f"{fr}_outlets.geojson").write_text(json.dumps(cut_to_frame(eu_outlets, eu_crs, fcrs, ext), separators=(",", ":")), encoding="utf-8")
        sf = cut_to_frame(eu_flow, flow_crs, fcrs, ext, thin=5, min_cells=6)
        (OUT / f"{fr}_slope_flow.geojson").write_text(json.dumps(sf, separators=(",", ":")), encoding="utf-8")
        # Relief: the hillshade reduced to IMG_W px wide and the 0 m land band, with the frame extent
        im = Image.open(RELIEF / rr / "regional_hillshade.png").convert("L")
        im.thumbnail((IMG_W, IMG_W))
        (ROOT / "story" / "figures").mkdir(exist_ok=True)
        im.save(ROOT / "story" / "figures" / f"{fr}_hillshade.png", optimize=True)  # beside basin.js, which is copied into the site
        bands = json.loads((RELIEF / rr / "regional.geojson").read_text(encoding="utf-8"))
        land = [f for f in bands["features"] if f["properties"]["kind"] == "land" and f["properties"]["level"] == 0]
        (OUT / f"{fr}_land.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": land}, separators=(",", ":")), encoding="utf-8")
        # Relief's base map (linear bathymetry, stepped climate-tinted land; Relief/docs/base-maps.md), reduced like the hillshade,
        # and its depth scale for the key
        for th, name in man["base"]["regional"].items():
            b = Image.open(RELIEF / rr / name).convert("RGB")
            b = b.resize((IMG_W, round(b.height * IMG_W / b.width)), Image.LANCZOS)
            b.save(ROOT / "story" / "figures" / f"{fr}_base_{th}.png", optimize=True)
        sinks = {s["name"]: s for s in [*lay.get("sinks", []), *eu.get("sinks", [])]}.values()
        manifest["frames"][fr] = {"name": lay["name"], "crs": fcrs, "extent": ext, "bbox": eu["bbox"], "sinks": list(sinks),
                                  "clusters": eu["clusters"], "budget": eu["budget"], "checks": eu.get("checks", []), "built": eu["built"],
                                  "relief": {"extent": man["extent"], "crs": man["crs"], "cell_m": man["lods"]["regional"]["cell"],
                                             "base": {"depth_scale": man["base"]["depth_scale"], "style": man["base"]["style"]}}}
    allsys = systems.copy()
    allsys["frame"] = "europe"
    allsys = allsys[[c for c in KEEP if c in allsys.columns]]
    # source terrain by catchment centroid, in lon/lat
    g = gpd.read_parquet(EU / "systems.parquet")[["system", "geometry"]].to_crs(4326)
    cents = {str(sid): (c.x, c.y) for sid, c in zip(g["system"].astype(str), g.geometry.representative_point())}
    allsys["terrain"] = [terrain_of(*cents.get(str(sid), (None, None))) for sid in allsys["system"]]
    comp = allsys.groupby("terrain").apply(lambda d: pd.Series({
        "n": len(d), "area_km2": d["area_km2"].sum(), "qs_mt_yr": d["qs_mt_yr"].sum(), "sand_supply_mt_yr": d["sand_supply_mt_yr"].sum(),
        "sand_share": d["sand_supply_mt_yr"].sum() / max(d["qs_mt_yr"].sum(), 1e-9),
        "yield_median": d["yield_t_km2_yr"].median(), "quality_area_weighted": (d["sand_quality"] * d["area_km2"]).sum() / d["area_km2"].sum(),
        "shield_share": ((d["frac_igneous_felsic"] + d["frac_gneiss_quartzite"]) * d["area_km2"]).sum() / d["area_km2"].sum(),
        "clastic_share": (d["frac_clastic"] * d["area_km2"]).sum() / d["area_km2"].sum(),
        "carbonate_share": (d["frac_carbonate"] * d["area_km2"]).sum() / d["area_km2"].sum(),
        "cover_share": (d["frac_unconsolidated"] * d["area_km2"]).sum() / d["area_km2"].sum(),
        "mud_share": (d["grain_clastic_mud"] * d["area_km2"]).sum() / d["area_km2"].sum(),
        "mixed_share": ((d["grain_clastic_mixed"] + d["grain_clastic_mixed_sand"] + d["grain_clastic_mixed_mud"]) * d["area_km2"]).sum() / d["area_km2"].sum(),
        "sand_led_share": (d["grain_clastic_mixed_sand"] * d["area_km2"]).sum() / d["area_km2"].sum(),
        "mud_led_share": (d["grain_clastic_mixed_mud"] * d["area_km2"]).sum() / d["area_km2"].sum(),
        "schist_share": (d["frac_schist"] * d["area_km2"]).sum() / d["area_km2"].sum(),
        "mafic_share": (d["frac_igneous_mafic"] * d["area_km2"]).sum() / d["area_km2"].sum(),
    })).reset_index()
    comp.to_csv(OUT / "compare.csv", index=False)
    allsys.to_csv(OUT / "catchments.csv", index=False)
    # tidy tables for the built-in charts
    big = allsys[allsys["kind"] == "system"].sort_values("area_km2", ascending=False).head(12)
    parts = {"frac_igneous_felsic": "granite and felsic volcanics", "frac_gneiss_quartzite": "gneiss and quartzite", "frac_schist": "schist and phyllite",
             "frac_igneous_mafic": "mafic and metavolcanic", "frac_clastic": "clastic sedimentary", "frac_carbonate": "carbonate", "frac_unconsolidated": "unconsolidated cover", "frac_other": "not classified"}
    wide = big.head(8)[["name"] + list(parts)].rename(columns={"name": "catchment"}).copy()  # eight rows read on a phone
    wide["total"] = wide[list(parts)].sum(axis=1)
    wide.to_csv(OUT / "composition.csv", index=False)  # one column per class: SubScout's bars stack the listed part columns
    bud = big[["name", "qs_mt_yr", "qs_cal_mt_yr", "sand_supply_mt_yr", "yield_t_km2_yr", "sand_quality", "glauconite_prone_shelf", "frame", "area_km2"]].rename(columns={"name": "catchment"})
    bud.to_csv(OUT / "budget.csv", index=False)
    (OUT / "frames.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"{len(allsys)} catchments, {len(big)} in the charts; terrains {allsys['terrain'].value_counts().to_dict()}; files:", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
