import { darken, lighten, mix } from './color';
import type { Palette } from './palette';
import { H, W, circle, ellipse, g, line, linear, path, poly, r1, radial, rect, rng, smooth } from './svg';

/* ------------------------------------------------------------------ */
/* Gradient registry                                                   */
/* ------------------------------------------------------------------ */

export class Defs {
  private items: string[] = [];
  private names = new Set<string>();
  constructor(private prefix: string) {}

  private id(name: string) {
    return `${this.prefix}-${name}`;
  }

  linear(name: string, stops: [number, string][], vertical = true): string {
    const id = this.id(name);
    if (!this.names.has(id)) {
      this.names.add(id);
      this.items.push(linear(id, stops, vertical));
    }
    return `url(#${id})`;
  }

  radial(name: string, stops: [number, string, number?][]): string {
    const id = this.id(name);
    if (!this.names.has(id)) {
      this.names.add(id);
      this.items.push(radial(id, stops));
    }
    return `url(#${id})`;
  }

  toString(): string {
    return this.items.join('');
  }
}

/* ------------------------------------------------------------------ */
/* Sky, mountains, mist, clouds                                        */
/* ------------------------------------------------------------------ */

export interface SkyOpts {
  sun?: [number, number, number];
  moon?: [number, number, number];
  stars?: boolean;
  glow?: [number, number, number];
  seed?: number;
}

export function sky(d: Defs, p: Palette, o: SkyOpts = {}): string {
  const parts = [rect(0, 0, W, H, { fill: d.linear('sky', [[0, p.sky[0]], [0.62, p.sky[1]], [1, p.sky[2]]]) })];
  if (o.glow) {
    const [x, y, r] = o.glow;
    parts.push(circle(x, y, r, { fill: d.radial('glow', [[0, p.glow.replace(/[\d.]+\)$/, '1)'), 0.55], [1, p.sky[2], 0]]) }));
  }
  if (o.stars) {
    const rand = rng(o.seed ?? 7);
    const stars: string[] = [];
    for (let i = 0; i < 140; i++) {
      const x = rand() * W;
      const y = rand() * H * 0.55;
      const r = rand() < 0.1 ? 1.8 : 0.6 + rand() * 0.9;
      stars.push(circle(x, y, r, { fill: '#fffbe8', opacity: r1(0.35 + rand() * 0.6), class: rand() < 0.25 ? 'twinkle' : undefined }));
    }
    parts.push(g({ class: 'stars' }, ...stars));
  }
  if (o.sun) {
    const [x, y, r] = o.sun;
    parts.push(
      g(
        { class: 'sun' },
        circle(x, y, r * 4, { fill: d.radial('sunhalo', [[0, p.sun, 0.55], [1, p.sun, 0]]) }),
        circle(x, y, r, { fill: p.sun }),
      ),
    );
  }
  if (o.moon) {
    const [x, y, r] = o.moon;
    parts.push(
      g(
        { class: 'moon' },
        circle(x, y, r * 3.2, { fill: d.radial('moonhalo', [[0, '#e8ecff', 0.35], [1, '#e8ecff', 0]]) }),
        circle(x, y, r, { fill: '#f4efd6' }),
        circle(x - r * 0.3, y - r * 0.2, r * 0.22, { fill: '#e2dcc0' }),
        circle(x + r * 0.25, y + r * 0.3, r * 0.15, { fill: '#e2dcc0' }),
        circle(x + r * 0.35, y - r * 0.35, r * 0.1, { fill: '#e6e0c6' }),
      ),
    );
  }
  return parts.join('');
}

export interface RangeOpts {
  name: string;
  seed: number;
  base: number;
  amp: number;
  color: string;
  fade?: string;
  peaks?: [number, number, number][];
  step?: number;
  x0?: number;
  x1?: number;
  bottom?: number;
}

export function ridgeY(o: RangeOpts): (x: number) => number {
  const rand = rng(o.seed);
  const f = [0.004 + rand() * 0.003, 0.011 + rand() * 0.006, 0.03 + rand() * 0.02];
  const ph = [rand() * 6.28, rand() * 6.28, rand() * 6.28];
  return (x: number) => {
    let y = o.base;
    for (const [px, h, w] of o.peaks ?? []) y -= h * Math.exp(-(((x - px) / w) ** 2));
    const n = 0.55 * Math.sin(x * f[0] + ph[0]) + 0.3 * Math.sin(x * f[1] + ph[1]) + 0.15 * Math.sin(x * f[2] + ph[2]);
    return y - o.amp * (n + 1) * 0.5;
  };
}

export function range(d: Defs, o: RangeOpts): string {
  const x0 = o.x0 ?? -20;
  const x1 = o.x1 ?? W + 20;
  const step = o.step ?? 14;
  const y = ridgeY(o);
  const rand = rng(o.seed * 31 + 5);
  const pts: string[] = [];
  for (let x = x0; x <= x1; x += step) pts.push(`${r1(x)} ${r1(y(x) + (rand() - 0.5) * 3)}`);
  const bottom = o.bottom ?? H;
  const fill = o.fade ? d.linear(o.name, [[0, o.color], [1, o.fade]]) : o.color;
  return path(`M${x0} ${bottom} L${pts.join(' L')} L${x1} ${bottom} Z`, { fill });
}

/** A soft horizontal band of mist. */
export function mistBand(d: Defs, name: string, y: number, h: number, color: string, opacity = 1): string {
  const fill = d.linear(`mist-${name}`, [[0, 'rgba(255,255,255,0)'], [0.5, color], [1, 'rgba(255,255,255,0)']]);
  return rect(-20, y, W + 40, h, { fill, opacity });
}

/** A bank of cloud with a bumpy top and flat bottom. */
export function cloudBank(x: number, y: number, w: number, h: number, color: string, seed: number, bump = 40): string {
  const rand = rng(seed);
  let d = `M${r1(x)} ${r1(y + h)} L${r1(x)} ${r1(y)}`;
  let cx = x;
  while (cx < x + w) {
    const rr = bump * (0.5 + rand());
    const dx = Math.min(rr * 2, x + w - cx);
    d += ` a${r1(rr)} ${r1(rr * 0.8)} 0 0 1 ${r1(dx)} 0`;
    cx += dx;
  }
  d += ` L${r1(x + w)} ${r1(y + h)} Z`;
  return path(d, { fill: color });
}

/** Small stylised cloud. */
export function puff(x: number, y: number, s: number, color: string, opacity = 1): string {
  return g(
    { opacity },
    ellipse(x, y, 60 * s, 16 * s, { fill: color }),
    circle(x - 22 * s, y - 10 * s, 20 * s, { fill: color }),
    circle(x + 6 * s, y - 18 * s, 26 * s, { fill: color }),
    circle(x + 34 * s, y - 6 * s, 16 * s, { fill: color }),
  );
}

/* ------------------------------------------------------------------ */
/* Ground, water, vegetation                                           */
/* ------------------------------------------------------------------ */

export function ground(d: Defs, p: Palette, y: number, o: { name?: string; wave?: number; seed?: number; color?: string; dark?: string } = {}): string {
  const rand = rng(o.seed ?? 3);
  const pts: [number, number][] = [];
  for (let x = -40; x <= W + 40; x += 160) pts.push([x, y + (rand() - 0.5) * (o.wave ?? 10)]);
  const top = smooth(pts).replace(/^M/, 'L');
  const fill = d.linear(o.name ?? 'ground', [[0, o.color ?? p.ground], [1, o.dark ?? p.groundDark]]);
  return path(`M-40 ${H} ${top} L${W + 40} ${H} Z`, { fill });
}

export function grassTufts(p: Palette, x0: number, x1: number, y: number, seed: number, n = 16): string {
  const rand = rng(seed);
  const out: string[] = [];
  for (let i = 0; i < n; i++) {
    const x = x0 + rand() * (x1 - x0);
    const yy = y + rand() * 30;
    const h = 10 + rand() * 16;
    out.push(path(`M${r1(x - 7)} ${r1(yy)} Q${r1(x - 4)} ${r1(yy - h * 0.6)} ${r1(x - 9)} ${r1(yy - h)} M${r1(x)} ${r1(yy)} Q${r1(x + 1)} ${r1(yy - h)} ${r1(x + 3)} ${r1(yy - h * 1.2)} M${r1(x + 6)} ${r1(yy)} Q${r1(x + 7)} ${r1(yy - h * 0.5)} ${r1(x + 12)} ${r1(yy - h * 0.8)}`, {
      stroke: rand() < 0.5 ? p.grass : darken(p.grass, 0.15),
      'stroke-width': 2.2,
      fill: 'none',
      'stroke-linecap': 'round',
    }));
  }
  return g({}, ...out);
}

export function pine(p: Palette, x: number, y: number, s: number, seed: number, lean = 0): string {
  const rand = rng(seed);
  const h = 250 * s;
  const topX = x + lean * 60 * s;
  const trunk: [number, number][] = [];
  const steps = 6;
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    trunk.push([x + (topX - x) * t + Math.sin(t * 5 + seed) * 10 * s, y - h * t]);
  }
  const width = (t: number) => (15 - 11 * t) * s;
  const left = trunk.map(([tx, ty], i) => [tx - width(i / steps), ty] as [number, number]);
  const right = trunk.map(([tx, ty], i) => [tx + width(i / steps), ty] as [number, number]).reverse();
  const out: string[] = [path(smooth(left) + ' L' + smooth(right).slice(1) + 'Z', { fill: p.trunk })];
  const pads: string[] = [];
  const branchCount = 4 + Math.floor(rand() * 2);
  for (let i = 0; i < branchCount; i++) {
    const t = 0.35 + (i / branchCount) * 0.6;
    const [bx, by] = trunk[Math.round(t * steps)];
    const dir = i % 2 === 0 ? -1 : 1;
    const len = (70 + rand() * 50) * s * (1.1 - t * 0.5);
    const ex = bx + dir * len;
    const ey = by - (10 + rand() * 25) * s;
    out.push(path(`M${r1(bx)} ${r1(by)} Q${r1((bx + ex) / 2)} ${r1(by + 8 * s)} ${r1(ex)} ${r1(ey)}`, { stroke: p.trunk, 'stroke-width': r1(5 * s), fill: 'none', 'stroke-linecap': 'round' }));
    pads.push(pinePad(p, ex, ey, (55 + rand() * 30) * s * (1.2 - t * 0.4), s));
  }
  pads.push(pinePad(p, topX, y - h - 6 * s, 60 * s, s));
  return g({ class: 'pine' }, ...out, ...pads);
}

function pinePad(p: Palette, x: number, y: number, w: number, s: number): string {
  return g(
    {},
    ellipse(x, y + 6 * s, w, 16 * s, { fill: p.foliageDark }),
    ellipse(x, y, w * 0.92, 14 * s, { fill: p.foliage }),
    ellipse(x - w * 0.25, y - 6 * s, w * 0.45, 9 * s, { fill: lighten(p.foliage, 0.12) }),
  );
}

export function roundTree(p: Palette, x: number, y: number, s: number, seed: number, color?: string): string {
  const rand = rng(seed);
  const c = color ?? p.foliage;
  const out = [path(`M${r1(x - 9 * s)} ${y} Q${r1(x - 4 * s)} ${r1(y - 70 * s)} ${r1(x - 2 * s)} ${r1(y - 130 * s)} L${r1(x + 6 * s)} ${r1(y - 130 * s)} Q${r1(x + 6 * s)} ${r1(y - 60 * s)} ${r1(x + 11 * s)} ${y} Z`, { fill: p.trunk })];
  const blobs: string[] = [];
  for (let i = 0; i < 7; i++) {
    const a = (i / 7) * Math.PI * 2;
    blobs.push(circle(x + Math.cos(a) * 45 * s * (0.7 + rand() * 0.4), y - 150 * s + Math.sin(a) * 30 * s, (32 + rand() * 18) * s, { fill: i % 2 ? c : darken(c, 0.12) }));
  }
  blobs.push(circle(x - 10 * s, y - 165 * s, 38 * s, { fill: lighten(c, 0.08) }));
  return g({}, ...out, ...blobs);
}

export function willow(p: Palette, x: number, y: number, s: number, seed: number): string {
  const rand = rng(seed);
  const out = [path(`M${r1(x - 12 * s)} ${y} C${r1(x - 20 * s)} ${r1(y - 80 * s)} ${r1(x + 20 * s)} ${r1(y - 120 * s)} ${r1(x)} ${r1(y - 200 * s)} L${r1(x + 12 * s)} ${r1(y - 200 * s)} C${r1(x + 30 * s)} ${r1(y - 120 * s)} ${r1(x)} ${r1(y - 70 * s)} ${r1(x + 14 * s)} ${y} Z`, { fill: p.trunk })];
  out.push(ellipse(x + 6 * s, y - 205 * s, 90 * s, 42 * s, { fill: p.foliageDark, opacity: 0.9 }));
  const strands: string[] = [];
  for (let i = 0; i < 26; i++) {
    const sx = x - 90 * s + rand() * 190 * s;
    const sy = y - 200 * s - rand() * 30 * s;
    const len = (90 + rand() * 90) * s;
    strands.push(`M${r1(sx)} ${r1(sy)} q${r1(8 * s)} ${r1(len * 0.5)} ${r1(-4 * s)} ${r1(len)}`);
  }
  out.push(path(strands.join(' '), { stroke: p.foliage, 'stroke-width': r1(3.2 * s), fill: 'none', 'stroke-linecap': 'round', class: 'sway' }));
  return g({}, ...out);
}

export function reeds(p: Palette, x0: number, x1: number, y: number, seed: number): string {
  const rand = rng(seed);
  const out: string[] = [];
  for (let x = x0; x < x1; x += 9 + rand() * 12) {
    const h = 40 + rand() * 50;
    const bend = (rand() - 0.5) * 20;
    out.push(`M${r1(x)} ${r1(y)} q${r1(bend * 0.3)} ${r1(-h * 0.5)} ${r1(bend)} ${r1(-h)}`);
  }
  return path(out.join(' '), { stroke: darken(p.grass, 0.1), 'stroke-width': 2.5, fill: 'none', 'stroke-linecap': 'round' });
}

export function rock(p: Palette, x: number, y: number, w: number, h: number, seed: number, color?: string): string {
  const rand = rng(seed);
  const c = color ?? p.stone;
  const pts: [number, number][] = [
    [x - w / 2, y],
    [x - w / 2 + w * 0.05, y - h * (0.5 + rand() * 0.2)],
    [x - w * 0.2, y - h * (0.9 + rand() * 0.1)],
    [x + w * 0.15, y - h],
    [x + w * 0.42, y - h * (0.6 + rand() * 0.2)],
    [x + w / 2, y],
  ];
  const top: [number, number][] = [pts[1], pts[2], pts[3], pts[4], [x + w * 0.1, y - h * 0.55], [x - w * 0.25, y - h * 0.5]];
  return g({}, poly(pts, { fill: c }), poly(top, { fill: lighten(c, 0.15) }), line(x + w * 0.1, y - h * 0.55, x + w * 0.05, y, { stroke: darken(c, 0.15), 'stroke-width': 2 }));
}

/* ------------------------------------------------------------------ */
/* Architecture                                                        */
/* ------------------------------------------------------------------ */

/** Curved Chinese roof. (x, y) = top-left of the ridge box. */
export function roof(x: number, y: number, w: number, h: number, color: string, o: { oh?: number; lift?: number; ridge?: string } = {}): string {
  const oh = o.oh ?? w * 0.08;
  const lift = o.lift ?? h * 0.4;
  const d =
    `M${r1(x - oh)} ${r1(y + h - lift)}` +
    ` Q${r1(x + w * 0.1)} ${r1(y + h + 2)} ${r1(x + w * 0.5)} ${r1(y + h)}` +
    ` Q${r1(x + w * 0.9)} ${r1(y + h + 2)} ${r1(x + w + oh)} ${r1(y + h - lift)}` +
    ` Q${r1(x + w * 0.86)} ${r1(y + h * 0.5)} ${r1(x + w * 0.84)} ${r1(y)}` +
    ` L${r1(x + w * 0.16)} ${r1(y)}` +
    ` Q${r1(x + w * 0.14)} ${r1(y + h * 0.5)} ${r1(x - oh)} ${r1(y + h - lift)} Z`;
  const tiles: string[] = [];
  const n = Math.max(4, Math.round(w / 16));
  for (let i = 1; i < n; i++) {
    const t = i / n;
    const tx = x + w * 0.16 + (w * 0.68) * t;
    const bx = x - oh * 0.2 + (w + oh * 0.4) * t;
    tiles.push(`M${r1(tx)} ${r1(y + 3)} L${r1(bx)} ${r1(y + h - 3)}`);
  }
  const ridge = o.ridge ?? darken(color, 0.3);
  return g(
    {},
    path(d, { fill: color }),
    path(tiles.join(' '), { stroke: darken(color, 0.18), 'stroke-width': 1.6, fill: 'none', opacity: 0.8 }),
    path(`M${r1(x + w * 0.12)} ${r1(y - 4)} L${r1(x + w * 0.88)} ${r1(y - 4)}`, { stroke: ridge, 'stroke-width': r1(Math.max(5, h * 0.14)), 'stroke-linecap': 'round' }),
    path(`M${r1(x + w * 0.1)} ${r1(y - 4)} q-6 -2 -9 -14 M${r1(x + w * 0.9)} ${r1(y - 4)} q6 -2 9 -14`, { stroke: ridge, 'stroke-width': 4, fill: 'none', 'stroke-linecap': 'round' }),
    path(`M${r1(x - oh)} ${r1(y + h - lift)} q-4 -6 -2 -14 M${r1(x + w + oh)} ${r1(y + h - lift)} q4 -6 2 -14`, { stroke: darken(color, 0.25), 'stroke-width': 3, fill: 'none', 'stroke-linecap': 'round' }),
  );
}

export interface HouseOpts {
  door?: boolean;
  window?: boolean;
  roofH?: number;
  wall?: string;
  roofColor?: string;
}

export function house(p: Palette, x: number, y: number, w: number, h: number, o: HouseOpts = {}): string {
  const roofH = o.roofH ?? h * 0.55;
  const wall = o.wall ?? p.wall;
  const parts = [
    rect(x - 12, y - 14, w + 24, 16, { fill: p.stoneDark }),
    rect(x - 10, y - 16, w + 20, 5, { fill: p.stoneLight }),
    rect(x, y - h, w, h - 14, { fill: wall }),
    rect(x + w * 0.62, y - h, w * 0.38, h - 14, { fill: p.wallShade, opacity: 0.5 }),
    rect(x, y - h, 9, h - 14, { fill: p.wood }),
    rect(x + w - 9, y - h, 9, h - 14, { fill: p.wood }),
    rect(x, y - h, w, 10, { fill: p.woodDark }),
  ];
  if (o.door !== false) {
    const dw = w * 0.26;
    const dx = x + w * 0.37;
    parts.push(rect(dx - 5, y - h * 0.72 - 5, dw + 10, h * 0.72 - 9, { fill: p.woodDark }), rect(dx, y - h * 0.72, dw, h * 0.72 - 14, { fill: darken(p.wood, 0.45) }), line(dx + dw / 2, y - h * 0.72, dx + dw / 2, y - 14, { stroke: p.woodDark, 'stroke-width': 2 }));
  }
  if (o.window !== false) {
    const ww = w * 0.2;
    for (const wx of [x + w * 0.1, x + w * 0.7]) {
      const wy = y - h * 0.68;
      const lat: string[] = [];
      for (let i = 1; i < 4; i++) lat.push(`M${r1(wx + (ww * i) / 4)} ${r1(wy)} v${r1(ww)} M${r1(wx)} ${r1(wy + (ww * i) / 4)} h${r1(ww)}`);
      parts.push(rect(wx - 4, wy - 4, ww + 8, ww + 8, { fill: p.woodDark }), rect(wx, wy, ww, ww, { fill: mix(p.paper, p.gold, 0.2) }), path(lat.join(' '), { stroke: p.woodDark, 'stroke-width': 2.5 }));
    }
  }
  parts.push(roof(x - 14, y - h - roofH * 0.82, w + 28, roofH, o.roofColor ?? p.roof, { oh: w * 0.1 }));
  return g({}, ...parts);
}

/** Stone archway (paifang). The plaque area is centered at (x + w/2, y - h*0.82). */
export function paifang(p: Palette, x: number, y: number, w: number, h: number, o: { color?: string; roofColor?: string } = {}): string {
  const c = o.color ?? p.stone;
  const dark = darken(c, 0.2);
  const pw = w * 0.07;
  const cols = [0, 0.27, 0.73, 1].map((f) => x + f * w - (f === 1 ? pw : f === 0 ? 0 : pw / 2));
  const heights = [0.66, 0.86, 0.86, 0.66].map((f) => h * f);
  const parts: string[] = [];
  cols.forEach((cx, i) => {
    parts.push(rect(cx, y - heights[i], pw, heights[i], { fill: c }), rect(cx + pw * 0.7, y - heights[i], pw * 0.3, heights[i], { fill: dark, opacity: 0.5 }));
    parts.push(rect(cx - pw * 0.35, y - 34, pw * 1.7, 34, { fill: dark }), rect(cx - pw * 0.25, y - 60, pw * 1.5, 26, { fill: c }));
  });
  const midL = cols[1];
  const midR = cols[2] + pw;
  parts.push(rect(midL - 6, y - h * 0.9, midR - midL + 12, h * 0.07, { fill: dark }));
  parts.push(rect(midL + 12, y - h * 0.88, midR - midL - 24, h * 0.13, { fill: c }));
  parts.push(rect(midL - 4, y - h * 0.72, midR - midL + 8, h * 0.05, { fill: dark }));
  parts.push(rect(cols[0] - 4, y - h * 0.68, cols[1] - cols[0] + pw + 8, h * 0.05, { fill: dark }));
  parts.push(rect(cols[2] - 4, y - h * 0.68, cols[3] - cols[2] + pw + 8, h * 0.05, { fill: dark }));
  parts.push(rect(cols[0] - 4, y - h * 0.6, cols[1] - cols[0] + pw + 8, h * 0.035, { fill: c }));
  parts.push(rect(cols[2] - 4, y - h * 0.6, cols[3] - cols[2] + pw + 8, h * 0.035, { fill: c }));
  const rc = o.roofColor ?? darken(c, 0.35);
  parts.push(roof(midL - 10, y - h * 1.01, midR - midL + 20, h * 0.13, rc, { oh: 22 }));
  parts.push(roof(cols[0] - 8, y - h * 0.77, cols[1] - cols[0] + pw + 16, h * 0.1, rc, { oh: 14 }));
  parts.push(roof(cols[2] - 8, y - h * 0.77, cols[3] - cols[2] + pw + 16, h * 0.1, rc, { oh: 14 }));
  return g({ class: 'paifang' }, ...parts);
}

/** Gate tower with an arched tunnel and a pavilion (South Gate of Heaven). */
export function gateTower(p: Palette, cx: number, y: number, o: { open: boolean; tunnelW?: number; tunnelH?: number }): string {
  const tw = o.tunnelW ?? 280;
  const th = o.tunnelH ?? 360;
  const bw = 640;
  const bh = 430;
  const bx = cx - bw / 2;
  const by = y - bh;
  const parts: string[] = [];
  parts.push(path(`M${bx - 20} ${y} L${bx} ${by} L${bx + bw} ${by} L${bx + bw + 20} ${y} Z`, { fill: p.stone }));
  const bricks: string[] = [];
  for (let row = 0; row < 14; row++) {
    const yy = by + 18 + row * 30;
    bricks.push(`M${bx - 20 + row * 1.4} ${yy} H${bx + bw + 20 - row * 1.4}`);
    for (let col = 0; col < 12; col++) {
      const xx = bx + (col + (row % 2) * 0.5) * (bw / 11);
      bricks.push(`M${r1(xx)} ${yy - 30} V${yy}`);
    }
  }
  parts.push(path(bricks.join(' '), { stroke: p.stoneDark, 'stroke-width': 1.3, opacity: 0.45 }));
  parts.push(rect(bx - 10, by - 16, bw + 20, 22, { fill: p.stoneDark }));
  const tx = cx - tw / 2;
  const ty = y - th;
  const arch = `M${tx} ${y} V${ty + tw / 2} A${tw / 2} ${tw / 2} 0 0 1 ${tx + tw} ${ty + tw / 2} V${y} Z`;
  parts.push(path(arch, { fill: darken(p.stone, 0.35) }));
  if (o.open) {
    parts.push(path(`M${tx + 14} ${y} V${ty + tw / 2 + 6} A${tw / 2 - 14} ${tw / 2 - 14} 0 0 1 ${tx + tw - 14} ${ty + tw / 2 + 6} V${y} Z`, { fill: '#1a1622' }));
    parts.push(path(`M${cx - 46} ${y} V${y - 120} A46 46 0 0 1 ${cx + 46} ${y - 120} V${y} Z`, { fill: '#f6c883', opacity: 0.75 }));
    parts.push(path(`M${cx - 46} ${y} L${cx - 110} ${y} L${cx - 70} ${y - 6} L${cx + 70} ${y - 6} L${cx + 110} ${y} Z`, { fill: '#f6c883', opacity: 0.35 }));
    parts.push(rect(tx + 4, ty + tw / 2, 16, th - tw / 2, { fill: p.red }), rect(tx + tw - 20, ty + tw / 2, 16, th - tw / 2, { fill: p.red }));
  } else {
    const inner = `M${tx + 14} ${y} V${ty + tw / 2 + 6} A${tw / 2 - 14} ${tw / 2 - 14} 0 0 1 ${tx + tw - 14} ${ty + tw / 2 + 6} V${y} Z`;
    parts.push(path(inner, { fill: p.red }));
    const studs: string[] = [];
    for (let r = 0; r < 7; r++) for (let c = 0; c < 4; c++) {
      studs.push(circle(tx + 40 + c * 28, ty + tw / 2 + 30 + r * 34, 4.5, { fill: p.gold }));
      studs.push(circle(cx + 26 + c * 28, ty + tw / 2 + 30 + r * 34, 4.5, { fill: p.gold }));
    }
    parts.push(...studs, line(cx, ty + 24, cx, y, { stroke: p.redDark, 'stroke-width': 4 }));
    parts.push(circle(cx - 16, y - 170, 9, { fill: 'none', stroke: p.gold, 'stroke-width': 3 }), circle(cx + 16, y - 170, 9, { fill: 'none', stroke: p.gold, 'stroke-width': 3 }));
  }
  const py = by - 16;
  const pw = 440;
  const px = cx - pw / 2;
  parts.push(rect(px - 20, py - 18, pw + 40, 18, { fill: p.stoneLight }));
  const rails: string[] = [];
  for (let i = 0; i <= 22; i++) rails.push(`M${px - 16 + i * 21} ${py - 18} v-26`);
  parts.push(path(rails.join(' ') + ` M${px - 20} ${py - 44} H${px + pw + 20}`, { stroke: p.stoneLight, 'stroke-width': 4 }));
  parts.push(rect(px + 20, py - 150, pw - 40, 110, { fill: p.redDark }));
  for (let i = 0; i < 6; i++) parts.push(rect(px + 24 + i * ((pw - 60) / 5), py - 150, 12, 110, { fill: p.red }));
  const lat: string[] = [];
  for (let i = 0; i < 5; i++) for (let k = 1; k < 5; k++) {
    const lx = px + 38 + i * ((pw - 60) / 5);
    lat.push(`M${r1(lx)} ${py - 140 + k * 20} h${r1((pw - 60) / 5 - 18)}`);
  }
  parts.push(path(lat.join(' '), { stroke: p.gold, 'stroke-width': 1.5, opacity: 0.6 }));
  parts.push(roof(px - 20, py - 212, pw + 40, 70, p.roof, { oh: 50 }));
  parts.push(roof(px + 50, py - 262, pw - 100, 60, p.roof, { oh: 36 }));
  return g({ class: 'gate-tower' }, ...parts);
}

/** Straight stairs going up into the distance (perspective). */
export function stairsInto(p: Palette, x0: number, y0: number, w0: number, x1: number, y1: number, w1: number, n: number): string {
  const parts: string[] = [];
  parts.push(poly([[x0 - w0 / 2, y0], [x1 - w1 / 2, y1], [x1 + w1 / 2, y1], [x0 + w0 / 2, y0]], { fill: p.stoneDark }));
  for (let i = 0; i < n; i++) {
    const t = 1 - Math.pow(1 - i / n, 1.6);
    const t2 = 1 - Math.pow(1 - (i + 0.55) / n, 1.6);
    const ya = y0 + (y1 - y0) * t;
    const yb = y0 + (y1 - y0) * t2;
    const xa = x0 + (x1 - x0) * t;
    const xb = x0 + (x1 - x0) * t2;
    const wa = w0 + (w1 - w0) * t;
    const wb = w0 + (w1 - w0) * t2;
    parts.push(poly([[xa - wa / 2, ya], [xb - wb / 2, yb], [xb + wb / 2, yb], [xa + wa / 2, ya]], { fill: p.stoneLight }));
  }
  return g({ class: 'stairs' }, ...parts);
}

/** Stairs following a walk path: a sloped band with step marks. */
export function stairsPath(p: Palette, pts: [number, number][], width = 34): string {
  const parts: string[] = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const [ax, ay] = pts[i];
    const [bx, by] = pts[i + 1];
    parts.push(poly([[ax - 20, ay - 6], [bx + (bx > ax ? 20 : -20), by - 6], [bx + (bx > ax ? 20 : -20), by + width], [ax - 20, ay + width]], { fill: p.stoneDark }));
    parts.push(poly([[ax - 16, ay - 4], [bx, by - 4], [bx, by + 8], [ax - 16, ay + 8]], { fill: p.stoneLight }));
    const len = Math.hypot(bx - ax, by - ay);
    const steps = Math.floor(len / 18);
    const marks: string[] = [];
    for (let k = 1; k < steps; k++) {
      const t = k / steps;
      const mx = ax + (bx - ax) * t;
      const my = ay + (by - ay) * t;
      marks.push(`M${r1(mx)} ${r1(my - 4)} v${width - 2}`);
    }
    parts.push(path(marks.join(' '), { stroke: darken(p.stoneDark, 0.25), 'stroke-width': 2 }));
    const posts: string[] = [];
    for (let k = 0; k <= steps; k += 3) {
      const t = k / Math.max(1, steps);
      posts.push(`M${r1(ax + (bx - ax) * t)} ${r1(ay + (by - ay) * t + width)} v-40`);
    }
    parts.push(path(posts.join(' '), { stroke: p.stone, 'stroke-width': 5, 'stroke-linecap': 'round' }));
    parts.push(path(`M${ax} ${ay + width - 36} L${bx} ${by + width - 36}`, { stroke: p.stone, 'stroke-width': 3, opacity: 0.8 }));
  }
  return g({ class: 'stairs-path' }, ...parts);
}

export function stele(p: Palette, x: number, y: number, w: number, h: number, o: { base?: boolean; color?: string } = {}): string {
  const c = o.color ?? p.stone;
  const bodyTop = y - h;
  const parts: string[] = [];
  if (o.base !== false) parts.push(rect(x - w * 0.18, y - 40, w * 1.36, 40, { fill: darken(c, 0.25) }), rect(x - w * 0.12, y - 48, w * 1.24, 10, { fill: darken(c, 0.1) }));
  const bottom = o.base !== false ? y - 48 : y;
  parts.push(path(`M${x} ${bottom} V${bodyTop + w * 0.3} Q${x} ${bodyTop} ${x + w / 2} ${bodyTop} Q${x + w} ${bodyTop} ${x + w} ${bodyTop + w * 0.3} V${bottom} Z`, { fill: c }));
  parts.push(path(`M${x + w * 0.78} ${bottom} V${bodyTop + w * 0.3} Q${x + w} ${bodyTop + w * 0.1} ${x + w} ${bodyTop + w * 0.3} V${bottom} Z`, { fill: darken(c, 0.15), opacity: 0.6 }));
  return g({}, ...parts);
}

export function wallSegment(p: Palette, x0: number, x1: number, y: number, h: number): string {
  return g({}, rect(x0, y - h, x1 - x0, h, { fill: p.red }), rect(x0, y - h, x1 - x0, h * 0.12, { fill: p.redDark }), roof(x0 - 10, y - h - 30, x1 - x0 + 20, 34, p.roof, { oh: 6, lift: 4 }));
}

export function railing(p: Palette, x0: number, x1: number, y: number, h = 50, color?: string): string {
  const c = color ?? p.stoneLight;
  const posts: string[] = [];
  for (let x = x0; x <= x1; x += 60) posts.push(rect(x - 5, y - h - 6, 10, h + 6, { fill: c }), rect(x - 7, y - h - 12, 14, 8, { fill: darken(c, 0.15) }));
  return g({}, rect(x0, y - h, x1 - x0, 8, { fill: c }), rect(x0, y - h * 0.45, x1 - x0, 6, { fill: darken(c, 0.1) }), ...posts);
}

/* ------------------------------------------------------------------ */
/* Props                                                               */
/* ------------------------------------------------------------------ */

export function boat(p: Palette, x: number, y: number, w: number): string {
  const hull = `M${x - w / 2} ${y - 40} Q${x - w * 0.42} ${y + 10} ${x} ${y + 12} Q${x + w * 0.42} ${y + 10} ${x + w / 2} ${y - 46} L${x + w * 0.4} ${y - 30} L${x - w * 0.4} ${y - 26} Z`;
  return g(
    { class: 'boat' },
    path(hull, { fill: p.woodDark }),
    path(`M${x - w * 0.46} ${y - 32} Q${x} ${y - 16} ${x + w * 0.47} ${y - 36}`, { stroke: p.wood, 'stroke-width': 6, fill: 'none' }),
    path(`M${x - w * 0.34} ${y - 30} Q${x - w * 0.34} ${y - 118} ${x - w * 0.05} ${y - 118} Q${x + w * 0.06} ${y - 118} ${x + w * 0.1} ${y - 26} Z`, { fill: mix(p.wood, p.gold, 0.35) }),
    path(`M${x - w * 0.3} ${y - 50} Q${x - w * 0.12} ${y - 108} ${x + w * 0.07} ${y - 50} M${x - w * 0.3} ${y - 80} Q${x - w * 0.14} ${y - 112} ${x + w * 0.08} ${y - 80}`, { stroke: p.woodDark, 'stroke-width': 2, fill: 'none', opacity: 0.6 }),
  );
}

export function pier(p: Palette, x0: number, x1: number, y: number): string {
  const posts: string[] = [];
  for (let x = x0 + 10; x < x1; x += 70) posts.push(rect(x, y, 14, 80, { fill: p.woodDark }));
  const planks: string[] = [];
  for (let x = x0; x < x1; x += 22) planks.push(`M${x} ${y - 16} v18`);
  return g({}, ...posts, rect(x0, y - 16, x1 - x0, 18, { fill: p.wood }), path(planks.join(' '), { stroke: p.woodDark, 'stroke-width': 1.5, opacity: 0.6 }));
}

export function campfire(p: Palette, x: number, y: number, lit: boolean): string {
  const stones: string[] = [];
  for (let i = 0; i < 7; i++) stones.push(ellipse(x - 48 + i * 16, y - 4 + (i % 2) * 3, 11, 8, { fill: i % 2 ? p.stoneDark : p.stone }));
  const logs = g({}, path(`M${x - 36} ${y - 8} L${x + 30} ${y - 26}`, { stroke: p.woodDark, 'stroke-width': 10, 'stroke-linecap': 'round' }), path(`M${x - 30} ${y - 26} L${x + 36} ${y - 8}`, { stroke: p.wood, 'stroke-width': 10, 'stroke-linecap': 'round' }));
  const parts = [ellipse(x, y - 4, 50, 10, { fill: '#2b2521', opacity: 0.6 }), logs, ...stones];
  if (lit) {
    parts.push(
      g(
        { class: 'flame' },
        circle(x, y - 50, 90, { fill: '#ffb85c', opacity: 0.18 }),
        path(`M${x - 26} ${y - 14} Q${x - 30} ${y - 60} ${x - 6} ${y - 96} Q${x - 4} ${y - 60} ${x + 8} ${y - 50} Q${x + 14} ${y - 76} ${x + 4} ${y - 104} Q${x + 36} ${y - 64} ${x + 26} ${y - 14} Z`, { fill: '#f08a2c' }),
        path(`M${x - 14} ${y - 14} Q${x - 14} ${y - 46} ${x} ${y - 66} Q${x + 6} ${y - 44} ${x + 12} ${y - 40} Q${x + 18} ${y - 30} ${x + 14} ${y - 14} Z`, { fill: '#ffd36b' }),
      ),
    );
  } else {
    parts.push(ellipse(x, y - 14, 22, 7, { fill: '#6d5e55' }), path(`M${x - 4} ${y - 22} q-6 -16 4 -30 q8 -12 0 -28`, { stroke: '#cfc8c0', 'stroke-width': 3, fill: 'none', opacity: 0.4 }));
  }
  return g({}, ...parts);
}

export function woodpile(p: Palette, x: number, y: number): string {
  const parts: string[] = [roof(x - 90, y - 190, 180, 40, p.roof, { oh: 12, lift: 8 }), rect(x - 78, y - 160, 8, 160, { fill: p.woodDark }), rect(x + 70, y - 160, 8, 160, { fill: p.woodDark })];
  const logs: string[] = [];
  for (let row = 0; row < 4; row++) for (let i = 0; i < 6 - (row % 2); i++) {
    const lx = x - 58 + i * 23 + (row % 2) * 11;
    const ly = y - 12 - row * 22;
    logs.push(circle(lx, ly, 11, { fill: p.wood }), circle(lx, ly, 6, { fill: mix(p.wood, p.gold, 0.5) }));
  }
  return g({}, ...parts, ...logs);
}

export function bigJar(p: Palette, x: number, y: number, s = 1): string {
  const w = 60 * s;
  const h = 100 * s;
  return g(
    {},
    ellipse(x, y, w * 1.05, 10 * s, { fill: p.shade }),
    path(`M${x - w * 0.7} ${y - h} Q${x - w * 1.2} ${y - h * 0.55} ${x - w * 0.6} ${y} L${x + w * 0.6} ${y} Q${x + w * 1.2} ${y - h * 0.55} ${x + w * 0.7} ${y - h} Z`, { fill: '#5a3a2a' }),
    path(`M${x - w * 0.55} ${y - h * 0.95} Q${x - w * 0.95} ${y - h * 0.55} ${x - w * 0.45} ${y - h * 0.08}`, { stroke: '#8a5a3e', 'stroke-width': 6 * s, fill: 'none', opacity: 0.6 }),
    ellipse(x, y - h, w * 0.75, 11 * s, { fill: '#3a2419' }),
    ellipse(x, y - h + 2, w * 0.6, 7 * s, { fill: '#1f140e' }),
  );
}

export function teaJar(p: Palette, x: number, y: number, s = 1): string {
  return g(
    {},
    ellipse(x, y, 34 * s, 6 * s, { fill: p.shade }),
    path(`M${x - 18 * s} ${y - 70 * s} Q${x - 44 * s} ${y - 40 * s} ${x - 24 * s} ${y} L${x + 24 * s} ${y} Q${x + 44 * s} ${y - 40 * s} ${x + 18 * s} ${y - 70 * s} Z`, { fill: '#e9e2cf' }),
    path(`M${x - 30 * s} ${y - 42 * s} Q${x} ${y - 36 * s} ${x + 30 * s} ${y - 42 * s}`, { stroke: '#4c6c8c', 'stroke-width': 3, fill: 'none' }),
    rect(x - 14 * s, y - 80 * s, 28 * s, 12 * s, { fill: '#4c6c8c', rx: 3 }),
  );
}

export function cup(x: number, y: number, big: boolean, color = '#e9e2cf', fill?: string): string {
  const w = big ? 22 : 14;
  const h = big ? 26 : 16;
  return g(
    {},
    path(`M${x - w} ${y - h} L${x - w * 0.7} ${y} L${x + w * 0.7} ${y} L${x + w} ${y - h} Z`, { fill: color, stroke: darken(color, 0.3), 'stroke-width': 1.5 }),
    fill ? ellipse(x, y - h, w * 0.92, 3.5, { fill }) : '',
    path(`M${x - w * 0.8} ${y - h * 0.55} H${x + w * 0.8}`, { stroke: '#4c6c8c', 'stroke-width': 2 }),
  );
}

export function bucketProp(p: Palette, x: number, y: number): string {
  return g({}, path(`M${x - 24} ${y - 50} L${x - 18} ${y} L${x + 18} ${y} L${x + 24} ${y - 50} Z`, { fill: p.wood }), path(`M${x - 22} ${y - 36} H${x + 22} M${x - 20} ${y - 14} H${x + 20}`, { stroke: p.woodDark, 'stroke-width': 4 }), path(`M${x - 24} ${y - 50} Q${x} ${y - 90} ${x + 24} ${y - 50}`, { stroke: p.woodDark, 'stroke-width': 3, fill: 'none' }));
}

export function fence(p: Palette, x0: number, x1: number, y: number): string {
  const parts: string[] = [];
  for (let x = x0; x <= x1; x += 26) parts.push(path(`M${x} ${y} V${y - 58} l6 -8 l6 8 V${y}`, { fill: p.wood, stroke: p.woodDark, 'stroke-width': 1.5 }));
  return g({}, rect(x0 - 6, y - 44, x1 - x0 + 24, 6, { fill: p.woodDark }), rect(x0 - 6, y - 20, x1 - x0 + 24, 6, { fill: p.woodDark }), ...parts);
}

export function hangingLantern(p: Palette, x: number, y: number, s: number, lit: boolean): string {
  const col = lit ? '#e8552f' : darken(p.red, 0.2);
  return g(
    { class: lit ? 'lantern lit' : 'lantern' },
    line(x, y - 20 * s, x, y, { stroke: p.ink, 'stroke-width': 1.5 }),
    lit ? circle(x, y + 22 * s, 46 * s, { fill: '#ffb060', opacity: 0.25 }) : '',
    rect(x - 10 * s, y, 20 * s, 6 * s, { fill: p.ink }),
    ellipse(x, y + 22 * s, 20 * s, 18 * s, { fill: col }),
    path(`M${x - 10 * s} ${y + 8 * s} Q${x - 16 * s} ${y + 22 * s} ${x - 10 * s} ${y + 36 * s} M${x + 10 * s} ${y + 8 * s} Q${x + 16 * s} ${y + 22 * s} ${x + 10 * s} ${y + 36 * s} M${x} ${y + 5 * s} V${y + 39 * s}`, { stroke: darken(col, 0.3), 'stroke-width': 1.2, fill: 'none' }),
    rect(x - 8 * s, y + 38 * s, 16 * s, 5 * s, { fill: p.ink }),
    line(x, y + 43 * s, x, y + 58 * s, { stroke: p.gold, 'stroke-width': 2 }),
  );
}

export function lanternString(p: Palette, x0: number, x1: number, y: number, sag: number, n: number, lit: boolean): string {
  const parts = [path(`M${x0} ${y} Q${(x0 + x1) / 2} ${y + sag * 2} ${x1} ${y}`, { stroke: p.ink, 'stroke-width': 1.5, fill: 'none' })];
  for (let i = 1; i <= n; i++) {
    const t = i / (n + 1);
    const lx = x0 + (x1 - x0) * t;
    const ly = y + 4 * sag * t * (1 - t) * 1;
    parts.push(hangingLantern(p, lx, ly + 18, 0.8, lit));
  }
  return g({}, ...parts);
}

export function stall(p: Palette, x: number, y: number, w: number, awning: string): string {
  return g(
    {},
    rect(x + 6, y - 190, 8, 190, { fill: p.woodDark }),
    rect(x + w - 14, y - 190, 8, 190, { fill: p.woodDark }),
    path(`M${x - 16} ${y - 160} L${x + 10} ${y - 200} L${x + w - 10} ${y - 200} L${x + w + 16} ${y - 160} Z`, { fill: awning }),
    path(`M${x - 16} ${y - 160} ${Array.from({ length: Math.round((w + 32) / 24) }, () => 'q6 10 12 0 q6 10 12 0').join(' ')}`, { fill: awning, stroke: darken(awning, 0.2), 'stroke-width': 1 }),
    rect(x, y - 70, w, 16, { fill: p.wood }),
    rect(x + 4, y - 54, w - 8, 54, { fill: p.woodDark }),
  );
}

export function lowTable(p: Palette, x: number, y: number, w: number): string {
  return g({}, ellipse(x, y, w * 0.55, 8, { fill: p.shade }), rect(x - w / 2, y - 48, w, 10, { fill: p.wood }), rect(x - w / 2 + 6, y - 38, 8, 38, { fill: p.woodDark }), rect(x + w / 2 - 14, y - 38, 8, 38, { fill: p.woodDark }));
}

export function stool(p: Palette, x: number, y: number): string {
  return g({}, rect(x - 20, y - 34, 40, 8, { fill: p.wood }), rect(x - 16, y - 26, 6, 26, { fill: p.woodDark }), rect(x + 10, y - 26, 6, 26, { fill: p.woodDark }));
}

export function hopscotch(x0: number, y: number, n: number, step: number): string {
  const parts: string[] = [];
  for (let i = 0; i < n; i++) {
    const x = x0 + i * step;
    parts.push(path(`M${x - step / 2 + 4} ${y - 8} L${x + step / 2 - 4} ${y - 8} L${x + step / 2 - 1} ${y + 14} L${x - step / 2 + 1} ${y + 14} Z`, { fill: 'none', stroke: '#f7efe0', 'stroke-width': 2.5, opacity: 0.8 }));
  }
  return g({ class: 'hopscotch' }, ...parts);
}

export function signPole(p: Palette, x: number, y: number, h: number): string {
  return g({}, rect(x - 7, y - h, 14, h, { fill: p.woodDark }), ellipse(x, y, 18, 5, { fill: p.shade }));
}

export function compassTable(p: Palette, cx: number, cy: number): string {
  return g(
    {},
    rect(cx - 90, cy + 20, 180, 12, { fill: p.wood }),
    rect(cx - 80, cy + 32, 10, 60, { fill: p.woodDark }),
    rect(cx + 70, cy + 32, 10, 60, { fill: p.woodDark }),
    ellipse(cx, cy, 82, 42, { fill: '#8a6a3a' }),
    ellipse(cx, cy, 72, 36, { fill: '#b8904a' }),
    ellipse(cx, cy, 48, 24, { fill: 'none', stroke: '#6a4a22', 'stroke-width': 1.5 }),
    ellipse(cx, cy, 26, 13, { fill: '#e8d9a8' }),
    path(`M${cx} ${cy - 10} L${cx + 5} ${cy} L${cx} ${cy + 14} L${cx - 5} ${cy} Z`, { fill: '#b8302a' }),
  );
}

/** The trail map carved on a stone: three gates on a winding path, "you are here" in the middle. */
export function mapStone(p: Palette, x: number, y: number, w: number, h: number): string {
  const top = y - h;
  const ink = darken(p.stoneLight, 0.4);
  return g(
    {},
    stele(p, x, y, w, h, { color: p.stoneLight }),
    path(`M${x + 45} ${top + 250} Q${x + 20} ${top + 200} ${x + 55} ${top + 150} Q${x + 85} ${top + 100} ${x + 65} ${top + 50}`, { stroke: ink, 'stroke-width': 3, 'stroke-dasharray': '6 5', fill: 'none' }),
    path(`M${x + 14} ${top + 300} L${x + 60} ${top + 24} L${x + 110} ${top + 300}`, { stroke: ink, 'stroke-width': 2, fill: 'none', opacity: 0.35 }),
    circle(x + 45, top + 250, 6, { fill: ink }),
    circle(x + 55, top + 150, 10, { fill: '#c0392b', class: 'pulse-dot' }),
    circle(x + 65, top + 50, 6, { fill: ink }),
  );
}

export function bellRack(p: Palette, x: number, y: number, w: number, icons: string[]): string {
  const parts: string[] = [];
  parts.push(rect(x, y, 12, 250, { fill: p.woodDark }), rect(x + w - 12, y, 12, 250, { fill: p.woodDark }));
  parts.push(rect(x - 16, y - 10, w + 32, 16, { fill: p.wood }), path(`M${x - 22} ${y - 10} q-6 -10 2 -16 M${x + w + 22} ${y - 10} q6 -10 -2 -16`, { stroke: p.wood, 'stroke-width': 8, fill: 'none', 'stroke-linecap': 'round' }));
  const n = icons.length;
  icons.forEach((icon, i) => {
    const bx = x + 28 + (i * (w - 56)) / (n - 1);
    const by = y + 40 + (i % 2) * 18;
    parts.push(
      g(
        { class: 'bell', 'data-bell': i },
        line(bx, y + 6, bx, by, { stroke: p.ink, 'stroke-width': 2 }),
        path(`M${bx - 18} ${by + 58} Q${bx - 20} ${by + 6} ${bx} ${by} Q${bx + 20} ${by + 6} ${bx + 18} ${by + 58} Z`, { fill: '#9a7a3a' }),
        rect(bx - 22, by + 54, 44, 8, { fill: '#7a5a28', rx: 3 }),
        g({ transform: `translate(${bx - 13} ${by + 16}) scale(0.26)` }, icon),
      ),
    );
  });
  return g({}, ...parts);
}

export function cliffMass(p: Palette, pts: [number, number][], seed: number, color?: string): string {
  const rand = rng(seed);
  const c = color ?? p.stoneDark;
  const strata: string[] = [];
  const xs = pts.map((q) => q[0]);
  const ys = pts.map((q) => q[1]);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  for (let i = 0; i < 14; i++) {
    const sx = minX + rand() * (maxX - minX);
    const sy = minY + rand() * (maxY - minY);
    strata.push(`M${r1(sx)} ${r1(sy)} q${r1(20 + rand() * 30)} ${r1(-6 + rand() * 12)} ${r1(50 + rand() * 60)} ${r1(-4 + rand() * 8)}`);
  }
  const id = `clip${seed}`;
  return g(
    {},
    `<clipPath id="${id}">${poly(pts)}</clipPath>`,
    poly(pts, { fill: c }),
    path(strata.join(' '), { stroke: darken(c, 0.2), 'stroke-width': 3, fill: 'none', 'clip-path': `url(#${id})`, opacity: 0.7 }),
  );
}

export function waterBody(d: Defs, p: Palette, pts: [number, number][], seed: number): string {
  const rand = rng(seed);
  const xs = pts.map((q) => q[0]);
  const ys = pts.map((q) => q[1]);
  const ripples: string[] = [];
  for (let i = 0; i < 22; i++) {
    const x = Math.min(...xs) + rand() * (Math.max(...xs) - Math.min(...xs));
    const y = Math.min(...ys) + 10 + rand() * (Math.max(...ys) - Math.min(...ys) - 20);
    ripples.push(`M${r1(x)} ${r1(y)} h${r1(20 + rand() * 50)}`);
  }
  const id = `wclip${seed}`;
  return g(
    { class: 'water' },
    `<clipPath id="${id}">${poly(pts)}</clipPath>`,
    poly(pts, { fill: d.linear('water', [[0, p.waterLight], [0.25, p.water], [1, darken(p.water, 0.2)]]) }),
    path(ripples.join(' '), { stroke: p.waterLight, 'stroke-width': 2.5, 'stroke-linecap': 'round', opacity: 0.7, 'clip-path': `url(#${id})`, class: 'ripples' }),
  );
}

export function tablet(p: Palette, x: number, y: number, w: number, h: number): string {
  return g({}, rect(x, y - h, w, h, { fill: p.stoneLight, rx: 4 }), rect(x + 5, y - h + 5, w - 10, h - 10, { fill: 'none', stroke: p.stoneDark, 'stroke-width': 2, rx: 3 }));
}
