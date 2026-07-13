/** 中值切割颜色量化算法。
 *
 * 将色块网格中的颜色数量减少到指定上限，
 * 通过反复在颜色范围最宽的通道上二分来实现。
 */

type RGB = [number, number, number];

interface Box {
  data: RGB[];
  rMin: number; rMax: number;
  gMin: number; gMax: number;
  bMin: number; bMax: number;
}

/** 中值切割 */
export function medianCut(pixels: RGB[], k: number): RGB[] {
  if (pixels.length <= k) return pixels;

  const boxes: Box[] = [
    {
      data: [...pixels],
      rMin: 0, rMax: 255, gMin: 0, gMax: 255, bMin: 0, bMax: 255,
    },
  ];

  while (boxes.length < k) {
    // 找体积最大的盒子
    let bestIdx = 0, bestVol = -1;
    for (let i = 0; i < boxes.length; i++) {
      const b = boxes[i];
      const vol = (b.rMax - b.rMin + 1) * (b.gMax - b.gMin + 1) * (b.bMax - b.bMin + 1);
      if (vol > bestVol) { bestVol = vol; bestIdx = i; }
    }

    const box = boxes[bestIdx];
    const rngR = box.rMax - box.rMin;
    const rngG = box.gMax - box.gMin;
    const rngB = box.bMax - box.bMin;

    // 选择范围最大的通道
    const ch = rngR >= rngG && rngR >= rngB ? 0 : rngG >= rngB ? 1 : 2;
    box.data.sort((a, b) => a[ch] - b[ch]);

    const mid = box.data.length >> 1;
    if (mid === 0) break;

    const left = box.data.slice(0, mid);
    const right = box.data.slice(mid);

    boxes[bestIdx] = makeBox(left);
    boxes.push(makeBox(right));
  }

  // 每个盒子的均值作为调色板
  return boxes.map((b) => {
    const sum: number[] = [0, 0, 0];
    for (const p of b.data) {
      sum[0] += p[0]; sum[1] += p[1]; sum[2] += p[2];
    }
    const n = b.data.length;
    return [Math.round(sum[0] / n), Math.round(sum[1] / n), Math.round(sum[2] / n)] as RGB;
  });
}

function makeBox(data: RGB[]): Box {
  const r = data.map((p) => p[0]);
  const g = data.map((p) => p[1]);
  const b = data.map((p) => p[2]);
  return {
    data,
    rMin: Math.min(...r), rMax: Math.max(...r),
    gMin: Math.min(...g), gMax: Math.max(...g),
    bMin: Math.min(...b), bMax: Math.max(...b),
  };
}

/** 量化颜色网格 */
export function quantizeGrid(
  grid: RGB[][],
  maxColors: number,
): RGB[][] {
  const pixels: RGB[] = grid.flat();
  const uniq = new Set(pixels.map((p) => p.join(',')));
  if (uniq.size <= maxColors) return grid;

  const palette = medianCut(pixels, maxColors);

  const h = grid.length;
  const w = grid[0].length;
  const out: RGB[][] = [];

  for (let r = 0; r < h; r++) {
    out[r] = [];
    for (let c = 0; c < w; c++) {
      let bestI = 0, bestD = Infinity;
      for (let i = 0; i < palette.length; i++) {
        const dr = grid[r][c][0] - palette[i][0];
        const dg = grid[r][c][1] - palette[i][1];
        const db = grid[r][c][2] - palette[i][2];
        const d = dr * dr + dg * dg + db * db;
        if (d < bestD) { bestD = d; bestI = i; }
      }
      out[r][c] = palette[bestI];
    }
  }
  return out;
}
