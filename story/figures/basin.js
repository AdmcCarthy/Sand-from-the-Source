// North-east Europe and its margins as source-to-sink frames: Relief hillshade, the land, catchments coloured by one of
// several readings (composition group, sand quality, yield, sand supply, size), flow lines as tapered ribbons by discharge, outlets.
// Coordinates are the frame CRS in metres (d3.geoIdentity, y reflected). Hillshade and land come with the figure;
// the catchments, rivers and outlets are the story's datasets.
import { token, onSchemeChange } from "../runtime/js/subscout.js";

const GROUP_COLOURS = ["#c8553d", "#3d6e9e", "#7a9a3b", "#b8860b", "#6b4c9a", "#2e8b8b", "#a0522d", "#5f5f5f"];

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
    const img = new Image();
    img.src = new URL(`${frame}_hillshade.png`, import.meta.url).href;
    await new Promise((res) => { img.onload = res; img.onerror = res; });
    return (cache[frame] = { systems, rivers, outlets, land, slope, img: img.width ? img : null, meta: frames[frame] });
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
    const dark = (document.documentElement.dataset.colourScheme || "light") === "dark";
    const [x0, y0, x1, y1] = D.meta.relief.extent;
    const aspect = (y1 - y0) / (x1 - x0);
    const H = opts.height ? opts.height() : Math.round(Math.min(width * aspect, window.innerHeight * (width < 600 ? 0.36 : 0.62)));
    const dpr = opts.pixelRatio || window.devicePixelRatio || 1;
    canvas.width = width * dpr; canvas.height = H * dpr; canvas.style.width = width + "px"; canvas.style.height = H + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const proj = d3.geoIdentity().reflectY(true).fitExtent([[0, 0], [width, H]], { type: "Polygon", coordinates: [[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]] });
    const path = d3.geoPath(proj, ctx);
    const [px0, py1] = proj([x0, y0]), [px1, py0] = proj([x1, y1]);
    ctx.fillStyle = token("surface") || (dark ? "#1b2230" : "#eef1f4"); ctx.fillRect(0, 0, width, H);
    ctx.save(); ctx.beginPath(); ctx.rect(px0, py0, px1 - px0, py1 - py0); ctx.clip();
    ctx.fillStyle = dark ? "rgba(24,38,58,.6)" : "rgba(170,196,222,.45)"; ctx.fillRect(px0, py0, px1 - px0, py1 - py0);
    ctx.beginPath(); for (const f of D.land) path(f); ctx.fillStyle = dark ? "rgba(255,255,255,.07)" : "rgba(255,255,255,.55)"; ctx.fill();
    // catchments
    const shown = D.systems.filter((f) => (f.properties.log10_area ?? 9) >= (state.fold ?? 0));
    for (const f of shown) { const c = fillOf(f.properties, view, dark); if (!c) continue; ctx.beginPath(); path(f); ctx.fillStyle = alpha(c, dark ? 0.6 : 0.55); ctx.fill(); }
    ctx.save(); ctx.setLineDash([4, 3]); ctx.beginPath(); for (const f of shown) path(f); ctx.strokeStyle = dark ? "rgba(255,255,255,.4)" : "rgba(40,40,40,.5)"; ctx.lineWidth = 0.8; ctx.stroke(); ctx.restore();
    if (D.img && shade > 0) { ctx.save(); ctx.globalCompositeOperation = "soft-light"; ctx.globalAlpha = Math.min(1, shade); ctx.drawImage(D.img, px0, py0, px1 - px0, py1 - py0); if (shade > 1) ctx.drawImage(D.img, px0, py0, px1 - px0, py1 - py0); ctx.restore(); }
    // water
    ctx.lineCap = "round"; ctx.lineJoin = "round";
    if (rivers === "slope") {
      for (const f of D.slope) { ctx.beginPath(); path(f); ctx.strokeStyle = alpha(gradRamp(f.properties.mean_gradient), 0.75); ctx.lineWidth = 0.6; ctx.stroke(); }
    } else if (rivers !== "off") {
      const sysOf = new Map(shown.map((f) => [f.properties.system, f.properties]));
      const byQ = D.rivers.filter((f) => !state.fold || sysOf.has(f.properties.system)).sort((a, b) => (a.properties.log_discharge ?? 0) - (b.properties.log_discharge ?? 0));
      for (const pass of ["glow", "core"]) for (const f of byQ) {
        const q = Math.max(0, f.properties.log_discharge ?? 0), s = sysOf.get(f.properties.system);
        const col = view === "group" && s && s.cluster >= 0 ? GROUP_COLOURS[s.cluster % GROUP_COLOURS.length] : (dark ? "#a8d0ff" : "#1f5a8f");
        ctx.beginPath(); path(f);
        if (pass === "glow") { ctx.strokeStyle = alpha(col, 0.16); ctx.lineWidth = 2 + 2.4 * q; } else { ctx.strokeStyle = alpha(col, 0.9); ctx.lineWidth = 0.35 + 1.2 * q; }
        ctx.stroke();
      }
    }
    for (const f of D.outlets) { const [x, y] = proj(f.geometry.coordinates); const r = Math.max(1.5, Math.sqrt(f.properties.discharge_cms || 1) / 7); ctx.beginPath(); ctx.arc(x, y, r, 0, 2 * Math.PI); ctx.fillStyle = dark ? "rgba(255,255,255,.85)" : "rgba(20,30,50,.85)"; ctx.fill(); }
    // sink names and a frame rule
    ctx.font = "italic 12px Georgia, serif"; ctx.fillStyle = dark ? "rgba(230,235,240,.8)" : "rgba(40,50,60,.8)";
    const toXY = lonlat(D.meta.crs);
    for (const s of D.meta.sinks || []) { if (!toXY) break; const p = proj(toXY(s.lon, s.lat)); ctx.fillText(s.name, p[0], p[1]); }
    ctx.restore();
    ctx.strokeStyle = dark ? "rgba(255,255,255,.2)" : "rgba(0,0,0,.2)"; ctx.lineWidth = 1; ctx.strokeRect(px0, py0, px1 - px0, py1 - py0);
    // legend, bottom left
    legend(view, rivers, D, dark, H);
  }

  function legend(view, rivers, D, dark, H) {
    ctx.save(); ctx.font = "11px system-ui, sans-serif"; const x = 12; let y = H - 12;
    const row = (col, label) => { ctx.fillStyle = col; ctx.fillRect(x, y - 9, 12, 9); ctx.fillStyle = dark ? "#e6e9ee" : "#26323d"; ctx.fillText(label, x + 18, y); y -= 15; };
    if (view === "group") { const cl = Object.entries(D.meta.clusters).sort((a, b) => +a[0] - +b[0]); for (const [i, c] of cl.reverse()) row(GROUP_COLOURS[+i % GROUP_COLOURS.length], `${c.name} (${c.n_systems})`); }
    else { const label = { quality: "sand quality proxy, 0.1 to 0.6", yield: "sediment yield, 3 to 1,000 t/km²/yr", sand: "sand supply, 0.03 to 10 Mt/yr", size: "catchment area, 1,000 to 1,000,000 km²" }[view]; const ramp = view === "quality" ? (t) => qualRamp(0.1 + 0.5 * t) : view === "size" ? (t) => sizeRamp(3 + 3 * t) : (t) => yieldRamp(0.5 + 2.5 * t); for (let i = 0; i < 10; i++) { ctx.fillStyle = ramp(i / 9); ctx.fillRect(x + i * 12, y - 9, 12, 9); } ctx.fillStyle = dark ? "#e6e9ee" : "#26323d"; ctx.fillText(label, x + 126, y); y -= 15; }
    if (rivers === "slope") { for (let i = 0; i < 10; i++) { ctx.fillStyle = gradRamp(0.08 * i / 9); ctx.fillRect(x + i * 12, y - 9, 12, 9); } ctx.fillStyle = dark ? "#e6e9ee" : "#26323d"; ctx.fillText("slope flow, flat to 8 % gradient", x + 126, y); }
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
