type Child = Node | string | null | undefined | false;
type Props = Record<string, unknown> & {
  class?: string;
  style?: string;
  html?: string;
};

/** Tiny hyperscript: h('div', { class: 'x', onclick }, 'text', child). */
export function h<K extends keyof HTMLElementTagNameMap>(tag: K, props: Props = {}, ...children: Child[]): HTMLElementTagNameMap[K] {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (v === undefined || v === null || v === false) continue;
    if (k === 'class') el.className = String(v);
    else if (k === 'style') el.setAttribute('style', String(v));
    else if (k === 'html') el.innerHTML = String(v);
    else if (k.startsWith('on') && typeof v === 'function') el.addEventListener(k.slice(2), v as EventListener);
    else if (k in el && typeof v !== 'string') (el as unknown as Record<string, unknown>)[k] = v;
    else el.setAttribute(k, v === true ? '' : String(v));
  }
  append(el, ...children);
  return el;
}

export function append(el: Element, ...children: Child[]): void {
  for (const c of children) {
    if (c === null || c === undefined || c === false) continue;
    el.append(typeof c === 'string' ? document.createTextNode(c) : c);
  }
}

export function clear(el: Element): void {
  while (el.firstChild) el.firstChild.remove();
}

export function svgEl(markup: string): SVGSVGElement {
  const t = document.createElement('template');
  t.innerHTML = markup.trim();
  return t.content.firstElementChild as SVGSVGElement;
}

export function icon(inner: string, viewBox = '0 0 100 100', cls = 'icon'): SVGSVGElement {
  return svgEl(`<svg class="${cls}" viewBox="${viewBox}" aria-hidden="true">${inner}</svg>`);
}

export const sleep = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

export function nextFrame(): Promise<void> {
  return new Promise((r) => requestAnimationFrame(() => r()));
}

/** Resolve on the next click/tap/key on `target` (or document). */
export function waitClick(target: EventTarget = document, keys = [' ', 'Enter']): Promise<void> {
  return new Promise((resolve) => {
    const done = () => {
      target.removeEventListener('click', onClick);
      document.removeEventListener('keydown', onKey);
      resolve();
    };
    const onClick = () => done();
    const onKey = (e: Event) => {
      const k = (e as KeyboardEvent).key;
      if (keys.includes(k) && !(e.target instanceof HTMLInputElement)) {
        e.preventDefault();
        done();
      }
    };
    target.addEventListener('click', onClick);
    document.addEventListener('keydown', onKey);
  });
}
