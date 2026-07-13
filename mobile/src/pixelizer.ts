/** 图片处理管道。
 *
 * 将 React Native 图片资源转换为像素化的拼豆颜色网格。
 * 流程：加载 → 缩放到目标尺寸 → 提取像素 → 颜色量化 → 色卡匹配
 */

import type { RGB } from './colorSpace';
import { rgbToLab, findNearest, precomputeLabCache } from './colorSpace';
import { quantizeGrid } from './quantizer';
import { PALETTE, type BeadColor } from './palette';

const PALETTE_LAB = precomputeLabCache(PALETTE);

export interface ProcessResult {
  /** (H, W, 3) 匹配后的 RGB 网格 */
  matchedGrid: RGB[][];
  /** (H, W) 色卡索引网格 */
  indexGrid: number[][];
  /** { 色号: 数量 } */
  colorCounts: Map<string, number>;
  /** 按数量降序排列的汇总 */
  colorSummary: Array<{ code: string; hex: string; rgb: RGB; count: number }>;
  /** 豆子尺寸 */
  beadW: number;
  beadH: number;
}

/**
 * 从 ImageData（如 Canvas 或 Skia Image 提取）生成拼豆颜色网格。
 *
 * @param pixels - 扁平化的 RGBA/UInt8 像素数组（已缩放到目标尺寸）
 * @param w - 宽度（豆子列数）
 * @param h - 高度（豆子行数）
 * @param maxColors - 最大颜色数量
 */
export function processPixels(
  pixels: Uint8ClampedArray,
  w: number,
  h: number,
  maxColors: number,
): ProcessResult {
  // 构建 RGB 网格
  const grid: RGB[][] = [];
  for (let r = 0; r < h; r++) {
    grid[r] = [];
    for (let c = 0; c < w; c++) {
      const i = (r * w + c) * 4;
      grid[r][c] = [pixels[i], pixels[i + 1], pixels[i + 2]];
    }
  }

  // 颜色量化
  const quantized = quantizeGrid(grid, maxColors);

  // 匹配到色卡
  const matchedGrid: RGB[][] = [];
  const indexGrid: number[][] = [];
  const counts = new Map<string, number>();

  for (let r = 0; r < h; r++) {
    matchedGrid[r] = [];
    indexGrid[r] = [];
    for (let c = 0; c < w; c++) {
      const lab = rgbToLab(quantized[r][c]);
      const idx = findNearest(lab, PALETTE_LAB);
      matchedGrid[r][c] = PALETTE[idx].rgb;
      indexGrid[r][c] = idx;
      const code = PALETTE[idx].code;
      counts.set(code, (counts.get(code) || 0) + 1);
    }
  }

  // 汇总
  const sorted = Array.from(counts.entries()).sort((a, b) => b[1] - a[1]);
  const colorSummary = sorted.map(([code, count]) => {
    const c = PALETTE.find((p) => p.code === code)!;
    return { code, hex: c.hex, rgb: c.rgb, count };
  });

  return {
    matchedGrid,
    indexGrid,
    colorCounts: counts,
    colorSummary,
    beadW: w,
    beadH: h,
  };
}

/** 根据高度和原图长宽比自动计算宽度 */
export function computeBeadW(
  imgWidth: number,
  imgHeight: number,
  beadH: number,
): number {
  return Math.max(1, Math.round((imgWidth / imgHeight) * beadH));
}
