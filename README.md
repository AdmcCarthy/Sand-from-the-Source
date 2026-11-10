# Sand from the Source

A SubScout data story about where the North Sea's sand comes from today: the drainage catchments of Norway, Sweden, Britain, Ireland and Denmark, what bedrock they erode, how much sediment they can deliver and how clean the sand should be, and where the present day stops standing for the basin's past.

Live page: https://admccarthy.github.io/Sand-from-the-Source/ (after the first Pages deploy).

## Thesis

Reservoir sand is somebody's hillside. Around the North Sea the hillsides are old, hard and carbonate-free, and the rivers are small: the margin is a slow, clean supplier of quartz and feldspar sand. A BQART budget on today's catchments puts the two margins at a few tens of megatonnes a year, with yields an order of magnitude below Alpine rivers, which is the frame in which the glauconitic, clean-sand shelves of the Cretaceous and Paleocene make sense. Ice, relief, divides and exposure all differed in the past, so the present composition is a bound, not a reconstruction.

## How it is built

- `scripts/make_extracts.py` writes the small public extracts in `story/data/` from the author's private pipelines (`europe-gis-data`, `geology-map-processing`, `source-to-sink`) and from Relief's terrain products. Only sources open for public display are used; see `DATA-LICENCE.md`.
- `story/story.md` is the narrative; `story/story.py` computes every number in it; `story/figures/basin.js` is the map on Relief terrain.
- Build: `uv run --project ../SubScout subscout build story --out _site`. GitHub Pages builds the same way from `.github/workflows/pages.yml`.

## Confidence

Observed: HydroSHEDS drainage, the surveys' maps, Relief terrain. Derived: bedrock shares, the BQART flux, the sand quality and sand share proxies, the groups. Interpreted: the glauconite reading and everything said about the past. The page's basis of analysis lists each figure's source and confidence.

Licence: MIT with Acknowledgement for the code and text (`LICENSE`); the data keeps its publishers' terms (`DATA-LICENCE.md`).
