import type { Settings } from '../core/types';

/**
 * Sound for the game, all synthesized:
 *  - speech: Web Speech API (zh-CN) for characters and phrases;
 *  - music: slow pentatonic plucks over a drone;
 *  - effects: small noise/tone recipes.
 */
export class AudioEngine {
  private ctx: AudioContext | null = null;
  private master: GainNode | null = null;
  private musicBus: GainNode | null = null;
  private sfxBus: GainNode | null = null;
  private reverb: ConvolverNode | null = null;
  private musicTimer: number | null = null;
  private drone: OscillatorNode[] = [];
  private mood = 1;
  private voice: SpeechSynthesisVoice | null = null;
  private voicesLoaded = false;

  constructor(private settings: () => Settings) {
    if (typeof speechSynthesis !== 'undefined') {
      this.pickVoice();
      speechSynthesis.addEventListener?.('voiceschanged', () => this.pickVoice());
    }
  }

  /* ---------------- speech ---------------- */

  private pickVoice() {
    try {
      const voices = speechSynthesis.getVoices();
      this.voicesLoaded = voices.length > 0;
      const zh = voices.filter((v) => /^zh[-_](CN|Hans)/i.test(v.lang) || v.lang === 'zh');
      this.voice = zh.find((v) => /google|xiaoxiao|tingting|yaoyao|huihui/i.test(v.name)) ?? zh[0] ?? null;
    } catch {
      this.voice = null;
    }
  }

  canSpeak(): boolean {
    return typeof speechSynthesis !== 'undefined' && (!!this.voice || !this.voicesLoaded);
  }

  speak(text: string, rate = 0.8): void {
    if (!this.settings().voice || typeof speechSynthesis === 'undefined') return;
    try {
      speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      u.lang = 'zh-CN';
      if (this.voice) u.voice = this.voice;
      u.rate = rate;
      speechSynthesis.speak(u);
    } catch {
      /* speech unavailable */
    }
  }

  /* ---------------- engine ---------------- */

  /** Must be called from a user gesture. */
  unlock(): void {
    if (this.ctx) {
      if (this.ctx.state === 'suspended') void this.ctx.resume();
      return;
    }
    const Ctor = window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (!Ctor) return;
    const ctx = new Ctor();
    this.ctx = ctx;
    this.master = ctx.createGain();
    this.master.gain.value = 0.8;
    this.master.connect(ctx.destination);
    this.reverb = ctx.createConvolver();
    this.reverb.buffer = this.impulse(2.8);
    const wet = ctx.createGain();
    wet.gain.value = 0.35;
    this.reverb.connect(wet).connect(this.master);
    this.musicBus = ctx.createGain();
    this.musicBus.gain.value = 0;
    this.musicBus.connect(this.master);
    this.musicBus.connect(this.reverb);
    this.sfxBus = ctx.createGain();
    this.sfxBus.gain.value = 0.7;
    this.sfxBus.connect(this.master);
    this.sfxBus.connect(this.reverb);
    this.applySettings();
  }

  private impulse(seconds: number): AudioBuffer {
    const ctx = this.ctx!;
    const len = Math.floor(ctx.sampleRate * seconds);
    const buf = ctx.createBuffer(2, len, ctx.sampleRate);
    for (let c = 0; c < 2; c++) {
      const d = buf.getChannelData(c);
      for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 2.6);
    }
    return buf;
  }

  applySettings(): void {
    if (!this.ctx) return;
    const s = this.settings();
    const t = this.ctx.currentTime;
    this.sfxBus!.gain.setTargetAtTime(s.sfx ? 0.7 : 0, t, 0.05);
    if (s.music) this.startMusic();
    else this.stopMusic();
  }

  /* ---------------- music ---------------- */

  setMood(chapter: number): void {
    this.mood = chapter;
    if (this.drone.length) {
      this.stopDrone();
      this.startDrone();
    }
  }

  private scale(): number[] {
    const roots = [0, 220, 196, 174.61, 146.83];
    const root = roots[this.mood] ?? 220;
    const steps = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21];
    return steps.map((st) => root * Math.pow(2, st / 12));
  }

  private startDrone() {
    const ctx = this.ctx!;
    const root = this.scale()[0] / 2;
    for (const [f, g] of [
      [root, 0.05],
      [root * 1.5, 0.025],
    ] as const) {
      const o = ctx.createOscillator();
      o.type = 'sine';
      o.frequency.value = f;
      const gain = ctx.createGain();
      gain.gain.value = 0;
      gain.gain.setTargetAtTime(g, ctx.currentTime, 2);
      const lfo = ctx.createOscillator();
      lfo.frequency.value = 0.07;
      const lfoGain = ctx.createGain();
      lfoGain.gain.value = g * 0.4;
      lfo.connect(lfoGain).connect(gain.gain);
      o.connect(gain).connect(this.musicBus!);
      o.start();
      lfo.start();
      this.drone.push(o, lfo);
    }
  }

  private stopDrone() {
    for (const o of this.drone) {
      try {
        o.stop();
      } catch {
        /* already stopped */
      }
    }
    this.drone = [];
  }

  private startMusic() {
    if (!this.ctx || this.musicTimer !== null) return;
    this.musicBus!.gain.setTargetAtTime(0.5, this.ctx.currentTime, 1.5);
    this.startDrone();
    const tick = () => {
      if (!this.ctx) return;
      const notes = this.scale();
      const n = Math.random() < 0.3 ? 2 : 1;
      for (let i = 0; i < n; i++) {
        const f = notes[Math.floor(Math.random() * notes.length)];
        this.pluck(f, this.ctx.currentTime + i * 0.18, 0.09, this.musicBus!);
      }
      this.musicTimer = window.setTimeout(tick, 900 + Math.random() * 2200);
    };
    this.musicTimer = window.setTimeout(tick, 800);
  }

  private stopMusic() {
    if (this.musicTimer !== null) clearTimeout(this.musicTimer);
    this.musicTimer = null;
    if (this.ctx) this.musicBus!.gain.setTargetAtTime(0, this.ctx.currentTime, 0.4);
    this.stopDrone();
  }

  /** A plucked-string tone (guzheng-ish). */
  private pluck(freq: number, at: number, vol: number, bus: AudioNode, decay = 2.2) {
    const ctx = this.ctx!;
    const o = ctx.createOscillator();
    const o2 = ctx.createOscillator();
    o.type = 'triangle';
    o2.type = 'sine';
    o.frequency.value = freq;
    o2.frequency.value = freq * 2.005;
    const filter = ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(freq * 8, at);
    filter.frequency.exponentialRampToValueAtTime(freq * 1.5, at + decay * 0.6);
    const g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, at);
    g.gain.exponentialRampToValueAtTime(vol, at + 0.01);
    g.gain.exponentialRampToValueAtTime(0.0001, at + decay);
    const g2 = ctx.createGain();
    g2.gain.value = 0.3;
    o.connect(filter);
    o2.connect(g2).connect(filter);
    filter.connect(g).connect(bus);
    o.start(at);
    o2.start(at);
    o.stop(at + decay + 0.1);
    o2.stop(at + decay + 0.1);
  }

  private noise(at: number, dur: number, vol: number, type: BiquadFilterType, freq: number, q = 1, sweepTo?: number) {
    const ctx = this.ctx!;
    const len = Math.floor(ctx.sampleRate * dur);
    const buf = ctx.createBuffer(1, len, ctx.sampleRate);
    const d = buf.getChannelData(0);
    for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
    const src = ctx.createBufferSource();
    src.buffer = buf;
    const f = ctx.createBiquadFilter();
    f.type = type;
    f.frequency.setValueAtTime(freq, at);
    if (sweepTo) f.frequency.exponentialRampToValueAtTime(sweepTo, at + dur);
    f.Q.value = q;
    const g = ctx.createGain();
    g.gain.setValueAtTime(vol, at);
    g.gain.exponentialRampToValueAtTime(0.0001, at + dur);
    src.connect(f).connect(g).connect(this.sfxBus!);
    src.start(at);
  }

  private bellTone(freq: number, at: number, vol = 0.18) {
    const ctx = this.ctx!;
    for (const [ratio, amp, dec] of [
      [1, 1, 3.2],
      [2.76, 0.45, 1.6],
      [5.4, 0.25, 0.8],
      [0.5, 0.3, 3.8],
    ] as const) {
      const o = ctx.createOscillator();
      o.type = 'sine';
      o.frequency.value = freq * ratio;
      const g = ctx.createGain();
      g.gain.setValueAtTime(0.0001, at);
      g.gain.exponentialRampToValueAtTime(vol * amp, at + 0.005);
      g.gain.exponentialRampToValueAtTime(0.0001, at + dec);
      o.connect(g).connect(this.sfxBus!);
      o.start(at);
      o.stop(at + dec + 0.1);
    }
  }

  /** Bells on the temple rack: index 0..5. */
  bell(index: number) {
    if (!this.ctx) return;
    const freqs = [261.6, 293.7, 329.6, 392, 440, 523.3];
    this.bellTone(freqs[index] ?? 330, this.ctx.currentTime);
  }

  sfx(name: string): void {
    if (!this.ctx || !this.settings().sfx) return;
    const t = this.ctx.currentTime;
    switch (name) {
      case 'click':
        this.pluck(880, t, 0.03, this.sfxBus!, 0.25);
        break;
      case 'splash':
        this.noise(t, 0.6, 0.4, 'bandpass', 1400, 0.8, 400);
        break;
      case 'pour':
        this.noise(t, 0.9, 0.2, 'bandpass', 900, 2, 2400);
        break;
      case 'fire':
        for (let i = 0; i < 8; i++) this.noise(t + Math.random() * 0.6, 0.05, 0.25, 'highpass', 2000);
        this.noise(t, 1, 0.12, 'lowpass', 500);
        break;
      case 'coins':
        for (let i = 0; i < 4; i++) this.bellTone(1800 + Math.random() * 600, t + i * 0.08, 0.05);
        break;
      case 'hop':
        this.noise(t, 0.08, 0.2, 'lowpass', 300);
        break;
      case 'gate':
        this.noise(t, 2.2, 0.35, 'lowpass', 160, 1, 60);
        this.bellTone(98, t + 0.3, 0.12);
        break;
      case 'bell':
        this.bellTone(330, t);
        break;
      case 'confirm':
        [523.3, 659.3, 784, 1046.5].forEach((f, i) => this.pluck(f, t + i * 0.09, 0.08, this.sfxBus!, 1.4));
        break;
      case 'wrong':
        this.pluck(146.8, t, 0.1, this.sfxBus!, 0.6);
        this.pluck(155.6, t + 0.02, 0.08, this.sfxBus!, 0.6);
        break;
      case 'page':
        this.noise(t, 0.25, 0.15, 'highpass', 3000);
        break;
      case 'item':
        this.pluck(659.3, t, 0.07, this.sfxBus!, 0.8);
        this.pluck(987.8, t + 0.08, 0.06, this.sfxBus!, 0.8);
        break;
      case 'glyph':
        this.pluck(1318.5, t, 0.035, this.sfxBus!, 0.9);
        break;
      case 'sunrise':
        [196, 293.7, 392, 493.9, 587.3, 784].forEach((f, i) => this.pluck(f, t + i * 0.35, 0.09, this.sfxBus!, 4));
        break;
      default:
        break;
    }
  }
}
