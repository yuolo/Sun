/** A walkable polyline, parameterised by distance along it. */
export class WalkPath {
  readonly pts: [number, number][];
  private readonly acc: number[];
  readonly total: number;

  constructor(pts: [number, number][]) {
    if (pts.length < 2) throw new Error('a path needs two points');
    this.pts = pts;
    this.acc = [0];
    for (let i = 1; i < pts.length; i++) {
      this.acc.push(this.acc[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
    }
    this.total = this.acc[this.acc.length - 1];
  }

  clamp(t: number): number {
    return Math.max(0, Math.min(this.total, t));
  }

  pointAt(t: number): [number, number] {
    const d = this.clamp(t);
    for (let i = 1; i < this.pts.length; i++) {
      if (d <= this.acc[i] || i === this.pts.length - 1) {
        const len = this.acc[i] - this.acc[i - 1] || 1;
        const k = (d - this.acc[i - 1]) / len;
        const [ax, ay] = this.pts[i - 1];
        const [bx, by] = this.pts[i];
        return [ax + (bx - ax) * k, ay + (by - ay) * k];
      }
    }
    return this.pts[this.pts.length - 1];
  }

  /** Parameter of the point on the path closest to (x, y). */
  nearest(x: number, y: number): number {
    let best = 0;
    let bestD = Infinity;
    for (let i = 1; i < this.pts.length; i++) {
      const [ax, ay] = this.pts[i - 1];
      const [bx, by] = this.pts[i];
      const dx = bx - ax;
      const dy = by - ay;
      const len2 = dx * dx + dy * dy || 1;
      const k = Math.max(0, Math.min(1, ((x - ax) * dx + (y - ay) * dy) / len2));
      const px = ax + dx * k;
      const py = ay + dy * k;
      const d = (px - x) ** 2 + (py - y) ** 2;
      if (d < bestD) {
        bestD = d;
        best = this.acc[i - 1] + Math.sqrt(len2) * k;
      }
    }
    return best;
  }

  /** Parameter for an x coordinate: the first segment spanning x. */
  atX(x: number): number {
    for (let i = 1; i < this.pts.length; i++) {
      const [ax, ay] = this.pts[i - 1];
      const [bx] = this.pts[i];
      if ((x - ax) * (x - bx) <= 0) return this.nearest(x, ay + (this.pts[i][1] - ay) * ((x - ax) / (bx - ax || 1)));
    }
    const first = this.pts[0];
    const last = this.pts[this.pts.length - 1];
    return Math.abs(x - first[0]) < Math.abs(x - last[0]) ? 0 : this.total;
  }
}
