import './styles/main.css';
import { App } from './ui/app';
import { h } from './ui/dom';
import { pauseMenu, prologue, titleScreen } from './ui/menu';
import { installModalKeys } from './ui/modal';
import { Runtime } from './ui/runtime';

const root = document.getElementById('app')!;
const app = new App(root);
installModalKeys();
root.append(h('div', { class: 'rotate-hint' }, 'Поверните телефон горизонтально'));

let runtime: Runtime | null = null;
let title: HTMLElement | null = null;

function showTitle(): void {
  runtime?.destroy();
  runtime = null;
  title?.remove();
  title = titleScreen(app, { onContinue: () => void play(false), onNew: () => void play(true) });
  root.prepend(title);
}

async function play(fresh: boolean): Promise<void> {
  app.audio.unlock();
  if (fresh) app.newGame();
  title?.remove();
  title = null;
  if (fresh) await prologue(root);
  runtime = new Runtime(app, root);
  runtime.onMainMenu = showTitle;
  runtime.onPause = () => pauseMenu(app, showTitle);
  await runtime.start();
}

showTitle();

if (import.meta.env.DEV || new URLSearchParams(location.search).has('debug')) {
  Object.assign(window, { __richu: { app, play, showTitle, get runtime() { return runtime; } } });
}
