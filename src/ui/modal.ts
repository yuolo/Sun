import { h } from './dom';

export interface ModalHandle {
  el: HTMLElement;
  body: HTMLElement;
  close(): void;
  closed: Promise<void>;
}

export interface ModalOpts {
  title?: string;
  className?: string;
  closable?: boolean;
  onClose?: () => void;
}

const stack: ModalHandle[] = [];

export function topModal(): ModalHandle | undefined {
  return stack[stack.length - 1];
}

export function modalOpen(): boolean {
  return stack.length > 0;
}

export function openModal(host: HTMLElement, content: Node, opts: ModalOpts = {}): ModalHandle {
  let resolveClosed!: () => void;
  const closed = new Promise<void>((r) => (resolveClosed = r));
  const body = h('div', { class: 'modal-body' }, content);
  const closeBtn = opts.closable === false ? null : h('button', { class: 'modal-close', 'aria-label': 'Закрыть', onclick: () => handle.close() }, '×');
  const panel = h('div', { class: `modal ${opts.className ?? ''}`, role: 'dialog', 'aria-modal': 'true' }, opts.title ? h('h2', { class: 'modal-title' }, opts.title) : null, closeBtn, body);
  const backdrop = h('div', { class: 'backdrop' }, panel);
  backdrop.addEventListener('click', (e) => {
    if (e.target === backdrop && opts.closable !== false) handle.close();
  });
  let isClosed = false;
  const handle: ModalHandle = {
    el: panel,
    body,
    closed,
    close() {
      if (isClosed) return;
      isClosed = true;
      const i = stack.indexOf(handle);
      if (i !== -1) stack.splice(i, 1);
      backdrop.classList.add('closing');
      setTimeout(() => backdrop.remove(), 160);
      opts.onClose?.();
      resolveClosed();
    },
  };
  stack.push(handle);
  host.append(backdrop);
  requestAnimationFrame(() => backdrop.classList.add('open'));
  return handle;
}

/** Esc closes the top modal if it can be closed. */
export function installModalKeys(): void {
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    const top = topModal();
    if (top && top.el.querySelector('.modal-close')) {
      e.preventDefault();
      top.close();
    }
  });
}
