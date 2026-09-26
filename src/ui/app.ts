import { PAGES } from '../content/pages';
import { currentHint } from '../core/hints';
import { openPages, pageStatus } from '../core/journal';
import { createState, loadFrom, saveTo, clearSave, type KeyValueStore } from '../core/state';
import type { GameState, Glyph } from '../core/types';
import { AudioEngine } from './audio';
import { openGlyphCard } from './card';
import { h } from './dom';
import { refreshAllGlyphs } from './glyph';
import { openJournal, type JournalTab } from './journal-ui';
import { openModal } from './modal';

function storage(): KeyValueStore | undefined {
  try {
    return window.localStorage;
  } catch {
    return undefined;
  }
}

/** Shared UI context: state, persistence, overlays, sound. */
export class App {
  state: GameState;
  readonly root: HTMLElement;
  readonly overlay: HTMLElement;
  readonly toasts: HTMLElement;
  readonly audio: AudioEngine;
  private saveTimer: number | null = null;
  private lastTick = performance.now();
  private knownOpenPages = new Set<string>();
  private listeners: (() => void)[] = [];

  constructor(root: HTMLElement) {
    this.root = root;
    this.state = loadFrom(storage()) ?? createState();
    this.overlay = h('div', { class: 'overlay' });
    this.toasts = h('div', { class: 'toasts', 'aria-live': 'polite' });
    root.append(this.overlay, this.toasts);
    this.audio = new AudioEngine(() => this.state.settings);
    this.rememberPages();
    window.addEventListener('pagehide', () => this.saveNow());
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') this.saveNow();
    });
    const unlock = () => this.audio.unlock();
    window.addEventListener('pointerdown', unlock, { once: false });
    window.addEventListener('keydown', unlock, { once: false });
  }

  hasSave(): boolean {
    return !!loadFrom(storage());
  }

  newGame(): void {
    const settings = this.state.settings;
    this.state = createState();
    this.state.settings = settings;
    clearSave(storage());
    this.knownOpenPages.clear();
    this.saveNow();
  }

  onChange(fn: () => void): () => void {
    this.listeners.push(fn);
    return () => (this.listeners = this.listeners.filter((f) => f !== fn));
  }

  /** Something in the journal changed: redraw glyphs, save. */
  changed(): void {
    refreshAllGlyphs(this);
    for (const fn of this.listeners) fn();
    this.save();
  }

  save(): void {
    if (this.saveTimer !== null) clearTimeout(this.saveTimer);
    this.saveTimer = window.setTimeout(() => this.saveNow(), 300);
  }

  saveNow(): void {
    if (this.saveTimer !== null) clearTimeout(this.saveTimer);
    this.saveTimer = null;
    const now = performance.now();
    this.state.playMs += Math.min(now - this.lastTick, 60_000);
    this.lastTick = now;
    saveTo(storage(), this.state);
  }

  tickPlaytime(): void {
    const now = performance.now();
    this.state.playMs += Math.min(now - this.lastTick, 60_000);
    this.lastTick = now;
  }

  /* ---------------- notifications ---------------- */

  toast(content: string | Node, kind = ''): void {
    const el = h('div', { class: `toast ${kind}` }, content);
    this.toasts.append(el);
    requestAnimationFrame(() => el.classList.add('show'));
    setTimeout(() => {
      el.classList.remove('show');
      setTimeout(() => el.remove(), 400);
    }, 3200);
  }

  private rememberPages(): void {
    for (const p of openPages(this.state)) this.knownOpenPages.add(p.id);
  }

  /** Called after glyphs were seen: announce new glyphs and newly opened pages. */
  announce(fresh: Glyph[]): void {
    if (fresh.length) {
      this.audio.sfx('glyph');
      document.body.classList.add('journal-new');
    }
    for (const p of PAGES) {
      if (pageStatus(this.state, p) === 'open' && !this.knownOpenPages.has(p.id)) {
        this.knownOpenPages.add(p.id);
        this.audio.sfx('page');
        this.toast(h('span', {}, 'Открыта страница дневника: ', h('b', {}, `«${p.title}»`)), 'page');
        document.body.classList.add('journal-page');
      }
    }
  }

  /* ---------------- panels ---------------- */

  openGlyph(g: Glyph, anchor?: HTMLElement): void {
    openGlyphCard(this, g, anchor);
  }

  openJournal(tab?: JournalTab, pageId?: string): void {
    document.body.classList.remove('journal-new', 'journal-page');
    openJournal(this, tab, pageId);
  }

  showHint(): void {
    const text = currentHint(this.state);
    openModal(this.overlay, h('p', { class: 'hint-text' }, text), { title: 'Подсказка', className: 'small' });
  }
}
