/** Small helpers for building SVG markup as strings. */

export const W = 1600;
export const H = 900;

export type Attrs = Record<string, string | number | undefined | null | false>;

export function attrs(a: Attrs): string {
  let out = '';
  for (const [k, v] of Object.entries(a)) {
    if (v === undefined || v === null || v === false) continue;
    out += ` ${k}="${String(v).replace(/"/g, '&quot;')}"`;
  }
  return out;
}

export const el = (tag: string, a: Attrs, inner = ''): string =>
  inner ? `<${tag}${attrs(a)}>${inner}</${tag}>` : `<${tag}${attrs(a)}/>`;

export const g = (a: Attrs, ...children: string[]): string => `<g${attrs(a)}>${children.join('')}</g>`;
export const path = (d: string, a: Attrs = {}): string => el('path', { d, ...a });
export const rect = (x: number, y: number, w: number, h: number, a: Attrs = {}): string =>
  el('rect', { x: r1(x), y: r1(y), width: r1(w), height: r1(h), ...a });
export const circle = (cx: number, cy: number, r: number, a: Attrs = {}): string =>
  el('circle', { cx: r1(cx), cy: r1(cy), r: r1(r), ...a });
export const ellipse = (cx: number, cy: number, rx: number, ry: number, a: Attrs = {}): string =>
  el('ellipse', { cx: r1(cx), cy: r1(cy), rx: r1(rx), ry: r1(ry), ...a });
export const line = (x1: number, y1: number, x2: number, y2: number, a: Attrs = {}): string =>
  el('line', { x1: r1(x1), y1: r1(y1), x2: r1(x2), y2: r1(y2), ...a });
export const poly = (pts: [number, number][], a: Attrs = {}): string =>
  el('polygon', { points: pts.map(([x, y]) => `${r1(x)},${r1(y)}`).join(' '), ...a });

export function r1(n: number): number {
  return Math.round(n * 10) / 10;
}

export function linear(id: string, stops: [number, string][], vertical = true): string {
  const dir = vertical ? { x1: 0, y1: 0, x2: 0, y2: 1 } : { x1: 0, y1: 0, x2: 1, y2: 0 };
  return el(
    'linearGradient',
    { id, ...dir },
    stops.map(([o, c]) => el('stop', { offset: o, 'stop-color': c })).join(''),
  );
}

export function radial(id: string, stops: [number, string, number?][]): string {
  return el(
    'radialGradient',
    { id },
    stops.map(([o, c, op]) => el('stop', { offset: o, 'stop-color': c, 'stop-opacity': op ?? 1 })).join(''),
  );
}

/** Deterministic pseudo random generator. */
export function rng(seed: number): () => number {
  let s = seed >>> 0 || 1;
  return () => {
    s = (Math.imul(s, 1664525) + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

/** Smooth path through points (Catmull-Rom → cubic Bézier). */
export function smooth(pts: [number, number][], closed = false): string {
  if (pts.length < 2) return '';
  let d = `M${r1(pts[0][0])} ${r1(pts[0][1])}`;
  const n = pts.length;
  for (let i = 0; i < n - 1 + (closed ? 1 : 0); i++) {
    const p0 = pts[(i - 1 + n) % n];
    const p1 = pts[i % n];
    const p2 = pts[(i + 1) % n];
    const p3 = pts[(i + 2) % n];
    const a0 = closed || i > 0 ? p0 : p1;
    const a3 = closed || i < n - 2 ? p3 : p2;
    const c1x = p1[0] + (p2[0] - a0[0]) / 6;
    const c1y = p1[1] + (p2[1] - a0[1]) / 6;
    const c2x = p2[0] - (a3[0] - p1[0]) / 6;
    const c2y = p2[1] - (a3[1] - p1[1]) / 6;
    d += ` C${r1(c1x)} ${r1(c1y)} ${r1(c2x)} ${r1(c2y)} ${r1(p2[0])} ${r1(p2[1])}`;
  }
  return closed ? d + 'Z' : d;
}

export function svgDoc(inner: string, defs = '', viewBox = `0 0 ${W} ${H}`): string {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${viewBox}" preserveAspectRatio="xMidYMid slice">${defs ? `<defs>${defs}</defs>` : ''}${inner}</svg>`;
}
