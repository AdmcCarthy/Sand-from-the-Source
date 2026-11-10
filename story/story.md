---
title: Sand from the Source
short_title: Sand from the Source
dek: Every sandstone in a basin was once a hillside. Around the North Sea three kinds of hillside feed the basins today, and they do not supply the same sand.
kicker: NORTH-EAST EUROPE · BRITAIN, NORWAY AND THE LOWLANDS COMPARED
byline: Adam McCarthy
date: 2026-11-10
arc: scqa
register: section
palette: tide
surface: nordic-cool
units: sm3
horizon: true
kpis:
  - { metric: n_catchments, label: catchments on three frames }
  - { metric: qs_total, label: "Mt of sediment a year, estimated", filter: round:0 }
  - { metric: nor_quality, label: "sand quality proxy, Norway", filter: round:2 }
  - { metric: brit_quality, label: "sand quality proxy, Britain and Ireland", filter: round:2 }
sources:
  hydrosheds:
    name: HydroSHEDS, HydroBASINS and HydroRIVERS v1 (Lehner and Grill 2013)
    url: "https://www.hydrosheds.org"
    accessed: 2026-11-10
    note: "Lehner, B., Grill G. (2013): Global river hydrography and network routing: baseline data and new approaches to study the world's large river systems. Hydrological Processes 27(15). Catchments grouped and summarised by the author."
  s2s:
    name: source-to-sink, the author's catchment composition and budget pipeline
    url: "https://github.com/AdmcCarthy/source-to-sink"
    accessed: 2026-11-10
    note: "Bedrock shares from the national geological surveys' open maps (NGU under NLOD 2.0, SGU open geodata, GTK open licence, BGS and GSNI under the Open Government Licence, GSI under CC BY 4.0) and, where no open national map covers the ground, the IGME 5000 of the BGR (cited) and Poland's 1:1M map of the PIG, read into one vocabulary; sediment flux by the BQART relation of Syvitski and Milliman (2007); terrain from Relief (Copernicus DEM GLO-90 by ESA and EMODnet Bathymetry; climate zones from Beck and others 2023, CC BY 4.0)."
  hoffmann:
    name: Hoffmann and others (2023), suspended sediment in large German rivers, Earth Surface Dynamics 11
    url: "https://esurf.copernicus.org/articles/11/287/2023/"
    accessed: 2026-11-10
  somme:
    name: Sømme, Martinsen and Lunt (2013), Linking offshore stratigraphy to onshore paleotopography, GSA Bulletin 125
    url: "https://doi.org/10.1130/B30747.1"
    accessed: 2026-11-10
    note: "Palaeorelief of southern Norway estimated from the volume of point-sourced depocentres: about 1.6 km in the Late Jurassic, under 0.5 km in the Late Cretaceous, about 1.1 km in the north and 0.5 km in the south in the Paleocene."
data:
  catchments: data/catchments.csv
  composition: data/composition.csv
  budget: data/budget.csv
  compare: data/compare.csv
  frames: data/frames.json
  ne_europe_catchments: data/ne_europe_catchments.geojson
  ne_europe_rivers: data/ne_europe_rivers.geojson
  ne_europe_outlets: data/ne_europe_outlets.geojson
  ne_europe_land: data/ne_europe_land.geojson
  ne_europe_slope_flow: data/ne_europe_slope_flow.geojson
  north_sea_catchments: data/north_sea_catchments.geojson
  north_sea_rivers: data/north_sea_rivers.geojson
  north_sea_outlets: data/north_sea_outlets.geojson
  north_sea_land: data/north_sea_land.geojson
  north_sea_slope_flow: data/north_sea_slope_flow.geojson
  norwegian_sea_catchments: data/norwegian_sea_catchments.geojson
  norwegian_sea_rivers: data/norwegian_sea_rivers.geojson
  norwegian_sea_outlets: data/norwegian_sea_outlets.geojson
  norwegian_sea_land: data/norwegian_sea_land.geojson
  norwegian_sea_slope_flow: data/norwegian_sea_slope_flow.geojson
---

Reservoir sand is somebody's hillside, carried down a river and left on a shelf. The rocks a river drains set what
grains it carries; its size, relief and climate set how much. North-east Europe holds three kinds of hillside in
one frame: the Norwegian shield with its Caledonian nappes, the Paleozoic uplands and Mesozoic lowlands of Britain
and Ireland, and the glacial plains that drain to the southern North Sea and the Baltic. This story measures the
catchments of all three, reads what they are made of, estimates what they deliver, sets them side by side, and
says where today stops standing for the basins' past.

## One frame, three kinds of source

::: step {beat=situation layout=wide}
### The catchments of North-east Europe

Each dashed area is one HydroSHEDS catchment: {{ n_systems }} whole river systems and the rest coastal groups,
{{ area_mkm2 | round:2 }} million km² in all. Ribbons are rivers, wider with more water, over the fine fall lines of
the terrain; dots are mouths; colour is the bedrock group. The sea floor is on Relief's depth scale.

```chart
id: basin
type: custom
module: figures/basin.js
data: [frames, ne_europe_catchments, ne_europe_rivers, ne_europe_outlets, ne_europe_land, ne_europe_slope_flow, north_sea_catchments, north_sea_rivers, north_sea_outlets, north_sea_land, north_sea_slope_flow, norwegian_sea_catchments, norwegian_sea_rivers, norwegian_sea_outlets, norwegian_sea_land, norwegian_sea_slope_flow]
state: { frame: ne_europe, view: group, rivers: all, shade: 1.5, fold: 3 }
title: Shield, upland and plain feed the same seas
subtitle: Present-day catchments on Relief terrain, coloured by bedrock group; rivers as ribbons over the terrain's fall lines
source: hydrosheds
confidence: derived
unit: km² (catchments), m³/s (river width)
notes: Catchments are HydroBASINS level-6 sub-basins grouped into whole systems; a system under 4,000 km² is pooled with its coastal neighbours by Pfafstetter code; groups under 1,000 km² are hidden on the map but counted. Groups are k-means on bedrock class and chart age shares, named from their means. Terrain and hillshade from Relief; catchment outlines dashed so the terrain reads through.
exception: { rule: one hue per entity, reason: the catchment colour carries the reading and the terrain beneath is context in grey }
```
:::

::: step {beat=situation}
Follow the fall lines instead: each thread is a path of steepest descent on the terrain, coloured by gradient.
Steep and short down the fjord walls, shallow across the plains. Rivers are where the threads gather.

```chart
use: basin
frame: ne_europe
view: group
rivers: slope
title: The terrain says where the rivers must go
subtitle: Paths of steepest descent on Relief's terrain, coloured by gradient
```
:::

## Three hillsides

::: step {beat=complication}
### Hard rock north, layered rock west, cover south

Norway's {{ nor_n }} catchments are {{ nor_shield | pct }} granite, felsic volcanics, gneiss and quartzite by area,
with {{ nor_carbonate | pct }} carbonate. Sweden and Finland's {{ swe_n }} are the same shield lying flat:
{{ swe_shield | pct }} crystalline rock under {{ swe_cover | pct }} glacial cover.

Britain and Ireland's {{ brit_n }} are different ground: {{ brit_clastic | pct }} clastic rock, {{ brit_mud | pct }}
of their area shale and mudstone, with {{ brit_carbonate | pct }} carbonate, the highest share of the four.

```chart
use: basin
frame: ne_europe
view: group
rivers: off
title: Four kinds of ground
subtitle: Catchments by bedrock group, rivers hidden
```
:::

::: step {beat=complication}
The {{ low_n }} lowland catchments draining to the southern North Sea and the Baltic are {{ low_cover | pct }}
glacial cover with {{ low_clastic | pct }} clastic rock showing through. Their rivers are the region's largest; their
sources are the softest and the muddiest.

```chart
use: basin
frame: ne_europe
view: size
rivers: flow
title: The lowland rivers are the big ones
subtitle: Catchments by size class, log scale
```
:::

```chart
id: rock
type: bars
data: compare_t
label: terrain
value: total_pct
part: [shield_pct, clastic_pct, carbonate_pct, cover_pct, other_pct]
parts_labels: [granite and gneiss, clastic sedimentary, carbonate, unconsolidated cover, other rock]
title: What each terrain is made of
subtitle: Share of mapped catchment area by harmonised bedrock class, per cent
source: s2s
confidence: derived
unit: per cent of mapped area
notes: Catchments are placed in a terrain by centroid; France and the catchments whose mouths lie beyond the frame (Danube, Dnieper, Rhône) are left out. Shares are area-weighted over the catchments; national maps first, the IGME 5000 and the PIG map where none covers the ground. Other rock is schist, mafic and unclassified units.
```

## How much each terrain carries

::: step {beat=question}
By the BQART relation the catchments together supply about {{ qs_total | round:0 }} Mt a year, or
{{ qs_cal_total | round:0 }} Mt scaled to gauged rivers. The median catchment in Norway yields
{{ nor_yield | round:0 }} t per km² a year, in Britain and Ireland {{ brit_yield | round:0 }}, in the lowlands
{{ low_yield | round:0 }}.

```chart
use: basin
frame: ne_europe
view: yield
rivers: off
title: Yield by catchment
subtitle: BQART sediment yield, t per km² a year, log scale
```
:::

::: step {beat=question}
The Rhine within the frame comes out at {{ rhine_qs | round:1 }} Mt a year against about
{{ rhine_monitored | cite:hoffmann }} measured at the Dutch border, {{ rhine_ratio | round:0 }} times too high: the
storage in Lake Constance and the floodplains that the relation does not carry. The Glomma, with no such traps, comes
out at {{ glomma_qs | round:1 }} against about {{ glomma_known | round:1 }}.

```chart
use: basin
frame: ne_europe
view: sand
rivers: flow
title: Sand supply by catchment
subtitle: BQART flux times the sand-prone share of the sources, Mt a year, log scale
```
:::

```chart
id: yields
type: bars
data: compare_t
label: terrain
value: yield_median
title: Sweden and Finland yield least, Britain most
subtitle: Median BQART sediment yield by source terrain, t per km² a year
source: s2s
confidence: derived
unit: t per km² a year
notes: BQART with Relief's relief, HydroRIVERS discharge, one mean temperature per climate zone and the paper's lithology factor; no reservoir trapping beyond a zone guess, so lowland rivers run high against gauges. The Swedish and Finnish median is low because the shield there is flat and cold.
```

## What reaches the shelf

::: step {beat=answer}
### Norway and Britain both score low, for opposite reasons

The quality proxy puts Sweden and Finland at {{ swe_quality | round:2 }} and the lowlands at
{{ low_quality | round:2 }}, Britain and Ireland at {{ brit_quality | round:2 }} and Norway at
{{ nor_quality | round:2 }}. Quartz-rich sources count for it; schist, mafic rock, mud and carbonate count against;
a cool climate keeps feldspar fresh.

```chart
use: basin
frame: ne_europe
view: quality
rivers: off
title: Where the sand is cleanest
subtitle: Sand quality proxy by catchment, from bedrock shares, grain words and climate
```
:::

::: step {beat=answer}
Norway loses marks for the nappes, {{ nor_schist | pct }} schist and {{ nor_mafic | pct }} mafic rock, and for
weather that delivers its granite as fresh feldspar: arkose, not quartz arenite. Britain loses them for carbonate and
for clastic rock mapped as sandstone with mudstone, {{ brit_mixed | pct }} of its area.

```chart
use: basin
frame: north_sea
view: quality
rivers: flow
title: Norway and Britain face to face across the North Sea
subtitle: Sand quality proxy on the North Sea frame
```
:::

::: step {beat=answer}
Sand as a share of the flux reverses the order: {{ nor_sand_share | pct }} from Norway, {{ swe_sand_share | pct }}
from Sweden and Finland, {{ low_sand_share | pct }} from the lowlands, {{ brit_sand_share | pct }} from Britain and
Ireland. Norway sends sand with little mud, and little of it; Britain sends the most mud with its sand.

```chart
use: basin
frame: ne_europe
view: sand
rivers: off
title: Sand supply, sources only
subtitle: BQART flux times the sand-prone share of the sources, Mt a year, log scale
```
:::

```chart
id: quality_bars
type: bars
data: compare_t
label: terrain
value: quality_pct
title: The flat shield scores highest, the nappes and the shale lowest
subtitle: Area-weighted sand quality proxy by source terrain, per cent
source: s2s
confidence: derived
unit: per cent
notes: The proxy is a recipe on bedrock shares, grain words and climate (quartz-rich sources count for; ductile, mud and carbonate sources against; cold climates keep feldspar fresh). It is not a measured mineralogy. France and the catchments whose mouths lie beyond the frame are listed in the table but left out of the comparison.
```

## Where today stops standing for the past

::: step {beat=support}
Ice: the fjords and till plains are glacial, and the last {{ 2.6 | param }} million years of sediment came from ice.
Relief: southern Norway stood at about {{ 1.6 | cite:somme }} km in the Late Jurassic, under {{ 0.5 | cite:somme }} km
in the Late Cretaceous and {{ 1.1 | cite:somme }} km in the Paleocene. Divides moved; Mesozoic cover has been stripped.

```chart
use: basin
frame: norwegian_sea
view: group
rivers: slope
title: Today's relief, not the past's
subtitle: Fall lines on today's terrain; the Jurassic and Paleocene stood higher
```
:::

::: step {beat=support}
What survives is the bound. Norway's ground cannot supply carbonate; it gives feldspar and quartz sand with mica
from the nappes, slowly, and under a warmer climate the feldspar would have weathered to cleaner quartz. Britain's
gives recycled quartz with shale and carbonate; the plains give mud. That fits the glauconitic, clean-sand
Cretaceous and Paleocene shelves facing Norway and the muddier fills to the south.

```chart
use: basin
frame: norwegian_sea
view: quality
rivers: flow
title: The bound that survives the breaks
subtitle: Sand quality proxy on the Norwegian Sea margin
```
:::

```table
kind: league
data: catchments
columns:
  - { field: name, label: Catchment }
  - { field: terrain, label: Terrain }
  - { field: area_km2, label: Area, unit: km², bar: true, format: int }
  - { field: cluster_name, label: Bedrock group }
  - { field: sand_quality, label: Sand quality proxy, format: round:2 }
  - { field: qs_mt_yr, label: Flux, unit: Mt a year, format: round:2 }
  - { field: sand_supply_mt_yr, label: Sand supply, unit: Mt a year, format: round:2 }
  - { field: yield_t_km2_yr, label: Yield, unit: t per km² a year, format: int }
sort: -area_km2
fold: 10
title: The catchments, with their readings
source: s2s
confidence: derived
```

The table lists every catchment with its readings; the page's basis of analysis gives each figure's source and confidence.
