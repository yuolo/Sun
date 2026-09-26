import type { FigureSpec } from '../core/types';
import { darken, lighten } from './color';
import { circle, ellipse, g, line, path, rect } from './svg';

const SKIN = '#e2bf98';
const HAIR = '#1d1a18';
const SHOE = '#2a2320';

/**
 * A figure drawn with its feet at (0, 0), facing right, about 200 units tall.
 * Returned markup is an SVG <g>; the caller positions and flips it.
 */
export function figure(spec: FigureSpec): string {
  const s = spec.scale ?? 1;
  const sit = spec.pose === 'sit';
  const robe = spec.robe;
  const trim = spec.trim ?? darken(robe, 0.35);
  const skin = spec.skin ?? SKIN;
  const hatColor = spec.hatColor ?? HAIR;
  const parts: string[] = [ellipse(0, 0, 40, 7, { fill: 'rgba(0,0,0,0.22)', class: 'fig-shadow' })];

  let hx = 3;
  let hy = -168;
  let hand: [number, number] = [22, -70];

  if (sit) {
    hy = -120;
    hand = [34, -52];
    parts.push(
      rect(-24, -38, 48, 8, { fill: '#6b4a2c' }),
      rect(-20, -30, 6, 30, { fill: '#4a3320' }),
      rect(14, -30, 6, 30, { fill: '#4a3320' }),
      rect(26, -40, 20, 36, { fill: darken(robe, 0.2) }),
      ellipse(40, -4, 12, 5, { fill: SHOE }),
      path('M-30 -48 L44 -48 Q52 -40 46 -30 L-30 -30 Z', { fill: robe }),
      path('M-22 -100 C-28 -82 -32 -62 -30 -40 L30 -40 C30 -62 26 -82 20 -100 Z', { fill: robe }),
      path('M-22 -100 C-28 -82 -32 -62 -30 -40 L-14 -40 C-14 -62 -12 -84 -6 -100 Z', { fill: '#000', opacity: 0.12 }),
      rect(-28, -76, 56, 8, { fill: trim }),
      path('M-12 -102 L10 -72', { stroke: trim, 'stroke-width': 5, fill: 'none' }),
      path('M12 -98 C28 -86 36 -70 38 -54 L22 -50 C20 -66 14 -82 6 -94 Z', { fill: darken(robe, 0.08) }),
      path('M22 -50 L38 -54', { stroke: trim, 'stroke-width': 4 }),
      rect(-5, -112, 10, 12, { fill: skin }),
    );
  } else {
    parts.push(
      g({ class: 'feet' }, ellipse(-10, -4, 12, 5, { fill: SHOE, class: 'foot-l' }), ellipse(14, -4, 12, 5, { fill: SHOE, class: 'foot-r' })),
      path('M-24 -148 C-30 -110 -40 -50 -44 -8 Q0 0 46 -8 C42 -50 32 -110 24 -148 Z', { fill: robe }),
      path('M-24 -148 C-30 -110 -40 -50 -44 -8 Q-32 -4 -18 -6 C-16 -60 -14 -110 -8 -148 Z', { fill: '#000', opacity: 0.12 }),
      path('M-44 -9 Q0 -1 46 -9', { stroke: trim, 'stroke-width': 6, fill: 'none' }),
      rect(-26, -102, 52, 9, { fill: trim }),
      path('M18 -94 l6 30 l-8 0 z', { fill: trim }),
      path('M-14 -150 L12 -104', { stroke: trim, 'stroke-width': 5, fill: 'none' }),
      path('M14 -146 C30 -130 36 -100 32 -74 L12 -70 C10 -96 8 -122 4 -142 Z', { fill: darken(robe, 0.08) }),
      path('M12 -71 L32 -75', { stroke: trim, 'stroke-width': 5 }),
      rect(-5, -160, 10, 14, { fill: skin }),
    );
  }

  const [px, py] = hand;
  const props: string[] = [];
  switch (spec.prop) {
    case 'oar':
      props.push(line(-60, -250, 70, 40, { stroke: '#7a5634', 'stroke-width': 6, 'stroke-linecap': 'round' }));
      break;
    case 'pole':
      if (!sit) {
        props.push(
          line(-90, -150, 90, -150, { stroke: '#8a6a3a', 'stroke-width': 7, 'stroke-linecap': 'round' }),
          line(-78, -150, -78, -96, { stroke: '#5a4a32', 'stroke-width': 2 }),
          line(78, -150, 78, -96, { stroke: '#5a4a32', 'stroke-width': 2 }),
          path('M-100 -96 L-56 -96 L-62 -52 L-94 -52 Z', { fill: '#b89458' }),
          path('M56 -96 L100 -96 L94 -52 L62 -52 Z', { fill: '#b89458' }),
          path('M-98 -84 H-58 M-96 -68 H-60 M58 -84 H98 M60 -68 H96', { stroke: '#7a5e32', 'stroke-width': 2 }),
        );
      }
      break;
    case 'staff':
      props.push(line(px + 12, py - 110, px + 16, sit ? -2 : 0, { stroke: '#7a5634', 'stroke-width': 5, 'stroke-linecap': 'round' }), circle(px + 12, py - 112, 5, { fill: '#5a3e24' }));
      break;
    case 'spear':
      props.push(
        line(px + 16, -262, px + 16, 0, { stroke: '#5a3e24', 'stroke-width': 5 }),
        path(`M${px + 16} -292 l7 22 l-14 0 z`, { fill: '#c8ccd2' }),
        path(`M${px + 10} -268 q6 16 12 0 q-2 14 -6 20 q-4 -6 -6 -20z`, { fill: '#c0392b' }),
      );
      break;
    case 'lantern':
    case 'lanternDark': {
      const lit = spec.prop === 'lantern';
      props.push(
        line(px, py, px + 22, py - 34, { stroke: '#5a3e24', 'stroke-width': 3 }),
        line(px + 22, py - 34, px + 22, py - 22, { stroke: '#222', 'stroke-width': 1.5 }),
        lit ? circle(px + 22, py - 4, 38, { fill: '#ffb060', opacity: 0.28, class: 'glow' }) : '',
        ellipse(px + 22, py - 6, 12, 15, { fill: lit ? '#f06a3a' : '#6a3a30' }),
        rect(px + 15, py - 23, 14, 4, { fill: '#222' }),
        rect(px + 15, py + 8, 14, 4, { fill: '#222' }),
      );
      break;
    }
    case 'bucket':
      props.push(path(`M${px - 10} ${py + 4} L${px - 7} ${py + 30} L${px + 13} ${py + 30} L${px + 16} ${py + 4} Z`, { fill: '#9a6c42' }));
      break;
    case 'gourd':
      props.push(circle(-18, sit ? -68 : -88, 7, { fill: '#c9a052' }), circle(-18, sit ? -56 : -76, 10, { fill: '#c9a052' }), line(-18, sit ? -76 : -96, -14, sit ? -78 : -98, { stroke: '#7a3a2a', 'stroke-width': 3 }));
      break;
    case 'fan':
      props.push(line(px, py, px + 10, py - 36, { stroke: '#5a3e24', 'stroke-width': 3 }), path(`M${px + 10} ${py - 36} q12 20 4 44 q-6 -18 -10 -8 q2 -20 6 -36z`, { fill: '#f2efe6' }));
      break;
    case 'scroll':
      props.push(rect(px - 4, py - 6, 30, 10, { fill: '#e8dcc0', rx: 4 }), rect(px - 6, py - 7, 5, 12, { fill: '#8a5a3a' }), rect(px + 25, py - 7, 5, 12, { fill: '#8a5a3a' }));
      break;
    default:
      break;
  }

  parts.push(circle(px, py + 2, 5, { fill: skin }));

  /* head */
  const head: string[] = [];
  if (spec.hat === 'hood') {
    const hood = spec.hatColor ?? darken(robe, 0.2);
    head.push(
      path(`M${hx - 22} ${hy + 24} C${hx - 30} ${hy - 4} ${hx - 18} ${hy - 24} ${hx + 2} ${hy - 24} C${hx + 22} ${hy - 24} ${hx + 26} ${hy - 6} ${hx + 22} ${hy + 20} Z`, { fill: hood }),
      ellipse(hx + 6, hy + 2, 10, 12, { fill: skin }),
      circle(hx + 11, hy - 1, 1.8, { fill: '#2a1f1a' }),
    );
  } else {
    head.push(circle(hx, hy, 16, { fill: skin }), circle(hx + 9, hy - 2, 1.8, { fill: '#2a1f1a' }), path(`M${hx - 16} ${hy + 2} a16 16 0 0 0 10 13`, { stroke: darken(skin, 0.15), 'stroke-width': 3, fill: 'none' }));
  }
  if (spec.beard) {
    head.push(path(`M${hx - 2} ${hy + 10} Q${hx + 14} ${hy + 14} ${hx + 12} ${hy + 8} Q${hx + 14} ${hy + 30} ${hx + 6} ${hy + 44} Q${hx - 2} ${hy + 28} ${hx - 2} ${hy + 10} Z`, { fill: '#d8d2c4' }));
  }
  const hairCap = path(`M${hx - 16} ${hy + 2} Q${hx - 18} ${hy - 18} ${hx} ${hy - 17} Q${hx + 14} ${hy - 17} ${hx + 15} ${hy - 6} Q${hx + 4} ${hy - 12} ${hx - 6} ${hy - 4} Q${hx - 10} ${hy + 2} ${hx - 12} ${hy + 8} Z`, { fill: HAIR });
  switch (spec.hat) {
    case 'straw':
      head.push(
        path(`M${hx - 52} ${hy - 4} L${hx} ${hy - 36} L${hx + 52} ${hy - 4} Q${hx} ${hy + 2} ${hx - 52} ${hy - 4} Z`, { fill: spec.hatColor ?? '#d8b36a' }),
        path(`M${hx} ${hy - 36} L${hx - 30} ${hy - 2} M${hx} ${hy - 36} L${hx - 10} ${hy} M${hx} ${hy - 36} L${hx + 12} ${hy} M${hx} ${hy - 36} L${hx + 32} ${hy - 2}`, { stroke: darken(spec.hatColor ?? '#d8b36a', 0.2), 'stroke-width': 1.5 }),
        line(hx - 10, hy - 2, hx + 2, hy + 16, { stroke: '#5a4a32', 'stroke-width': 1.2 }),
      );
      break;
    case 'wide':
      head.push(ellipse(hx, hy - 9, 44, 8, { fill: hatColor }), path(`M${hx - 18} ${hy - 9} Q${hx - 18} ${hy - 32} ${hx} ${hy - 32} Q${hx + 18} ${hy - 32} ${hx + 18} ${hy - 9} Z`, { fill: darken(hatColor, 0.1) }), rect(hx - 18, hy - 14, 36, 5, { fill: '#b8302a' }));
      break;
    case 'cap':
      head.push(
        path(`M${hx - 17} ${hy - 1} Q${hx - 19} ${hy - 26} ${hx} ${hy - 26} Q${hx + 18} ${hy - 26} ${hx + 17} ${hy - 4} Z`, { fill: hatColor }),
        circle(hx - 6, hy - 26, 8, { fill: hatColor }),
        path(`M${hx - 14} ${hy - 10} q-14 4 -22 18`, { stroke: hatColor, 'stroke-width': 4, fill: 'none', 'stroke-linecap': 'round' }),
      );
      break;
    case 'topknot':
      head.push(hairCap, circle(hx - 2, hy - 21, 8, { fill: HAIR }), line(hx - 14, hy - 24, hx + 10, hy - 18, { stroke: spec.hatColor && spec.hatColor !== HAIR ? spec.hatColor : '#c9a86a', 'stroke-width': 2.5 }));
      break;
    case 'bun':
      head.push(hairCap, circle(hx - 14, hy - 10, 10, { fill: HAIR }), line(hx - 26, hy - 16, hx - 4, hy - 4, { stroke: '#c9a86a', 'stroke-width': 2 }));
      break;
    case 'twinbuns':
      head.push(hairCap, circle(hx - 12, hy - 17, 7, { fill: HAIR }), circle(hx + 9, hy - 19, 7, { fill: HAIR }), rect(hx - 16, hy - 13, 8, 3, { fill: '#c0392b' }));
      break;
    case 'scholar':
      head.push(path(`M${hx - 17} ${hy - 4} L${hx - 15} ${hy - 36} L${hx + 15} ${hy - 36} L${hx + 17} ${hy - 4} Z`, { fill: hatColor }), line(hx - 15, hy - 22, hx + 15, hy - 22, { stroke: lighten(hatColor, 0.2), 'stroke-width': 1.5 }), path(`M${hx - 16} ${hy - 6} q-12 10 -16 26`, { stroke: hatColor, 'stroke-width': 3, fill: 'none' }));
      break;
    case 'guard':
      head.push(
        path(`M${hx - 18} ${hy - 2} Q${hx - 18} ${hy - 30} ${hx} ${hy - 30} Q${hx + 18} ${hy - 30} ${hx + 18} ${hy - 2} Z`, { fill: hatColor }),
        rect(hx - 22, hy - 6, 44, 6, { fill: '#8a2a22', rx: 2 }),
        line(hx, hy - 30, hx, hy - 42, { stroke: '#c9a86a', 'stroke-width': 3 }),
        path(`M${hx} ${hy - 42} q-8 4 -14 16 q10 -4 14 -6 q4 2 10 6 q-2 -10 -10 -16z`, { fill: '#c0392b' }),
      );
      break;
    case 'bald':
      head.push(path(`M${hx - 8} ${hy - 12} a10 10 0 0 1 10 -3`, { stroke: lighten(skin, 0.35), 'stroke-width': 3, fill: 'none', 'stroke-linecap': 'round' }));
      break;
    case 'hood':
      break;
    default:
      head.push(hairCap);
  }
  parts.push(g({ class: 'fig-head' }, ...head), ...props);
  return g({ transform: s === 1 ? undefined : `scale(${s})`, class: 'fig' }, ...parts);
}

/** Approximate figure height (for placing bubbles). */
export function figureHeight(spec: FigureSpec): number {
  const s = spec.scale ?? 1;
  const base = spec.pose === 'sit' ? 150 : 205;
  const hat = spec.hat === 'straw' || spec.hat === 'scholar' || spec.hat === 'guard' ? 20 : 8;
  return (base + hat) * s;
}
