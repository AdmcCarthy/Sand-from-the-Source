# Sand from the Source

A SubScout data story about where North-east Europe's sand comes from today: the drainage catchments of Norway, Sweden and Finland, Britain and Ireland and the continental lowlands, what bedrock they erode, how much sediment they can deliver, how clean the sand should be, how the four terrains compare, and where the present day stops standing for the basins' past.

Live at https://admccarthy.github.io/Sand-from-the-Source/ once Pages has deployed.

## The argument

Reservoir sand is somebody's hillside. Around the North Sea there are three kinds: the Norwegian shield with its Caledonian nappes, the Paleozoic and Mesozoic layered rock of Britain and Ireland, and the glacial plains that drain to the southern North Sea and the Baltic. A BQART budget on today's catchments gives Norway and the flat shield the lowest yields and the cleanest sand-to-mud ratio, Britain the highest yield per square kilometre of the four and the most mud, and the lowlands the largest rivers. A quality proxy read from the sources puts Norway and Britain both low, for opposite reasons: the nappes' schist and mafic rock and a cold that delivers fresh feldspar on one side, interbedded sandstone and mudstone with carbonate on the other. Ice, relief, divides and exposure all differed in the past, so the present composition is a bound, not a reconstruction.

## Layout

- `story/story.md`: the narrative, every number a `{{ metric }}`.
- `story/story.py`: metrics with method, source and confidence; the per-terrain comparison table.
- `story/figures/basin.js`: the map, on Relief's landscape (2 : 1) regions for the North-east Europe, North Sea and Norwegian Sea frames, drawing one Europe-wide catchment set.
- `story/data/`: small extracts (CSV, GeoJSON) written by `scripts/make_extracts.py` from the private `source-to-sink` repo. `compare.csv` holds the per-terrain totals.
- `DATA-LICENCE.md`: the terms of every source and the attribution lines the page prints.

## Build

```
uv run --project ../SubScout subscout build story --out _site
python ../SubScout/scripts/readability.py _site
```

The extracts are rebuilt with `uv run --project ../source-to-sink python scripts/make_extracts.py` when the pipeline changes.
