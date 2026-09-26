import { figure, figureHeight } from '../src/art/figures';
import { ancientForm } from '../src/art/ancient';
import { illustration, ITEM_ICONS, BELL_ICONS } from '../src/art/illustrations';
import { SCENES } from '../src/content/world';
import { createState } from '../src/core/state';
import { num } from '../src/core/interact';
import { LEXICON } from '../src/content/lexicon';

const root = document.getElementById('root')!;
const params = new URLSearchParams(location.search);
const only = params.get('scene');
const state = createState();
for (const f of (params.get('flags') ?? '').split(',').filter(Boolean)) state.flags[f] = true;

for (const scene of SCENES) {
  if (only && scene.id !== only) continue;
  const look = scene.look(state);
  const wrap = document.createElement('div');
  wrap.className = 'scene';
  wrap.id = `scene-${scene.id}`;
  let figs = '';
  for (const a of scene.actors) {
    if (a.visible && !a.visible(state)) continue;
    const spec = typeof a.figure === 'function' ? a.figure(state) : a.figure;
    const facing = typeof a.facing === 'function' ? a.facing(state) : a.facing ?? 'right';
    figs += `<g transform="translate(${num(a.x, state)} ${num(a.y, state)}) scale(${facing === 'left' ? -1 : 1} 1)">${figure(spec)}</g>`;
    void figureHeight;
  }
  const signs = scene.signs.map((s) => `<text x="${s.x}" y="${s.y}" font-size="${s.size ?? 32}" text-anchor="middle" dominant-baseline="middle" fill="#fff" stroke="#000" stroke-width="1" ${s.vertical ? 'writing-mode="tb"' : ''}>${s.lines.join(' ')}</text>`).join('');
  const path = `<polyline points="${scene.path.map((p) => p.join(',')).join(' ')}" fill="none" stroke="magenta" stroke-width="2" stroke-dasharray="6 6"/>`;
  const hot = scene.hotspots.map((h) => `<rect x="${h.rect[0]}" y="${h.rect[1]}" width="${h.rect[2]}" height="${h.rect[3]}" fill="none" stroke="yellow" stroke-width="2"/>`).join('');
  const exits = scene.exits.map((h) => `<rect x="${h.rect[0]}" y="${h.rect[1]}" width="${h.rect[2]}" height="${h.rect[3]}" fill="none" stroke="cyan" stroke-width="2"/>`).join('');
  const overlay = params.has('debug') ? path + hot + exits : '';
  const bg = scene.art(state, look);
  const cut = bg.lastIndexOf('</svg>');
  wrap.innerHTML = bg.slice(0, cut) + `${figs}${signs}${overlay}</svg>` + (scene.front ? `<div style="position:absolute;inset:0">${scene.front(state, look)}</div>` : '');
  root.append(Object.assign(document.createElement('h2'), { textContent: `${scene.id} · ${scene.title} (${look.time})` }), wrap);
}

if (!only) {
  const icons = document.createElement('div');
  icons.className = 'icons';
  icons.id = 'icons';
  for (const g of LEXICON) {
    icons.insertAdjacentHTML('beforeend', `<div><svg viewBox="0 0 100 100">${illustration(g.ch)}</svg><br>${g.ch} ${ancientForm(g.ch) ? '<span style="display:inline-block;width:30px;height:30px;color:#6a4a2a">' + ancientForm(g.ch) + '</span>' : ''}</div>`);
  }
  for (const [k, v] of Object.entries(ITEM_ICONS)) icons.insertAdjacentHTML('beforeend', `<div><svg viewBox="0 0 100 100">${v}</svg><br>${k}</div>`);
  for (const [k, v] of Object.entries(BELL_ICONS)) icons.insertAdjacentHTML('beforeend', `<div><svg viewBox="0 0 100 100" style="background:#9a7a3a">${v}</svg><br>${k}</div>`);
  root.append(icons);
}
