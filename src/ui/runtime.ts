import { figure, figureHeight } from '../art/figures';
import { ITEM_ICONS } from '../art/illustrations';
import { PLAYER_FIGURE } from '../content/chapters/common';
import { itemDef } from '../content/items';
import { CHAPTERS, sceneById } from '../content/world';
import { clickHotspot, enterScene, num, recordLine, takeExit, talkTo, useItemOn, visibleActors, visibleExits, visibleHotspots, visibleSigns, actorStand } from '../core/interact';
import { confirmGlyphs, see } from '../core/journal';
import { WalkPath } from '../core/path';
import { START } from '../core/state';
import type { ActorDef, Chapter, ComposeRequest, Cup, FigureSpec, FlagValue, GameState, Glyph, PuzzleId, SceneDef, SceneLook, ScriptContext } from '../core/types';
import type { App } from './app';
import { openComposer } from './composer-ui';
import { h, icon, sleep, svgEl } from './dom';
import { Rain, applyLight, moveLight } from './fx';
import { phraseEl } from './glyph';
import { journalIcon } from './journal-ui';
import { modalOpen } from './modal';
import { chapterCard, showEnding } from './menu';
import { openAncient, openBells, openCompose, openStele, openTray } from './puzzles-ui';

interface ActorView {
  id: string;
  el: HTMLElement;
  x: number;
  y: number;
  facing: 'left' | 'right';
  spec: FigureSpec;
}

const WALK_SPEED = 360;
const NPC_SPEED = 240;

export class Runtime implements ScriptContext {
  readonly app: App;
  scene!: SceneDef;
  look!: SceneLook;
  path!: WalkPath;

  private viewport: HTMLElement;
  private stage: HTMLElement;
  private bg: HTMLElement;
  private signsLayer: HTMLElement;
  private hot: HTMLElement;
  private actorsLayer: HTMLElement;
  private front: HTMLElement;
  private light: HTMLElement;
  private mist: HTMLElement;
  private marks: HTMLElement;
  private catcher: HTMLElement;
  private bubbles: HTMLElement;
  private caption: HTMLElement;
  private curtainEl: HTMLElement;
  private hud: HTMLElement;
  private inv: HTMLElement;
  private tooltip: HTMLElement;
  private cursorItem: HTMLElement;
  private rain: Rain;

  private actors = new Map<string, ActorView>();
  private player!: ActorView;
  private activeBubbles: { el: HTMLElement; view: ActorView }[] = [];
  private busy = false;
  private selectedItem: string | null = null;
  private walkToken = 0;
  private lastArt = '';
  private k = 1;
  private ox = 0;
  private oy = 0;
  private cleanup: (() => void)[] = [];

  onMainMenu: () => void = () => {};
  onPause: () => void = () => {};

  constructor(app: App, host: HTMLElement) {
    this.app = app;
    this.bg = h('div', { class: 'layer bg' });
    this.signsLayer = h('div', { class: 'layer signs' });
    this.hot = h('div', { class: 'layer hot' });
    this.actorsLayer = h('div', { class: 'layer actors' });
    this.front = h('div', { class: 'layer front' });
    const rainCanvas = h('canvas', { class: 'layer rain' });
    this.rain = new Rain(rainCanvas);
    this.mist = h('div', { class: 'layer mist' });
    this.light = h('div', { class: 'layer light' });
    this.marks = h('div', { class: 'layer marks' });
    this.stage = h('div', { class: 'stage' }, this.bg, this.signsLayer, this.hot, this.actorsLayer, this.front, rainCanvas, this.mist, this.light, this.marks);
    this.catcher = h('div', { class: 'catcher' });
    this.bubbles = h('div', { class: 'bubbles' });
    this.caption = h('div', { class: 'caption', role: 'status' });
    this.curtainEl = h('div', { class: 'curtain on' });
    this.viewport = h('div', { class: 'viewport' }, this.stage, this.catcher, this.bubbles, this.caption, this.curtainEl);

    const btn = (label: string, key: string, content: Node | string, onclick: () => void, cls = '') => h('button', { class: `hud-btn ${cls}`, title: `${label} (${key})`, 'aria-label': label, onclick }, content);
    this.hud = h(
      'div',
      { class: 'hud' },
      btn('Дневник', 'J', journalIcon(), () => this.app.openJournal(), 'journal-btn'),
      btn('Подсказка', 'H', '?', () => this.app.showHint()),
      btn('Меню', 'Esc', '☰', () => this.onPause()),
    );
    this.inv = h('div', { class: 'inventory', 'aria-label': 'Сумка' });
    this.tooltip = h('div', { class: 'tooltip' });
    this.cursorItem = h('div', { class: 'cursor-item' });
    host.append(this.viewport, this.hud, this.inv, this.tooltip, this.cursorItem);

    this.bindInput();
    const onResize = () => this.fit();
    window.addEventListener('resize', onResize);
    this.cleanup.push(() => window.removeEventListener('resize', onResize));
    this.fit();
  }

  get state(): GameState {
    return this.app.state;
  }

  destroy(): void {
    this.rain.kill();
    for (const f of this.cleanup) f();
    for (const el of [this.viewport, this.hud, this.inv, this.tooltip, this.cursorItem]) el.remove();
    document.body.classList.remove('using-item');
  }

  /* ================================================================ */
  /* Layout                                                           */
  /* ================================================================ */

  private fit(): void {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    this.k = Math.min(vw / 1600, vh / 900);
    this.ox = (vw - 1600 * this.k) / 2;
    this.oy = (vh - 900 * this.k) / 2;
    this.stage.style.transform = `translate(${this.ox}px, ${this.oy}px) scale(${this.k})`;
    document.documentElement.style.setProperty('--stage-k', String(this.k));
    for (const b of this.activeBubbles) this.placeBubble(b.el, b.view);
  }

  private toPage(x: number, y: number): [number, number] {
    return [this.ox + x * this.k, this.oy + y * this.k];
  }

  private toStage(cx: number, cy: number): [number, number] {
    return [(cx - this.ox) / this.k, (cy - this.oy) / this.k];
  }

  private depthScale(y: number): number {
    const d = this.scene?.depth;
    if (!d) return 1;
    const near = Math.max(...this.scene.path.map((p) => p[1]));
    const [far, sFar] = d;
    const t = Math.max(0, Math.min(1, (near - y) / (near - far)));
    return 1 - t * (1 - sFar);
  }

  /* ================================================================ */
  /* Start and scenes                                                 */
  /* ================================================================ */

  async start(): Promise<void> {
    const s = this.state;
    this.scene = sceneById(s.scene);
    this.path = new WalkPath(this.scene.path);
    if (s.px < 0) s.px = this.path.atX(this.scene.entries[START.entry] ?? this.scene.path[0][0]);
    this.renderScene();
    this.app.audio.setMood(this.scene.chapter);
    await this.curtain(false);
    this.busy = true;
    try {
      this.markSigns();
      await enterScene(this, this.scene);
    } finally {
      this.busy = false;
      this.afterInteraction();
    }
  }

  private markSigns(): void {
    const fresh: Glyph[] = [];
    for (const sign of visibleSigns(this.scene, this.state)) fresh.push(...see(this.state, sign.lines.join('')));
    if (fresh.length) this.app.announce(fresh);
  }

  private renderScene(): void {
    const s = this.state;
    this.look = this.scene.look(s);
    this.lastArt = this.scene.art(s, this.look);
    this.bg.innerHTML = this.lastArt;
    this.front.innerHTML = this.scene.front ? this.scene.front(s, this.look) : '';
    document.body.dataset.time = this.look.time;
    this.renderDynamic();
    this.applyLook();
    this.placePlayer();
  }

  private applyLook(): void {
    applyLight(this.light, this.look, this.has('lantern'));
    if (this.look.rain) this.rain.start();
    else this.rain.stop();
    this.mist.classList.toggle('on', !!this.look.mist);
  }

  /** Redraw what depends on state: art (if changed), signs, actors, hotspots, inventory. */
  private refresh(fade = 400): void {
    const s = this.state;
    this.look = this.scene.look(s);
    const art = this.scene.art(s, this.look);
    if (art !== this.lastArt) {
      this.lastArt = art;
      if (fade > 0) {
        const old = this.bg.firstElementChild as HTMLElement | null;
        const holder = h('div', { class: 'bg-old', html: this.bg.innerHTML });
        this.stage.insertBefore(holder, this.bg.nextSibling);
        this.bg.innerHTML = art;
        holder.style.transition = `opacity ${fade}ms`;
        requestAnimationFrame(() => (holder.style.opacity = '0'));
        setTimeout(() => holder.remove(), fade + 50);
        void old;
      } else this.bg.innerHTML = art;
      this.front.innerHTML = this.scene.front ? this.scene.front(s, this.look) : '';
    }
    document.body.dataset.time = this.look.time;
    this.renderDynamic();
    this.applyLook();
  }

  private renderDynamic(): void {
    this.renderSigns();
    this.renderActors();
    this.renderHot();
    this.renderInventory();
  }

  private renderSigns(): void {
    this.signsLayer.replaceChildren();
    for (const sign of visibleSigns(this.scene, this.state)) {
      const el = h('div', {
        class: `sign style-${sign.style}${sign.vertical ? ' vertical' : ''}${sign.arrow ? ` arrow arrow-${sign.arrow}` : ''}`,
        style: `left:${sign.x}px;top:${sign.y}px;font-size:${sign.size ?? 36}px`,
      });
      for (const line of sign.lines) el.append(h('div', { class: 'sign-line' }, phraseEl(this.app, line, { size: 'sign' })));
      this.signsLayer.append(el);
    }
  }

  private makeView(id: string, spec: FigureSpec, x: number, y: number, facing: 'left' | 'right', label: string, isPlayer = false): ActorView {
    const hgt = figureHeight(spec);
    const hw = 46 * (spec.scale ?? 1);
    const el = h('div', { class: `actor${isPlayer ? ' player' : ''}`, 'data-id': id, 'data-label': label });
    el.append(
      svgEl(`<svg class="actor-svg" viewBox="-160 -340 320 360" width="320" height="360"><g class="flip"><g class="bob">${figure(spec)}</g></g><rect class="hit" x="${-hw}" y="${-hgt}" width="${hw * 2}" height="${hgt}" fill="transparent"/></svg>`),
    );
    const view: ActorView = { id, el, x, y, facing, spec };
    this.position(view);
    return view;
  }

  private position(v: ActorView): void {
    const sc = this.depthScale(v.y);
    v.el.style.left = `${v.x}px`;
    v.el.style.top = `${v.y}px`;
    v.el.style.zIndex = String(Math.round(v.y));
    v.el.style.transform = `scale(${sc})`;
    v.el.classList.toggle('left', v.facing === 'left');
  }

  private resolveFacing(a: ActorDef): 'left' | 'right' {
    const f = a.facing;
    return typeof f === 'function' ? f(this.state) : (f ?? 'right');
  }

  private renderActors(): void {
    for (const v of this.actors.values()) v.el.remove();
    this.actors.clear();
    for (const a of visibleActors(this.scene, this.state)) {
      const spec = typeof a.figure === 'function' ? a.figure(this.state) : a.figure;
      const v = this.makeView(a.id, spec, num(a.x, this.state), num(a.y, this.state), this.resolveFacing(a), a.name);
      this.actors.set(a.id, v);
      this.actorsLayer.append(v.el);
    }
    this.renderPlayer();
  }

  private playerSpec(): FigureSpec {
    return { ...PLAYER_FIGURE, prop: this.has('lantern') ? 'lantern' : 'staff' };
  }

  private renderPlayer(): void {
    const old = this.player;
    const [x, y] = this.path ? this.path.pointAt(this.state.px) : [0, 0];
    this.player = this.makeView('player', this.playerSpec(), x, y, old?.facing ?? 'right', 'Вы', true);
    old?.el.remove();
    this.actorsLayer.append(this.player.el);
    moveLight(this.light, x, y);
  }

  private placePlayer(): void {
    const [x, y] = this.path.pointAt(this.state.px);
    this.player.x = x;
    this.player.y = y;
    this.position(this.player);
    moveLight(this.light, x, y);
  }

  private renderHot(): void {
    this.hot.replaceChildren();
    for (const hs of visibleHotspots(this.scene, this.state)) {
      const [x, y, w, hh] = hs.rect;
      this.hot.append(h('div', { class: 'hotspot', 'data-id': hs.id, 'data-label': hs.name, style: `left:${x}px;top:${y}px;width:${w}px;height:${hh}px` }));
    }
    for (const ex of visibleExits(this.scene, this.state)) {
      const [x, y, w, hh] = ex.rect;
      this.hot.append(h('div', { class: `exit dir-${ex.dir}`, 'data-id': ex.id, 'data-label': ex.label, style: `left:${x}px;top:${y}px;width:${w}px;height:${hh}px` }, h('span', { class: 'exit-arrow' })));
    }
  }

  private renderInventory(): void {
    const s = this.state;
    this.inv.replaceChildren();
    if (s.coins > 0 || s.flags.ch2) {
      this.inv.append(h('div', { class: 'coins', title: 'Монеты' }, icon('<circle cx="50" cy="50" r="40" fill="#c8923a" stroke="#7a5420" stroke-width="6"/><rect x="38" y="38" width="24" height="24" fill="#f6ecd6" stroke="#7a5420" stroke-width="4"/>'), h('span', {}, String(s.coins))));
    }
    for (const id of s.inventory) {
      const def = itemDef(id);
      const b = h('button', { class: `item${this.selectedItem === id ? ' selected' : ''}`, title: def ? `${def.name}. ${def.description}` : id, 'aria-label': def?.name ?? id }, icon(ITEM_ICONS[id] ?? ''), h('span', { class: 'item-name' }, def?.name ?? id));
      b.addEventListener('click', (e) => {
        e.stopPropagation();
        this.selectItem(this.selectedItem === id ? null : id);
      });
      this.inv.append(b);
    }
  }

  private selectItem(id: string | null): void {
    this.selectedItem = id;
    document.body.classList.toggle('using-item', !!id);
    this.cursorItem.replaceChildren(id ? icon(ITEM_ICONS[id] ?? '') : '');
    this.renderInventory();
  }

  /* ================================================================ */
  /* Input                                                            */
  /* ================================================================ */

  private bindInput(): void {
    this.stage.addEventListener('click', (e) => this.onStageClick(e));
    const onMove = (e: PointerEvent) => {
      this.cursorItem.style.transform = `translate(${e.clientX + 12}px, ${e.clientY + 12}px)`;
      const t = e.target as Element;
      const target = t.closest?.('.actor:not(.player), .hotspot, .exit') as HTMLElement | null;
      if (target && !this.busy && e.pointerType === 'mouse') {
        this.tooltip.textContent = this.selectedItem ? `${itemDef(this.selectedItem)?.name ?? ''} → ${target.dataset.label ?? ''}` : (target.dataset.label ?? '');
        this.tooltip.style.transform = `translate(${e.clientX + 16}px, ${e.clientY - 34}px)`;
        this.tooltip.classList.add('on');
      } else this.tooltip.classList.remove('on');
    };
    window.addEventListener('pointermove', onMove);
    const onKey = (e: KeyboardEvent) => {
      if (e.defaultPrevented || e.target instanceof HTMLInputElement) return;
      if (modalOpen() || document.querySelector('.catcher.on, .chapter-card')) return;
      const k = e.key.toLowerCase();
      if (k === 'j' || k === 'о') this.app.openJournal();
      else if (k === 'h' || k === 'р') this.app.showHint();
      else if (e.key === 'Escape') {
        if (this.selectedItem) this.selectItem(null);
        else this.onPause();
      }
    };
    document.addEventListener('keydown', onKey);
    const onContext = (e: MouseEvent) => {
      if (this.selectedItem) {
        e.preventDefault();
        this.selectItem(null);
      }
    };
    window.addEventListener('contextmenu', onContext);
    this.cleanup.push(() => {
      window.removeEventListener('pointermove', onMove);
      document.removeEventListener('keydown', onKey);
      window.removeEventListener('contextmenu', onContext);
    });
  }

  private onStageClick(e: MouseEvent): void {
    if (this.busy) return;
    const t = e.target as Element;
    if (t.closest('.glyph')) return;
    const actor = t.closest('.actor:not(.player)') as HTMLElement | null;
    if (actor) return void this.interact(() => this.interactActor(actor.dataset.id!));
    const hs = t.closest('.hotspot') as HTMLElement | null;
    if (hs) return void this.interact(() => this.interactHotspot(hs.dataset.id!));
    const ex = t.closest('.exit') as HTMLElement | null;
    if (ex) return void this.interact(() => this.interactExit(ex.dataset.id!));
    if (this.selectedItem) {
      this.selectItem(null);
      return;
    }
    const [x, y] = this.toStage(e.clientX, e.clientY);
    void this.walkTo(this.path.nearest(x, y));
  }

  private async interact(fn: () => Promise<void>): Promise<void> {
    this.busy = true;
    document.body.classList.add('busy');
    this.tooltip.classList.remove('on');
    try {
      await fn();
    } catch (err) {
      console.error(err);
    } finally {
      this.busy = false;
      document.body.classList.remove('busy');
      this.afterInteraction();
    }
  }

  private afterInteraction(): void {
    this.refresh(300);
    this.app.saveNow();
  }

  private async interactActor(id: string): Promise<void> {
    const a = this.scene.actors.find((x) => x.id === id);
    if (!a) return;
    const [ax, ay] = [num(a.x, this.state), num(a.y, this.state)];
    await this.walkTo(this.path.nearest(actorStand(a, this.state), ay));
    this.face(ax);
    const item = this.selectedItem;
    if (item) {
      this.selectItem(null);
      const handled = await useItemOn(this, this.scene, id, item);
      if (!handled) await this.emote(id, '？');
    } else await talkTo(this, this.scene, id);
  }

  private async interactHotspot(id: string): Promise<void> {
    const hs = this.scene.hotspots.find((x) => x.id === id);
    if (!hs) return;
    const [x, y, w, hh] = hs.rect;
    const stand = hs.standAt !== undefined ? num(hs.standAt, this.state) : x + w / 2;
    await this.walkTo(this.path.nearest(stand, y + hh));
    this.face(x + w / 2);
    const item = this.selectedItem;
    if (item) {
      this.selectItem(null);
      const handled = await useItemOn(this, this.scene, id, item);
      if (!handled) await this.emote('player', '？');
    } else await clickHotspot(this, this.scene, id);
  }

  private async interactExit(id: string): Promise<void> {
    const ex = this.scene.exits.find((x) => x.id === id);
    if (!ex) return;
    this.selectItem(null);
    await this.walkTo(this.path.nearest(ex.standAt, ex.rect[1] + ex.rect[3]));
    await takeExit(this, this.scene, id);
  }

  private face(x: number): void {
    this.player.facing = x < this.player.x ? 'left' : 'right';
    this.position(this.player);
  }

  walkTo(target: number): Promise<void> {
    const token = ++this.walkToken;
    const start = this.state.px;
    const end = this.path.clamp(target);
    const dist = end - start;
    if (Math.abs(dist) < 3) return Promise.resolve();
    const duration = (Math.abs(dist) / WALK_SPEED) * 1000;
    const t0 = performance.now();
    this.player.el.classList.add('walking');
    let lastX = this.player.x;
    return new Promise((resolve) => {
      const step = (now: number) => {
        if (token !== this.walkToken) return resolve();
        const k = Math.min(1, (now - t0) / duration);
        this.state.px = start + dist * k;
        const [x, y] = this.path.pointAt(this.state.px);
        if (Math.abs(x - lastX) > 0.5) this.player.facing = x < lastX ? 'left' : 'right';
        lastX = x;
        this.player.x = x;
        this.player.y = y;
        this.position(this.player);
        moveLight(this.light, x, y);
        if (k < 1) requestAnimationFrame(step);
        else {
          this.player.el.classList.remove('walking');
          resolve();
        }
      };
      requestAnimationFrame(step);
    });
  }

  /* ================================================================ */
  /* Bubbles                                                          */
  /* ================================================================ */

  private viewOf(actor: string): ActorView {
    if (actor === 'player') return this.player;
    return this.actors.get(actor) ?? this.player;
  }

  private placeBubble(el: HTMLElement, v: ActorView): void {
    const sc = this.depthScale(v.y);
    const [px, py] = this.toPage(v.x, v.y - figureHeight(v.spec) * sc - 14);
    const w = el.offsetWidth;
    const vw = window.innerWidth;
    let left = px - w / 2;
    left = Math.max(8, Math.min(vw - w - 8, left));
    const top = Math.max(8 + el.offsetHeight, py);
    el.style.left = `${left}px`;
    el.style.top = `${top}px`;
    el.style.setProperty('--tail', `${Math.max(16, Math.min(w - 16, px - left))}px`);
  }

  private showBubble(v: ActorView, text: string, cls = ''): HTMLElement {
    const el = h('div', { class: `bubble ${cls}` }, phraseEl(this.app, text, { size: 'bubble' }));
    this.bubbles.append(el);
    const entry = { el, view: v };
    this.activeBubbles.push(entry);
    this.placeBubble(el, v);
    requestAnimationFrame(() => el.classList.add('show'));
    return el;
  }

  private hideBubble(el: HTMLElement): void {
    this.activeBubbles = this.activeBubbles.filter((b) => b.el !== el);
    el.classList.remove('show');
    setTimeout(() => el.remove(), 180);
  }

  private waitAdvance(extra?: HTMLElement): Promise<void> {
    return new Promise((resolve) => {
      this.catcher.classList.add('on');
      const done = () => {
        this.catcher.classList.remove('on');
        this.catcher.removeEventListener('click', onClick);
        extra?.removeEventListener('click', onExtra);
        document.removeEventListener('keydown', onKey);
        resolve();
      };
      const onClick = () => done();
      const onExtra = (e: Event) => {
        if (!(e.target as Element).closest('.glyph')) done();
      };
      const onKey = (e: KeyboardEvent) => {
        if (modalOpen() || e.target instanceof HTMLInputElement) return;
        if (e.key === ' ' || e.key === 'Enter') {
          e.preventDefault();
          done();
        }
      };
      this.catcher.addEventListener('click', onClick);
      extra?.addEventListener('click', onExtra);
      document.addEventListener('keydown', onKey);
    });
  }

  private async emote(actor: string, sign: string): Promise<void> {
    const el = this.showBubble(this.viewOf(actor), sign, 'emote');
    await sleep(900);
    this.hideBubble(el);
  }

  /* ================================================================ */
  /* ScriptContext                                                    */
  /* ================================================================ */

  flag(name: string): FlagValue | undefined {
    return this.state.flags[name];
  }

  set(name: string, value: FlagValue = true): void {
    this.state.flags[name] = value;
  }

  has(item: string): boolean {
    return this.state.inventory.includes(item);
  }

  give(item: string): void {
    if (this.has(item)) return;
    this.state.inventory.push(item);
    this.app.audio.sfx('item');
    const def = itemDef(item);
    this.app.toast(h('span', { class: 'toast-item' }, icon(ITEM_ICONS[item] ?? ''), ` ${def?.name ?? item}`), 'item');
    this.renderInventory();
    if (item === 'lantern') {
      this.renderPlayer();
      this.applyLook();
    }
  }

  take(item: string): void {
    this.state.inventory = this.state.inventory.filter((i) => i !== item);
    if (this.selectedItem === item) this.selectItem(null);
    this.renderInventory();
  }

  addCoins(n: number): void {
    this.state.coins = Math.max(0, this.state.coins + n);
    if (n > 0) this.app.audio.sfx('coins');
    this.renderInventory();
  }

  async say(actor: string, text: string, opts?: { auto?: number }): Promise<void> {
    const fresh = see(this.state, text);
    recordLine(this.state, actor, text, this.state.scene);
    this.app.announce(fresh);
    const v = this.viewOf(actor);
    this.app.audio.speak(text.replace(/[…]/g, ''), opts?.auto ? 1 : 0.85);
    const el = this.showBubble(v, text, opts?.auto ? 'quick' : '');
    if (opts?.auto) await sleep(opts.auto);
    else await this.waitAdvance(el);
    this.hideBubble(el);
  }

  async talk(lines: [string, string][]): Promise<void> {
    for (const [a, t] of lines) await this.say(a, t);
  }

  async narrate(text: string): Promise<void> {
    this.caption.replaceChildren(h('span', {}, text), h('span', { class: 'next' }, '▸'));
    this.caption.classList.add('on');
    await this.waitAdvance(this.caption);
    this.caption.classList.remove('on');
  }

  async ask(actor: string, question: string): Promise<string> {
    const fresh = see(this.state, question);
    recordLine(this.state, actor, question, this.state.scene);
    this.app.announce(fresh);
    this.app.audio.speak(question, 0.85);
    const el = this.showBubble(this.viewOf(actor), question, 'question');
    const answer = await openComposer(this.app, { title: 'Ваш ответ', question, submit: 'Сказать', cancel: 'Промолчать', max: 6 });
    this.hideBubble(el);
    if (answer) {
      this.app.audio.speak(answer, 0.85);
      const mine = this.showBubble(this.player, answer, 'mine');
      await sleep(1100);
      this.hideBubble(mine);
    }
    return answer;
  }

  puzzle(id: 'tray'): Promise<Cup[] | null>;
  puzzle(id: 'bells'): Promise<boolean>;
  puzzle(id: 'compose', req: ComposeRequest): Promise<Glyph[]>;
  puzzle(id: 'stele'): Promise<string>;
  puzzle(id: 'ancient'): Promise<boolean>;
  async puzzle(id: PuzzleId, req?: ComposeRequest): Promise<unknown> {
    switch (id) {
      case 'tray':
        return openTray(this.app);
      case 'bells':
        return openBells(this.app);
      case 'compose':
        return openCompose(this.app, req!);
      case 'stele':
        return openStele(this.app);
      case 'ancient':
        return openAncient(this.app);
    }
  }

  async move(actor: string, x: number, y?: number): Promise<void> {
    const v = this.actors.get(actor);
    if (!v) return;
    const tx = x;
    const ty = y ?? v.y;
    const sx = v.x;
    const sy = v.y;
    const dist = Math.hypot(tx - sx, ty - sy);
    if (dist < 2) return;
    v.facing = tx < sx ? 'left' : 'right';
    v.el.classList.add('walking');
    const duration = (dist / NPC_SPEED) * 1000;
    const t0 = performance.now();
    await new Promise<void>((resolve) => {
      const step = (now: number) => {
        const k = Math.min(1, (now - t0) / duration);
        v.x = sx + (tx - sx) * k;
        v.y = sy + (ty - sy) * k;
        this.position(v);
        if (k < 1) requestAnimationFrame(step);
        else resolve();
      };
      requestAnimationFrame(step);
    });
    v.el.classList.remove('walking');
    if (tx < -60 || tx > 1660) v.el.style.opacity = '0';
  }

  async goto(sceneId: string, entry: string): Promise<void> {
    await this.curtain(true);
    this.rain.kill();
    for (const b of this.activeBubbles) b.el.remove();
    this.activeBubbles = [];
    this.scene = sceneById(sceneId);
    this.path = new WalkPath(this.scene.path);
    this.state.scene = sceneId;
    this.state.px = this.path.atX(this.scene.entries[entry] ?? this.scene.path[0][0]);
    this.renderScene();
    this.app.audio.setMood(this.scene.chapter);
    this.app.saveNow();
    await this.curtain(false);
    this.markSigns();
    await enterScene(this, this.scene);
  }

  wait(ms: number): Promise<void> {
    return sleep(ms);
  }

  private async curtain(on: boolean): Promise<void> {
    this.curtainEl.classList.toggle('on', on);
    await sleep(on ? 380 : 320);
  }

  private async pointAt(name: string): Promise<void> {
    const m = this.scene.marks?.[name];
    if (!m) return;
    const el = h('div', { class: 'mark', style: `left:${m[0]}px;top:${m[1]}px` });
    this.marks.append(el);
    await sleep(900);
    setTimeout(() => el.remove(), 1400);
  }

  async event(name: string): Promise<void> {
    if (name.startsWith('point-')) return this.pointAt(name.slice(6));
    switch (name) {
      case 'sunset': {
        const sun = this.bg.querySelector<SVGGElement>('.sun');
        if (sun) {
          sun.style.transition = 'transform 2.6s ease-in, opacity 2.6s ease-in';
          sun.style.transform = 'translateY(220px)';
          sun.style.opacity = '0';
        }
        this.stage.classList.add('dimming');
        await sleep(2400);
        this.stage.classList.remove('dimming');
        break;
      }
      case 'clouds':
        this.mist.classList.add('on');
        await sleep(1400);
        break;
      case 'rain':
        this.refresh(1200);
        await sleep(1200);
        break;
      case 'rain-stop':
        this.rain.stop();
        await sleep(900);
        break;
      case 'moonrise':
        this.refresh(1800);
        await sleep(1600);
        break;
      case 'campfire':
      case 'gate-open':
        this.refresh(600);
        await sleep(600);
        break;
      case 'poet-writes':
        await this.poetWrites();
        break;
      case 'sunrise':
        await this.sunrise();
        break;
      default:
        this.refresh();
    }
  }

  private async poetWrites(): Promise<void> {
    const box = h('div', { class: 'writing' }, h('span', { class: 'w-a' }, '日'), h('span', { class: 'w-b' }, '月'), h('span', { class: 'w-c' }, '明'));
    this.viewport.append(box);
    await sleep(50);
    box.classList.add('step1');
    await sleep(1000);
    box.classList.add('step2');
    await sleep(1000);
    box.classList.add('step3');
    await sleep(1600);
    box.classList.add('out');
    await sleep(500);
    box.remove();
  }

  private async sunrise(): Promise<void> {
    this.app.audio.sfx('sunrise');
    this.refresh(3200);
    const sun = this.bg.querySelector<SVGGElement>('.sun');
    if (sun) {
      sun.style.transform = 'translateY(170px)';
      sun.getBoundingClientRect();
      sun.style.transition = 'transform 5s cubic-bezier(.2,.6,.3,1)';
      requestAnimationFrame(() => (sun.style.transform = 'translateY(0)'));
    }
    this.stage.classList.add('sunrise');
    await sleep(3600);
  }

  sfx(name: string): void {
    this.app.audio.sfx(name);
  }

  confirm(glyphs: Glyph[]): void {
    const fresh = confirmGlyphs(this.state, glyphs);
    if (fresh.length) {
      this.app.changed();
      this.app.toast(h('span', {}, 'Подтверждено: ', h('b', { class: 'zh' }, fresh.join(' '))), 'ok');
    }
  }

  async chapter(n: Chapter): Promise<void> {
    const def = CHAPTERS.find((c) => c.n === n);
    if (!def) return;
    this.app.audio.setMood(n);
    await chapterCard(this.app, this.viewport, def);
  }

  async finish(): Promise<void> {
    this.state.finished = true;
    this.app.saveNow();
    await showEnding(this.app, () => this.onMainMenu());
  }

  /* ================================================================ */
  /* Debug                                                            */
  /* ================================================================ */

  async debugGoto(sceneId: string, entry: string): Promise<void> {
    await this.interact(() => this.goto(sceneId, entry));
  }

  debugRefresh(): void {
    this.refresh(0);
  }
}
