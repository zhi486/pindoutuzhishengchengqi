/** CIE L*a*b* 色彩空间转换与最近邻颜色匹配。
 *
 * 将 sRGB 像素转换为感知均匀的 LAB 空间，
 * 然后通过 Delta-E CIE76 距离匹配到最接近的色卡颜色。
 */

export type RGB = [number, number, number];
export type LAB = [number, number, number];

// D65 参考白点
const REF_X = 0.95047;
const REF_Y = 1.0;
const REF_Z = 1.08883;

/** sRGB → 线性 RGB */
function srgbToLinear(c: number): number {
  c /= 255;
  return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

/** 线性 RGB → CIE XYZ (D65) */
function linearRgbToXyz(r: number, g: number, b: number): [number, number, number] {
  return [
    r * 0.4124564 + g * 0.3575761 + b * 0.1804375,
    r * 0.2126729 + g * 0.7151522 + b * 0.072175,
    r * 0.0193339 + g * 0.119192 + b * 0.9503041,
  ];
}

const f = (t: number): number =>
  t > 0.008856 ? Math.cbrt(t) : 7.787 * t + 16 / 116;

/** XYZ → CIE L*a*b* */
function xyzToLab(x: number, y: number, z: number): LAB {
  const fy = f(y / REF_Y);
  return [
    116 * fy - 16,
    500 * (f(x / REF_X) - fy),
    200 * (fy - f(z / REF_Z)),
  ];
}

/** sRGB → CIE L*a*b* */
export function rgbToLab(rgb: RGB): LAB {
  const r = srgbToLinear(rgb[0]);
  const g = srgbToLinear(rgb[1]);
  const b = srgbToLinear(rgb[2]);
  const [x, y, z] = linearRgbToXyz(r, g, b);
  return xyzToLab(x, y, z);
}

/** CIE76 Delta-E 色差 */
export function deltaE(lab1: LAB, lab2: LAB): number {
  const dL = lab1[0] - lab2[0];
  const da = lab1[1] - lab2[1];
  const db = lab1[2] - lab2[2];
  return Math.sqrt(dL * dL + da * da + db * db);
}

/** 预计算色卡 LAB 缓存 */
export function precomputeLabCache(palette: { rgb: RGB }[]): LAB[] {
  return palette.map((c) => rgbToLab(c.rgb));
}

/** 在色卡中查找最接近的颜色索引 */
export function findNearest(
  pixelLab: LAB,
  paletteLab: LAB[],
): number {
  let bestIdx = 0;
  let bestDist = Infinity;
  for (let i = 0; i < paletteLab.length; i++) {
    const d = deltaE(pixelLab, paletteLab[i]);
    if (d < bestDist) {
      bestDist = d;
      bestIdx = i;
    }
  }
  return bestIdx;
}
