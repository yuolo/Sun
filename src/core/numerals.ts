const DIGITS = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九'];

/** 0–99 in Chinese numerals: 7 → 七, 10 → 十, 13 → 十三, 20 → 二十. */
export function toHanzi(n: number): string {
  if (!Number.isInteger(n) || n < 0 || n > 99) throw new RangeError(`unsupported number ${n}`);
  if (n < 10) return DIGITS[n];
  const tens = Math.floor(n / 10);
  const ones = n % 10;
  return (tens === 1 ? '' : DIGITS[tens]) + '十' + (ones ? DIGITS[ones] : '');
}

/** Parse 1–99 written in Chinese numerals. Returns null if not a number. */
export function fromHanzi(text: string): number | null {
  if (!text) return null;
  const i = text.indexOf('十');
  const digit = (c: string) => {
    const d = DIGITS.indexOf(c);
    return d > 0 ? d : null;
  };
  if (i === -1) return text.length === 1 ? digit(text) : null;
  const before = text.slice(0, i);
  const after = text.slice(i + 1);
  if (before.length > 1 || after.length > 1) return null;
  const tens = before ? digit(before) : 1;
  const ones = after ? digit(after) : 0;
  if (tens === null || ones === null) return null;
  return tens * 10 + ones;
}
