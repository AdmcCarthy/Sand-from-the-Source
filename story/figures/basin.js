// North-east Europe and its margins as source-to-sink frames: Relief hillshade, the land, catchments coloured by one of
// several readings (composition group, sand quality, yield, sand supply, size), flow lines as tapered ribbons by discharge, outlets.
// Coordinates are the frame CRS in metres (d3.geoIdentity, y reflected). Hillshade and land come with the figure;
// the catchments, rivers and outlets are the story's datasets.
import { token, onSchemeChange } from "../runtime/js/subscout.js";

const GROUP_COLOURS = ["#c8553d", "#3d6e9e", "#7a9a3b", "#b8860b", "#6b4c9a", "#2e8b8b", "#a0522d", "#5f5f5f"];

// Relief's shelf depth ramp (0 to 1,300 m, linear; copied from Relief/preview/palette.js, Detuned style). The stacked sea bands
// are coloured at their midpoints, so the sea floor reads on Relief's own scale and the key can show it.
const SEA_STOPS = [0, 20, 50, 100, 200, 500, 1000], SEA_MAX = 1300;
const SEA = { light: ["#e8f0f2", "#cfe1e6", "#aacdd8", "#7eb0c5", "#5891ae", "#3a6d94", "#264b73", "#162b50"], dark: ["#3a8aa2", "#2f7690", "#25647d", "#1c526b", "#144157", "#0e3045", "#092336", "#06172a"] };
function seaColour(metres, dark) {
  const cols = SEA[dark ? "dark" : "light"], stops = SEA_STOPS.map((b, i) => [b / SEA_MAX, cols[i]]).concat([[1, cols.at(-1)]]);
  let t = Math.min(1, Math.max(0, metres / SEA_MAX)), k = 0; while (k < stops.length - 2 && t > stops[k + 1][0]) k++;
  const [t0, c0] = stops[k], [t1, c1] = stops[k + 1]; return d3.interpolateRgb(c0, c1)(Math.min(1, Math.max(0, (t - t0) / (t1 - t0 || 1))));
}
const OCEAN_STOPS = [0, 200, 1000, 2000, 3000, 4000, 5000, 6000, 7000], OCEAN_MAX = 7000;
const OCEAN = { light: ["#e2f4f9", "#bfe2ed", "#83bddc", "#5c9acd", "#4579ba", "#355a9f", "#2a3e80", "#1e2763", "#131546"], dark: ["#71b7c8", "#56a5bd", "#2c83aa", "#1d679c", "#154b8a", "#113375", "#101e5c", "#0a0b42", "#040027"] };
function depthColour(kind, metres, dark) {
  const cols = (kind === "ocean" ? OCEAN : SEA)[dark ? "dark" : "light"], br = kind === "ocean" ? OCEAN_STOPS : SEA_STOPS, max = kind === "ocean" ? OCEAN_MAX : SEA_MAX;
  const stops = br.map((b, i) => [b / max, cols[i]]); if (cols.length > br.length) stops.push([1, cols.at(-1)]);
  let t = Math.min(1, Math.max(0, metres / max)), k = 0; while (k < stops.length - 2 && t > stops[k + 1][0]) k++;
  const [t0, c0] = stops[k], [t1, c1] = stops[k + 1]; return d3.interpolateRgb(c0, c1)(Math.min(1, Math.max(0, (t - t0) / (t1 - t0 || 1))));
}
// palette.js `tune`: saturation towards the colour's own grey, then lifted (mix > 0) or sunk
function tune(h, sat, mix) { const c = d3.rgb(h), y = 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b, t = mix > 0 ? 255 : 0, m = Math.abs(mix); const f = (v) => { const g = y + (v - y) * sat; return g + (t - g) * m; }; return d3.rgb(f(c.r), f(c.g), f(c.b)).formatHex(); }
// the water family: flat ground in a detuned river blue, steep in a saturated indigo; ribbons take the flat tone, threads the ramp
const SHAPE_FLAT = { light: "#7f9fb4", dark: "#7fa3b8" }, SHAPE_STEEP = { light: "#3a1f9c", dark: "#b08cff" };
const shapeRampFor = (dark) => d3.scaleSequential(d3.interpolateHcl(SHAPE_FLAT[dark ? "dark" : "light"], SHAPE_STEEP[dark ? "dark" : "light"])).domain([0, 0.08]);

// Relief's hillshade PNG is light (flat ground sits near 180 of 255), and soft-light is neutral at mid grey, so drawn as it
// comes it barely shows. Flat ground is moved to mid grey and the slopes stretched before the shade is composited.
function toneHill(img, flat = 180, gain = 2.5) {
  const c = document.createElement("canvas"); c.width = img.width; c.height = img.height;
  const x = c.getContext("2d"); x.drawImage(img, 0, 0);
  const d = x.getImageData(0, 0, c.width, c.height), p = d.data;
  for (let i = 0; i < p.length; i += 4) { const v = Math.max(0, Math.min(255, 128 + (p[i] - flat) * gain)); p[i] = p[i + 1] = p[i + 2] = v; }
  x.putImageData(d, 0, 0); return c;
}

export default function basin(el, datasets, opts = {}) {
  const frames = datasets.frames.frames;
  const canvas = d3.select(el).selectAll("canvas").data([0]).join("canvas").attr("role", "img")
    .attr("aria-label", "Map of catchments, flow lines and outlets on terrain, coloured by the chosen reading").node();
  const ctx = canvas.getContext("2d");
  const cache = {};
  let last = null;

  async function load(frame) {
    if (cache[frame]) return cache[frame];
    const systems = datasets[`${frame}_catchments`].features;
    const rivers = datasets[`${frame}_rivers`].features;
    const outlets = datasets[`${frame}_outlets`].features;
    const land = datasets[`${frame}_land`].features;
    const slope = datasets[`${frame}_slope_flow`] ? datasets[`${frame}_slope_flow`].features : [];
    // Relief's hillshade and its base map in both themes (linear bathymetry, stepped climate-tinted land; Relief/docs/base-maps.md)
    const load1 = async (name) => { const im = new Image(); im.src = new URL(name, import.meta.url).href; await new Promise((res) => { im.onload = res; im.onerror = res; }); return im.width ? im : null; };
    const img = await load1(`${frame}_hillshade.png`);
    const base = { light: await load1(`${frame}_base_light.png`), dark: await load1(`${frame}_base_dark.png`) };
    return (cache[frame] = { systems, rivers, outlets, land, slope, base, img: img ? toneHill(img) : null, meta: frames[frame] });
  }

  const alpha = (hex, a) => { const c = d3.color(hex); if (!c) return hex; c.opacity = a; return c.formatRgb(); };
  const qualRamp = d3.scaleSequential(d3.interpolateYlGnBu).domain([0.1, 0.6]);
  const yieldRamp = d3.scaleSequential(d3.interpolateYlOrBr).domain([0.5, 3]);
  const gradRamp = d3.scaleSequential(d3.interpolateViridis).domain([0, 0.08]);
  const sizeRamp = d3.scaleSequential(d3.interpolatePuBuGn).domain([3, 6]);

  function fillOf(p, view, dark) {
    if (p.mapped_frac == null || p.mapped_frac < 0.5) return dark ? "rgba(90,96,106,.5)" : "rgba(200,203,208,.55)";
    if (view === "group") return p.cluster >= 0 ? GROUP_COLOURS[p.cluster % GROUP_COLOURS.length] : "#bbb";
    if (view === "quality") return qualRamp(p.sand_quality ?? 0);
    if (view === "yield") return yieldRamp(Math.log10(Math.max(1, p.yield_t_km2_yr ?? 1)));
    if (view === "sand") return yieldRamp(Math.log10(Math.max(0.001, p.sand_supply_mt_yr ?? 0.001)) + 2);
    if (view === "size") return sizeRamp(p.log10_area ?? 3);
    return null;
  }

  async function draw(width, state = {}) {
    last = [width, state];
    const frame = state.frame || "north_sea", view = state.view || "group", rivers = state.rivers || "flow", shade = state.shade ?? 0.9;
    const D = await load(frame);
    // "Auto" leaves the attribute unset, so the system preference decides
    const cs = document.documentElement.dataset.colourScheme, dark = cs ? cs === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    const [x0, y0, x1, y1] = D.meta.relief.extent;
    const aspect = (y1 - y0) / (x1 - x0);
    // on wide screens the legend sits in a strip under the map so it never covers data; phones keep it over the map corner
    const strip = width >= 760, LH = strip ? legendHeight(view, rivers, D) : 0;
    const H = opts.height ? opts.height() : Math.round(Math.min(width * aspect + LH, window.innerHeight * (width < 600 ? 0.36 : opts.vhShare ?? 0.62)));
    const MH = H - LH;
    const dpr = opts.pixelRatio || window.devicePixelRatio || 1;
    canvas.width = width * dpr; canvas.height = H * dpr; canvas.style.width = width + "px"; canvas.style.height = H + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const proj = d3.geoIdentity().reflectY(true).fitExtent([[0, 0], [width, MH]], { type: "Polygon", coordinates: [[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]] });
    const path = d3.geoPath(proj, ctx);
    const [px0, py1] = proj([x0, y0]), [px1, py0] = proj([x1, y1]);
    ctx.fillStyle = token("surface") || (dark ? "#1b2230" : "#eef1f4"); ctx.fillRect(0, 0, width, H);
    ctx.save(); ctx.beginPath(); ctx.rect(px0, py0, px1 - px0, py1 - py0); ctx.clip();
    // Relief's base map under everything, lightened a little on land so the catchment colours carry; a flat wash if a frame has none
    const baseImg = D.base[dark ? "dark" : "light"];
    if (baseImg) { ctx.drawImage(baseImg, px0, py0, px1 - px0, py1 - py0); ctx.beginPath(); for (const f of D.land) path(f); ctx.fillStyle = dark ? "rgba(0,0,0,.15)" : "rgba(255,255,255,.3)"; ctx.fill(); }
    else { ctx.fillStyle = dark ? "rgba(24,38,58,.6)" : "rgba(170,196,222,.45)"; ctx.fillRect(px0, py0, px1 - px0, py1 - py0); ctx.beginPath(); for (const f of D.land) path(f); ctx.fillStyle = dark ? "rgba(255,255,255,.07)" : "rgba(255,255,255,.55)"; ctx.fill(); }
    // catchments
    const shown = D.systems.filter((f) => (f.properties.log10_area ?? 9) >= (state.fold ?? 0));
    for (const f of shown) { const c = fillOf(f.properties, view, dark); if (!c) continue; ctx.beginPath(); path(f); ctx.fillStyle = alpha(c, dark ? 0.6 : 0.55); ctx.fill(); }
    // catchment divides as solid black lines (near-white on the dark scheme), firm enough to hold against the terrain
    ctx.save(); ctx.beginPath(); for (const f of shown) path(f); ctx.strokeStyle = dark ? "rgba(255,255,255,.75)" : "rgba(0,0,0,.85)"; ctx.lineWidth = 1.3; ctx.lineJoin = "round"; ctx.stroke(); ctx.restore();
    // the hillshade sits above the fills and outlines so the terrain reads through the data; soft-light once, and above
    // strength 1 a second pass with a light multiply so ridges bite without muddying the colours
    if (D.img && shade > 0) { ctx.save(); ctx.globalCompositeOperation = "soft-light"; ctx.globalAlpha = Math.min(1, shade); ctx.drawImage(D.img, px0, py0, px1 - px0, py1 - py0); if (shade > 1) { ctx.drawImage(D.img, px0, py0, px1 - px0, py1 - py0); ctx.globalCompositeOperation = "multiply"; ctx.globalAlpha = (shade - 1) * 0.6; ctx.drawImage(D.img, px0, py0, px1 - px0, py1 - py0); } ctx.restore(); }
    // water
    ctx.lineCap = "round"; ctx.lineJoin = "round";
    // "all" is the catchment-shape view: the rivers as muted ribbons, and over them the terrain's fall lines in the saturated
    // end of the same colour family, so the two read as one drawing of how each catchment drains
    const combined = rivers === "all", shapeRamp = shapeRampFor(dark);
    if (rivers !== "off" && rivers !== "slope") {
      const sysOf = new Map(shown.map((f) => [f.properties.system, f.properties]));
      const byQ = D.rivers.filter((f) => !state.fold || sysOf.has(f.properties.system)).sort((a, b) => (a.properties.log_discharge ?? 0) - (b.properties.log_discharge ?? 0));
      for (const pass of ["glow", "core"]) for (const f of byQ) {
        const q = Math.max(0, f.properties.log_discharge ?? 0), s = sysOf.get(f.properties.system);
        let col = view === "group" && s && s.cluster >= 0 ? GROUP_COLOURS[s.cluster % GROUP_COLOURS.length] : (dark ? "#a8d0ff" : "#1f5a8f");
        if (combined) col = view === "group" && s && s.cluster >= 0 ? tune(col, 0.35, dark ? -0.05 : 0.08) : SHAPE_FLAT[dark ? "dark" : "light"];
        ctx.beginPath(); path(f);
        if (pass === "glow") { ctx.strokeStyle = alpha(col, combined ? 0.1 : 0.16); ctx.lineWidth = 2 + 2.4 * q; } else { ctx.strokeStyle = alpha(col, combined ? 0.6 : 0.9); ctx.lineWidth = 0.35 + 1.2 * q; }
        ctx.stroke();
      }
    }
    if (rivers === "slope" || combined) {
      for (const f of D.slope) { ctx.beginPath(); path(f); ctx.strokeStyle = alpha(shapeRamp(f.properties.mean_gradient), combined ? 0.9 : 0.85); ctx.lineWidth = combined ? 0.6 : 0.6; ctx.stroke(); }
    }
    for (const f of D.outlets) { const [x, y] = proj(f.geometry.coordinates); const r = Math.max(1.5, Math.sqrt(f.properties.discharge_cms || 1) / 7); ctx.beginPath(); ctx.arc(x, y, r, 0, 2 * Math.PI); ctx.fillStyle = dark ? "rgba(255,255,255,.85)" : "rgba(20,30,50,.85)"; ctx.fill(); }
    // sink names and a frame rule
    ctx.font = "italic 12px Georgia, serif"; ctx.fillStyle = dark ? "rgba(230,235,240,.8)" : "rgba(40,50,60,.8)";
    const toXY = lonlat(D.meta.crs);
    for (const s of D.meta.sinks || []) { if (!toXY) break; const p = proj(toXY(s.lon, s.lat)); ctx.fillText(s.name, p[0], p[1]); }
    ctx.restore();
    ctx.strokeStyle = dark ? "rgba(255,255,255,.2)" : "rgba(0,0,0,.2)"; ctx.lineWidth = 1; ctx.strokeRect(px0, py0, px1 - px0, py1 - py0);
    legend(view, rivers, D, dark, H, strip ? LH : 0);
  }

  // Legend, bottom left: swatches for groups, and for every ramp a bar with ticks at the values that matter (log scales are
  // labelled in their own units), plus Relief's depth key when the frame has sea bands.
  // Height of the legend strip: the tallest block (group swatches, or a bar with its title and ticks) plus a margin.
  // Catchments with under half their area mapped are drawn grey, so the group key says so when any are on the map.
  const unmapped = (D) => D.systems.some((f) => f.properties.mapped_frac == null || f.properties.mapped_frac < 0.5);

  function legendHeight(view, rivers, D) {
    const nGroups = view === "group" ? Object.keys(D.meta.clusters).length + (unmapped(D) ? 1 : 0) : 0;
    return Math.max(nGroups * 15, 40) + 18;
  }

  function legend(view, rivers, D, dark, H, LH = 0) {
    ctx.save(); ctx.font = "11px system-ui, sans-serif"; let x = 12; const ink = dark ? "#e6e9ee" : "#26323d", muted = dark ? "rgba(230,233,238,.75)" : "rgba(38,50,61,.75)"; let y = H - 12;
    const BW = 210, BH = 11, bottom = y, gap = 28;
    // strip mode: each block is a column of its own along the bottom; the cursor `x` moves right after each one
    const block = (w) => { if (LH) { x += w + gap; y = bottom; } };
    // a quiet panel behind the legend so it reads over the map; its height follows what the legend will hold
    const nGroups = view === "group" ? Object.keys(D.meta.clusters).length + (unmapped(D) ? 1 : 0) : 0;
    const ds = D.meta.relief && D.meta.relief.base ? D.meta.relief.base.depth_scale : null;
    const panelH = (view === "group" ? nGroups * 15 : 35) + (rivers === "slope" || rivers === "all" ? 35 : 0) + (ds ? 35 : 0) + 6;
    const labelW = view === "group" ? Math.max(...Object.values(D.meta.clusters).map((c) => ctx.measureText(`${c.name} (${c.n_systems})`).width), unmapped(D) ? ctx.measureText("bedrock not mapped in open data (under half the area)").width : 0) + 18 : 0;
    if (LH) { ctx.fillStyle = dark ? "rgba(27,34,48,.6)" : "rgba(245,247,249,.7)"; ctx.fillRect(0, H - LH, ctx.canvas.width, LH); }
    else { ctx.fillStyle = dark ? "rgba(27,34,48,.78)" : "rgba(245,247,249,.82)"; ctx.fillRect(x - 7, H - 12 - panelH - 2, Math.max(BW, labelW, 240) + 14, panelH + 12); }
    const row = (col, label) => { ctx.fillStyle = col; ctx.fillRect(x, y - 9, 12, 9); ctx.fillStyle = ink; ctx.fillText(label, x + 18, y); y -= 15; };
    const bar = (title, rampOf, ticks) => {
      ctx.font = "10px system-ui, sans-serif"; ctx.fillStyle = muted; ctx.textAlign = "left";
      for (const [t, l] of ticks) { const tx = x + t * BW; ctx.fillRect(tx, y - 4, 1, 4); ctx.textAlign = t < 0.05 ? "left" : t > 0.95 ? "right" : "center"; ctx.fillText(l, tx, y + 7); }
      y -= 6; for (let i = 0; i < 30; i++) { ctx.fillStyle = rampOf(i / 29); ctx.fillRect(x + i * BW / 30, y - BH, BW / 30 + 0.5, BH); }
      y -= BH + 3; ctx.textAlign = "left"; ctx.font = "11px system-ui, sans-serif"; ctx.fillStyle = ink; ctx.fillText(title, x, y); y -= 15;
    };
    const lg = (v, lo, span) => (Math.log10(v) - lo) / span;
    // the depth key as Relief's manifest describes it: a linear bar on the frame's depth scale with the manifest's ticks
    const mark = () => block(BW);
    if (ds) { const max = ds.max_m, kind = ds.kind === "ocean" ? "ocean" : "sea"; bar(`sea floor, depth in m (Relief, linear, ${ds.kind} scale)`, (t) => depthColour(kind, t * max, dark), ds.ticks_m.filter((v) => v / max < 0.9).map((v) => [v / max, v.toLocaleString("en-GB")]).concat([[1, max.toLocaleString("en-GB") + "+"]])); mark(); }
    if (rivers === "slope" || rivers === "all") bar(rivers === "all" ? "fall lines over the rivers, colour is gradient" : "slope flow, colour is the mean gradient", (t) => shapeRampFor(dark)(0.08 * t), [0, 2, 4, 6, 8].map((v) => [v / 8, v + " %"])), mark();
    if (view === "group") { const cl = Object.entries(D.meta.clusters).sort((a, b) => +a[0] - +b[0]); if (unmapped(D)) row(dark ? "#5a606a" : "#c8cbd0", "bedrock not mapped in open data (under half the area)"); for (const [i, c] of cl.reverse()) row(GROUP_COLOURS[+i % GROUP_COLOURS.length], `${c.name} (${c.n_systems})`); block(labelW); }
    else if (view === "quality") bar("sand quality proxy", (t) => qualRamp(0.1 + 0.5 * t), [0.1, 0.2, 0.3, 0.4, 0.5, 0.6].map((v) => [(v - 0.1) / 0.5, v.toFixed(1)]));
    else if (view === "yield") bar("sediment yield, t/km²/yr, log scale", (t) => yieldRamp(0.5 + 2.5 * t), [3, 10, 30, 100, 300, 1000].map((v) => [lg(v, 0.5, 2.5), v.toLocaleString("en-GB")]));
    else if (view === "sand") bar("sand supply, Mt/yr, log scale", (t) => yieldRamp(0.5 + 2.5 * t), [0.03, 0.1, 0.3, 1, 3, 10].map((v) => [lg(v, -1.5, 2.5), String(v)]));
    else if (view === "size") bar("catchment area, km², log scale", (t) => sizeRamp(3 + 3 * t), [1e3, 1e4, 1e5, 1e6].map((v) => [(Math.log10(v) - 3) / 3, v >= 1e6 ? "1,000,000" : v.toLocaleString("en-GB")]));
    ctx.restore();
  }

  function lonlat(crs) {
    if (crs === "EPSG:25832") { const d = Math.PI / 180, a = 6378137, f = 1 / 298.257222101, k0 = 0.9996, e2 = f * (2 - f), ep2 = e2 / (1 - e2); return (lon, lat) => { const p = lat * d, l = (lon - 9) * d, N = a / Math.sqrt(1 - e2 * Math.sin(p) ** 2), T = Math.tan(p) ** 2, C = ep2 * Math.cos(p) ** 2, A = Math.cos(p) * l; const M = a * ((1 - e2 / 4 - 3 * e2 * e2 / 64) * p - (3 * e2 / 8 + 3 * e2 * e2 / 32) * Math.sin(2 * p) + (15 * e2 * e2 / 256) * Math.sin(4 * p)); return [500000 + k0 * N * (A + (1 - T + C) * A ** 3 / 6), k0 * (M + N * Math.tan(p) * (A * A / 2 + (5 - T + 9 * C) * A ** 4 / 24))]; }; }
    if (crs === "EPSG:3035") { const R = 6371007.181, d = Math.PI / 180, p0 = 52 * d, l0 = 10 * d; return (lon, lat) => { const p = lat * d, l = lon * d - l0, k = Math.sqrt(2 / (1 + Math.sin(p0) * Math.sin(p) + Math.cos(p0) * Math.cos(p) * Math.cos(l))); return [4321000 + R * k * Math.cos(p) * Math.sin(l), 3210000 + R * k * (Math.cos(p0) * Math.sin(p) - Math.sin(p0) * Math.cos(p) * Math.cos(l))]; }; }
    if (crs.includes("+proj=lcc")) { const R = 6371007.181, d = Math.PI / 180, p1 = 62 * d, p2 = 70 * d, p0 = 66 * d, l0 = 8 * d; const n = Math.log(Math.cos(p1) / Math.cos(p2)) / Math.log(Math.tan(Math.PI / 4 + p2 / 2) / Math.tan(Math.PI / 4 + p1 / 2)); const F = Math.cos(p1) * Math.pow(Math.tan(Math.PI / 4 + p1 / 2), n) / n, r0 = R * F / Math.pow(Math.tan(Math.PI / 4 + p0 / 2), n); return (lon, lat) => { const r = R * F / Math.pow(Math.tan(Math.PI / 4 + lat * d / 2), n), th = n * (lon * d - l0); return [r * Math.sin(th), r0 - r * Math.cos(th)]; }; }
    return null;
  }

  onSchemeChange(() => last && draw(...last));
  return { draw, repaint: () => last && draw(...last) };
}
