---
title: Sand from the Source
short_title: Sand from the Source
dek: Every sandstone in a basin was once a hillside. Today's rivers around the North Sea show what the hillsides supply, how much, and how clean.
kicker: NORTH SEA · NORWEGIAN SEA · PRESENT-DAY CATCHMENTS
byline: Adam McCarthy
date: 2026-11-10
arc: scqa
register: section
palette: tide
surface: nordic-cool
units: sm3
horizon: true
kpis:
  - { metric: n_catchments, label: catchments on two margins }
  - { metric: qs_total, label: "Mt of sediment a year, estimated", filter: round:0 }
  - { metric: sand_share, label: of it from sand-prone rock, filter: pct }
  - { metric: median_yield, label: "t per km² a year, the typical yield", filter: round:0 }
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
    note: "Bedrock shares from the national geological surveys' open maps (NGU under NLOD 2.0, SGU open geodata, GTK open licence, BGS and GSNI under the Open Government Licence, GSI under CC BY 4.0; the IGME 5000 of the BGR, cited, where no national map covers the ground), read into one vocabulary; sediment flux by the BQART relation of Syvitski and Milliman (2007); terrain from Relief (Copernicus DEM GLO-90 by ESA and EMODnet Bathymetry; climate zones from Beck and others 2023, CC BY 4.0)."
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
  frames: data/frames.json
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
grains it carries; its size, relief and climate set how much. Around the North Sea the rivers are small and the
rock is old and hard, and that is the point: the margin is a slow, clean supplier, and has been for long stretches
of its past. This story measures today's catchments on two margins, reads what they are made of, estimates what
they deliver, and says where today stops standing for the past.

## Two shores and the water between

::: step {beat=situation layout=wide}
### The catchments of two margins

Each dashed area is one HydroSHEDS catchment: {{ n_systems }} whole river systems and the rest coastal groups,
{{ area_mkm2 | round:2 }} million km² in all. Ribbons are rivers, wider with more water; dots are mouths; colour is the
bedrock group.

```chart
id: basin
type: custom
module: figures/basin.js
data: [frames, north_sea_catchments, north_sea_rivers, north_sea_outlets, north_sea_land, north_sea_slope_flow, norwegian_sea_catchments, norwegian_sea_rivers, norwegian_sea_outlets, norwegian_sea_land, norwegian_sea_slope_flow]
state: { frame: north_sea, view: group, rivers: flow, shade: 0.9 }
title: Hard rock on both shores, small rivers between
subtitle: Present-day catchments and rivers on Relief terrain, coloured by bedrock group
source: hydrosheds
confidence: derived
unit: km² (catchments), m³/s (river width)
notes: Catchments are HydroBASINS level-6 sub-basins grouped into whole systems; a system under 4,000 km² is pooled with its coastal neighbours by Pfafstetter code. Groups are k-means on bedrock class and chart age shares, named from their means. Terrain and hillshade from Relief; catchment outlines dashed so the terrain reads through.
exception: { rule: one hue per entity, reason: the catchment colour carries the reading and the terrain beneath is context in grey }
```
:::

::: step {beat=situation}
Follow the fall lines instead: each thread is a path of steepest descent on the terrain, coloured by gradient.
Steep and short down the fjord walls, long and shallow across the lowlands. Rivers are where the threads gather.

```chart
use: basin
frame: north_sea
view: group
rivers: slope
title: The terrain says where the rivers must go
subtitle: Paths of steepest descent on Relief's terrain, coloured by gradient
```
:::

## The rock is old and hard

::: step {beat=complication}

North of Stad {{ nor_shield | pct }} of the catchment area is granite, felsic volcanics, gneiss or quartzite and
{{ nor_carbonate | pct }} carbonate. Britain drains Paleozoic clastic rock, much of it shale.

```chart
use: basin
frame: north_sea
view: group
rivers: off
title: Two shores, two kinds of source
subtitle: Catchments by bedrock group, rivers hidden
```
:::

::: step {beat=complication}
Grouped by what they erode, {{ n_groups }} kinds emerge: shield granite and gneiss, Caledonian schist, Paleozoic
clastic rock, young cover with carbonates, and glacial cover. The first two are the sand makers.

```chart
use: basin
frame: norwegian_sea
view: group
rivers: flow
title: North of Stad the shield takes over
subtitle: The Norwegian Sea margin, catchments by bedrock group
```
:::

```chart
id: comp
type: bars
data: composition
label: catchment
value: total
part: [frac_igneous_felsic, frac_gneiss_quartzite, frac_schist, frac_igneous_mafic, frac_clastic, frac_carbonate, frac_unconsolidated, frac_other]
parts_labels: [granite and felsic volcanics, gneiss and quartzite, schist and phyllite, mafic and metavolcanic, clastic sedimentary, carbonate, unconsolidated cover, not classified]
title: What the eight largest catchments erode
subtitle: Share of mapped bedrock area by harmonised class, largest river systems first
source: s2s
confidence: derived
unit: share of mapped area
notes: Shares are of the mapped area; national maps first, the IGME 5000 where none covers the ground. Classes are read from each survey's own lithology words.
```

## How much the rivers carry

::: step {beat=question}

By the BQART relation the two margins supply about {{ qs_total | round:0 }} Mt a year, or
{{ qs_cal_total | round:0 }} Mt scaled to gauged rivers. The Glomma: {{ glomma_qs | round:1 }} Mt against about
{{ glomma_known | round:1 }} measured.

```chart
use: basin
frame: north_sea
view: yield
rivers: off
title: Yield by catchment
subtitle: BQART sediment yield, t per km² a year, log scale
```
:::

::: step {beat=question}
The typical yield is {{ median_yield | round:0 }} t per km² a year; the Rhine alone delivers about
{{ rhine_monitored | cite:hoffmann }} Mt a year. These margins are starved: {{ glauconite_share | pct }} of the larger
catchments yield slowly enough for glaucony to form offshore.

```chart
use: basin
frame: north_sea
view: yield
rivers: flow
title: "Low almost everywhere"
subtitle: BQART sediment yield, t per km² a year, log scale
```
:::

```chart
id: budget
type: bars
data: budget
label: catchment
value: qs_mt_yr
title: A few megatonnes a year, spread thinly
subtitle: BQART sediment flux of the twelve largest catchments, Mt a year
source: s2s
confidence: derived
unit: Mt a year
notes: Relief is the catchment's highest point from Relief's 3 km elevation grid; discharge is the HydroRIVERS mouth reach; lithology on the paper's 0.5 to 2 scale; no glaciers; lake trapping guessed per climate zone. Monitored loads are modern and post-dam, so the natural flux lies between this column and the calibrated one.
```

## What reaches the shelf

::: step {beat=answer}
### The sand is clean and it arrives slowly

Quality read from the sources: quartz and feldspar rock scores high, schist, mafic rock and mud score low,
carbonate counts against. The proxy runs from {{ quality_median | round:2 }} typically to {{ quality_max | round:2 }}
at best, highest on the shield and the quartzite belts, lowest on cover and shale.

```chart
use: basin
frame: north_sea
view: quality
rivers: off
title: Where the sand is cleanest
subtitle: Sand quality proxy by catchment, from bedrock shares, grain words and climate
```
:::

::: step {beat=answer}
Sand supply is the flux times the sand-prone share: about {{ sand_total | round:0 }} Mt a year,
{{ sand_share | pct }} of the flux. A small number for two margins, and the one a Jurassic or Paleocene fan lived on,
scaled by the relief of its time.

```chart
use: basin
frame: north_sea
view: sand
rivers: flow
title: Sand supply by catchment
subtitle: BQART flux times the sand-prone share of the sources, Mt a year, log scale
```
:::

## Where today stops standing for the past

::: step {beat=support}
### Four breaks between the present and the basin's past

Ice: the fjords and till plains are glacial, and the last {{ 2.6 | param }} million years of sediment came from ice.
Relief: southern Norway stood at about {{ 1.6 | cite:somme }} km in the Late Jurassic, under {{ 0.5 | cite:somme }} km
in the Late Cretaceous and {{ 1.1 | cite:somme }} km in the Paleocene. Divides moved; Mesozoic cover has been stripped.

```chart
use: basin
frame: north_sea
view: group
rivers: slope
title: Today's relief, not the past's
subtitle: Fall lines on today's terrain; the Jurassic and Paleocene stood higher
```
:::

::: step {beat=support}
What survives is the bound: this ground cannot supply carbonate, gives quartz and feldspar sand with mica from
the nappes, and gives it slowly. That fits the margin's glauconitic, clean-sand Cretaceous and Paleocene shelves.

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
