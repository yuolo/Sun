import type { SceneLook } from '../core/types';

/** Rain drawn on a canvas covering the stage. */
export class Rain {
  private ctx: CanvasRenderingContext2D | null;
  private drops: { x: number; y: number; v: number; l: number }[] = [];
  private raf = 0;
  private running = false;
  private intensity = 0;

  constructor(canvas: HTMLCanvasElement) {
    canvas.width = 1600;
    canvas.height = 900;
    this.ctx = canvas.getContext('2d');
    for (let i = 0; i < 260; i++) this.drops.push(this.drop(Math.random() * 900));
  }

  private drop(y = -20) {
    return { x: Math.random() * 1700 - 50, y, v: 16 + Math.random() * 12, l: 14 + Math.random() * 18 };
  }

  start(): void {
    if (this.running) return;
    this.running = true;
    this.intensity = 0;
    const loop = () => {
      if (!this.ctx) return;
      const c = this.ctx;
      c.clearRect(0, 0, 1600, 900);
      c.strokeStyle = 'rgba(200,215,235,0.55)';
      c.lineWidth = 1.6;
      c.beginPath();
      const n = Math.floor(this.drops.length * this.intensity);
      for (let i = 0; i < n; i++) {
        const d = this.drops[i];
        c.moveTo(d.x, d.y);
        c.lineTo(d.x - d.l * 0.25, d.y + d.l);
        d.y += d.v;
        d.x -= d.v * 0.25;
        if (d.y > 900) Object.assign(d, this.drop());
      }
      c.stroke();
      this.intensity = this.running ? Math.min(1, this.intensity + 0.01) : Math.max(0, this.intensity - 0.02);
      if (this.running || this.intensity > 0) this.raf = requestAnimationFrame(loop);
      else c.clearRect(0, 0, 1600, 900);
    };
    cancelAnimationFrame(this.raf);
    this.raf = requestAnimationFrame(loop);
  }

  stop(): void {
    this.running = false;
  }

  kill(): void {
    this.running = false;
    this.intensity = 0;
    cancelAnimationFrame(this.raf);
    this.ctx?.clearRect(0, 0, 1600, 900);
  }
}

const DARKNESS: Record<string, number> = {
  day: 0,
  golden: 0,
  sunset: 0.08,
  dusk: 0.32,
  night: 0.5,
  predawn: 0.42,
  dawn: 0,
};

/** Night overlay with a warm pool of light around the player's lantern. */
export function applyLight(el: HTMLElement, look: SceneLook, hasLantern: boolean): void {
  const dark = DARKNESS[look.time] ?? 0;
  el.style.setProperty('--dark', String(dark));
  el.classList.toggle('on', dark > 0);
  el.classList.toggle('lantern', !!look.lantern && hasLantern && dark > 0.2);
}

export function moveLight(el: HTMLElement, x: number, y: number): void {
  el.style.setProperty('--lx', `${x}px`);
  el.style.setProperty('--ly', `${y - 80}px`);
}
