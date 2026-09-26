#!/usr/bin/env node
/**
 * Turns the Vite build (dist/) into one self-contained HTML file:
 * CSS, JavaScript and fonts are inlined. The result opens straight from
 * disk (file://) and can be hosted anywhere as a single page.
 *
 *   npm run build && npm run build:single   →   dist-single/richu.html
 */
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const dist = join(root, 'dist');
const out = join(root, 'dist-single');

let html = readFileSync(join(dist, 'index.html'), 'utf8');

const inlineCss = (href) => {
  const file = join(dist, href);
  let css = readFileSync(file, 'utf8');
  css = css.replace(/url\((['"]?)([^'")]+\.woff2)\1\)/g, (_m, _q, url) => {
    const font = readFileSync(join(dirname(file), url));
    return `url(data:font/woff2;base64,${font.toString('base64')})`;
  });
  return css;
};

html = html.replace(/<link rel="stylesheet"[^>]*href="([^"]+)"[^>]*>/g, (_m, href) => `<style>\n${inlineCss(href)}\n</style>`);
html = html.replace(/<script type="module"[^>]*src="([^"]+)"[^>]*><\/script>/g, (_m, src) => {
  const js = readFileSync(join(dist, src), 'utf8').replace(/<\/script/gi, '<\\/script');
  return `<script type="module">\n${js}\n</script>`;
});
html = html.replace(/<link rel="modulepreload"[^>]*>/g, '');

if (/(src|href)="\.\/assets\//.test(html)) throw new Error('some assets were not inlined');
mkdirSync(out, { recursive: true });
writeFileSync(join(out, 'richu.html'), html);
console.log(`dist-single/richu.html: ${Math.round(html.length / 1024)} KB`);
