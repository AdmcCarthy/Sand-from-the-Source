"""Write the small public extracts for the story from the private sibling repos.

Reads source-to-sink/data/derived/<frame>/ (catchments with composition, budget and groups; rivers; slope flow; outlets),
Relief/data/out/<frame>/ (hillshade and the 0 m land band) and writes story/data/. Only frames whose geology sources
are open for public display are used (north_sea, norwegian_sea); see DATA-LICENCE.md. Everything written is derived
and generalised; no raw survey map is copied.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
S2S = ROOT.parent / "source-to-sink" / "data" / "derived"
RELIEF = ROOT.parent / "Relief" / "data" / "out"
OUT = ROOT / "story" / "data"
FRAMES = ["north_sea", "norwegian_sea"]
KEEP = ["system", "name", "kind", "frame", "area_km2", "size_class", "cluster", "cluster_name", "mapped_frac", "composition_source",
        "sand_quality", "sand_share", "qs_mt_yr", "qs_cal_mt_yr", "sand_supply_mt_yr", "sand_cal_mt_yr", "yield_t_km2_yr", "relief_max_m",
        "temp_c", "q_km3_yr", "q_source", "lithology_factor", "glauconite_prone_shelf", "discharge_cms", "mainstem_km",
        "frac_igneous_felsic", "frac_igneous_mafic", "frac_gneiss_quartzite", "frac_schist", "frac_clastic", "frac_carbonate", "frac_unconsolidated", "frac_other",
        "age_Cenozoic", "age_Mesozoic", "age_Paleozoic", "age_Neoproterozoic", "age_Older_Proterozoic", "age_Archean", "age_unread",
        "grain_clastic_sand", "grain_clastic_mud", "grain_clastic_mixed"]


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
        for src, dst in (("systems.topojson", f"{fr}_catchments.json"), ("rivers.topojson", f"{fr}_rivers.json"), ("outlets.geojson", f"{fr}_outlets.geojson")):
            (OUT / dst).write_text((d / src).read_text(encoding="utf-8"), encoding="utf-8")
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
        manifest["frames"][fr] = {"name": lay["name"], "crs": lay["crs"], "extent": lay["extent"], "bbox": lay["bbox"], "sinks": lay.get("sinks", []),
                                  "clusters": lay["clusters"], "budget": lay["budget"], "checks": lay.get("checks", []), "built": lay["built"],
                                  "relief": {"extent": man["extent"], "crs": man["crs"], "cell_m": man["lods"]["regional"]["cell"]}}
    allsys = pd.concat(frames, ignore_index=True)
    allsys = allsys[[c for c in KEEP if c in allsys.columns]]
    allsys.to_csv(OUT / "catchments.csv", index=False)
    # tidy tables for the built-in charts
    big = allsys[allsys["kind"] == "system"].sort_values("area_km2", ascending=False).head(18)
    parts = {"frac_igneous_felsic": "granite and felsic volcanics", "frac_gneiss_quartzite": "gneiss and quartzite", "frac_schist": "schist and phyllite",
             "frac_igneous_mafic": "mafic and metavolcanic", "frac_clastic": "clastic sedimentary", "frac_carbonate": "carbonate", "frac_unconsolidated": "unconsolidated cover", "frac_other": "not classified"}
    rows = [{"catchment": r["name"], "part": label, "share": float(r[col])} for _, r in big.iterrows() for col, label in parts.items()]
    pd.DataFrame(rows).to_csv(OUT / "composition.csv", index=False)
    bud = big[["name", "qs_mt_yr", "qs_cal_mt_yr", "sand_supply_mt_yr", "yield_t_km2_yr", "sand_quality", "glauconite_prone_shelf", "frame", "area_km2"]].rename(columns={"name": "catchment"})
    bud.to_csv(OUT / "budget.csv", index=False)
    (OUT / "frames.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"{len(allsys)} catchments, {len(big)} in the charts; files:", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
