"""Write the small public extracts for the story from the private sibling repos.

Reads source-to-sink/data/derived/<frame>/ (catchments with composition, budget and groups; rivers; slope flow; outlets),
Relief/data/out/<frame>/ (hillshade and the 0 m land band) and writes story/data/. Only frames whose geology sources
are open for public display are used (north_sea, norwegian_sea); see DATA-LICENCE.md. Everything written is derived
and generalised; no raw survey map is copied.
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
from PIL import Image
import shapely

ROOT = Path(__file__).resolve().parents[1]
S2S = ROOT.parent / "source-to-sink" / "data" / "derived"
RELIEF = ROOT.parent / "Relief" / "data" / "out"
OUT = ROOT / "story" / "data"
FRAMES = ["ne_europe", "north_sea", "norwegian_sea"]
KEEP = ["system", "name", "kind", "frame", "area_km2", "size_class", "cluster", "cluster_name", "mapped_frac", "composition_source",
        "sand_quality", "sand_share", "qs_mt_yr", "qs_cal_mt_yr", "sand_supply_mt_yr", "sand_cal_mt_yr", "yield_t_km2_yr", "relief_max_m",
        "temp_c", "q_km3_yr", "q_source", "lithology_factor", "glauconite_prone_shelf", "discharge_cms", "mainstem_km",
        "frac_igneous_felsic", "frac_igneous_mafic", "frac_gneiss_quartzite", "frac_schist", "frac_clastic", "frac_carbonate", "frac_unconsolidated", "frac_other",
        "age_Cenozoic", "age_Mesozoic", "age_Paleozoic", "age_Neoproterozoic", "age_Older_Proterozoic", "age_Archean", "age_unread",
        "grain_clastic_sand", "grain_clastic_mud", "grain_clastic_mixed"]


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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    frames = []
    manifest = {"frames": {}}
    for fr in FRAMES:
        d = S2S / fr
        lay = json.loads((d / "layers.json").read_text(encoding="utf-8"))
        s = pd.read_csv(d / "systems.csv")
        s["frame"] = fr
        frames.append(s)
        # catchments and rivers as published (TopoJSON in the frame CRS), outlets, slope flow thinned to one line in three
        sys_keep = ["system", "name", "kind", "area_km2", "log10_area", "size_class", "cluster", "cluster_name", "mapped_frac", "sand_quality",
                    "qs_mt_yr", "qs_cal_mt_yr", "sand_supply_mt_yr", "yield_t_km2_yr", "glauconite_prone_shelf", "discharge_cms"]
        (OUT / f"{fr}_catchments.geojson").write_text(json.dumps(topo_to_geojson(d / "systems.topojson", "systems", sys_keep), separators=(",", ":")), encoding="utf-8")
        (OUT / f"{fr}_rivers.geojson").write_text(json.dumps(topo_to_geojson(d / "rivers.topojson", "rivers", ["system", "log_discharge"]), separators=(",", ":")), encoding="utf-8")
        (OUT / f"{fr}_outlets.geojson").write_text((d / "outlets.geojson").read_text(encoding="utf-8"), encoding="utf-8")
        sf = json.loads((d / "slope_flow.geojson").read_text(encoding="utf-8"))
        sf["features"] = [f for i, f in enumerate(sf["features"]) if i % 3 == 0 and f["properties"]["cells"] >= 6]
        (OUT / f"{fr}_slope_flow.geojson").write_text(json.dumps(sf, separators=(",", ":")), encoding="utf-8")
        # Relief: the hillshade reduced to 1400 px wide and the 0 m land band, with the frame extent
        man = json.loads((RELIEF / fr / "manifest.json").read_text(encoding="utf-8"))
        im = Image.open(RELIEF / fr / "regional_hillshade.png").convert("L")
        im.thumbnail((1400, 1400))
        (ROOT / "story" / "figures").mkdir(exist_ok=True)
        im.save(ROOT / "story" / "figures" / f"{fr}_hillshade.png", optimize=True)  # beside basin.js, which is copied into the site
        bands = json.loads((RELIEF / fr / "regional.geojson").read_text(encoding="utf-8"))
        land = [f for f in bands["features"] if f["properties"]["kind"] == "land" and f["properties"]["level"] == 0]
        (OUT / f"{fr}_land.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": land}, separators=(",", ":")), encoding="utf-8")
        # the stacked sea bands too, so the page can colour the sea floor on Relief's depth scale
        sea = [f for f in bands["features"] if f["properties"]["kind"] == "sea"]
        (OUT / f"{fr}_sea.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": sea}, separators=(",", ":")), encoding="utf-8")
        manifest["frames"][fr] = {"name": lay["name"], "crs": lay["crs"], "extent": lay["extent"], "bbox": lay["bbox"], "sinks": lay.get("sinks", []),
                                  "clusters": lay["clusters"], "budget": lay["budget"], "checks": lay.get("checks", []), "built": lay["built"],
                                  "relief": {"extent": man["extent"], "crs": man["crs"], "cell_m": man["lods"]["regional"]["cell"]}}
    allsys = pd.concat(frames, ignore_index=True)
    allsys = allsys[[c for c in KEEP if c in allsys.columns]]
    # source terrain by catchment centroid: Britain and Ireland, Norway, Sweden and Finland, the continental lowlands
    cents = {}
    for fr in FRAMES:
        g = gpd.read_parquet(S2S / fr / "systems.parquet")[["system", "geometry"]].to_crs(4326)
        for sid, c in zip(g["system"].astype(str), g.geometry.centroid):
            cents.setdefault((fr, sid), (c.x, c.y))
    def terrain(row):
        lon, lat = cents.get((row["frame"], str(row["system"])), (None, None))
        name = str(row["name"])
        if lon is None:
            return "unplaced"
        if "outside the frame" in name or "Black Sea" in name or "Mediterranean" in name:
            return "Beyond the frame"
        if lon < 2.5 and 49.5 <= lat < 61.5:
            return "Britain and Ireland"
        if lat < 49.5 and lon < 8:
            return "France"
        # the Scandinavian divide runs north-east from Trøndelag: Norway lies west of it
        if lat >= 57.5 and lon < 12.5 or lat >= 63 and lon < 12 + (lat - 63) * 1.9:
            return "Norway"
        if lat >= 55.3 and 12.5 <= lon < 32 and (lat >= 60 or lon < 19.5):
            return "Sweden and Finland"
        return "Continental lowlands"
    allsys["terrain"] = allsys.apply(terrain, axis=1)
    # the same catchment can sit on two frames: keep one row per system for the tables, preferring the NE Europe frame
    allsys = allsys.sort_values("frame", key=lambda c: c.map({"ne_europe": 0, "north_sea": 1, "norwegian_sea": 2})).drop_duplicates("system")
    comp = allsys.groupby("terrain").apply(lambda d: pd.Series({
        "n": len(d), "area_km2": d["area_km2"].sum(), "qs_mt_yr": d["qs_mt_yr"].sum(), "sand_supply_mt_yr": d["sand_supply_mt_yr"].sum(),
        "sand_share": d["sand_supply_mt_yr"].sum() / max(d["qs_mt_yr"].sum(), 1e-9),
        "yield_median": d["yield_t_km2_yr"].median(), "quality_area_weighted": (d["sand_quality"] * d["area_km2"]).sum() / d["area_km2"].sum(),
        "shield_share": ((d["frac_igneous_felsic"] + d["frac_gneiss_quartzite"]) * d["area_km2"]).sum() / d["area_km2"].sum(),
        "clastic_share": (d["frac_clastic"] * d["area_km2"]).sum() / d["area_km2"].sum(),
        "carbonate_share": (d["frac_carbonate"] * d["area_km2"]).sum() / d["area_km2"].sum(),
        "cover_share": (d["frac_unconsolidated"] * d["area_km2"]).sum() / d["area_km2"].sum(),
        "mud_share": (d["grain_clastic_mud"] * d["area_km2"]).sum() / d["area_km2"].sum(),
        "mixed_share": (d["grain_clastic_mixed"] * d["area_km2"]).sum() / d["area_km2"].sum(),
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
