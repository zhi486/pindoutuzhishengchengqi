"""颜色量化器 —— 减少图像中的颜色数量。

在使用拼豆色卡匹配之前，可选择性地将颜色数减至指定数量，
使最终图纸更简洁。采用中值切割算法（纯 numpy 实现，无需额外依赖）。
"""

import numpy as np


def median_cut(pixels: np.ndarray, k: int) -> np.ndarray:
    """中值切割颜色量化算法。

    算法思路：
    1. 将所有像素放入一个"盒子"
    2. 找到颜色范围最大的通道（R、G 或 B）
    3. 按该通道的中值将盒子一分为二
    4. 递归直到盒子数量达到 K
    5. 每个盒子的颜色均值即为调色板的一项

    这个方法天然倾向于保留人眼容易察觉差异的颜色区分，
    比简单的线性等分效果好得多。

    Args:
        pixels: (N, 3) numpy float64 数组，每个像素的 RGB 值（0-255）
        k: 目标颜色数量

    Returns:
        (k, 3) numpy float64 数组，K 个调色板颜色
    """
    k = min(k, len(pixels))
    if k <= 1:
        return np.mean(pixels, axis=0, keepdims=True)

    def _cut(box):
        # box 是一个 (M, 3) 的像素子集
        if len(box) == 0:
            return np.zeros((1, 3))
        # 计算每个通道的范围
        ranges = np.max(box, axis=0) - np.min(box, axis=0)
        # 选择范围最大的通道
        channel = int(np.argmax(ranges))
        # 按该通道排序
        sorted_idx = np.argsort(box[:, channel])
        box = box[sorted_idx]
        # 在中位数处切割
        median = len(box) // 2
        return np.mean(box, axis=0, keepdims=True)

    # 初始化: 所有像素在一个盒子里
    boxes = [pixels]

    # 迭代：每次切割体积最大的盒子
    while len(boxes) < k:
        # 找到体积最大的盒子 (range 之积作为体积的近似)
        volumes = []
        for b in boxes:
            ranges = np.max(b, axis=0) - np.min(b, axis=0)
            volumes.append(np.prod(ranges + 1))  # +1 避免零体积
        largest_idx = int(np.argmax(volumes))
        largest_box = boxes.pop(largest_idx)

        # 切割
        ranges = np.max(largest_box, axis=0) - np.min(largest_box, axis=0)
        channel = int(np.argmax(ranges))
        sorted_idx = np.argsort(largest_box[:, channel])
        largest_box = largest_box[sorted_idx]
        median = len(largest_box) // 2

        if median > 0:
            boxes.append(largest_box[:median])
            boxes.append(largest_box[median:])
        else:
            # 无法再切，放回去
            boxes.append(largest_box)
            break

    # 每个盒子的均值作为调色板
    palette = np.array([np.mean(b, axis=0).round() for b in boxes], dtype=np.float64)
    return palette


def quantize_grid(
    color_grid: np.ndarray, max_colors: int
) -> np.ndarray:
    """对颜色网格进行中值切割量化。

    Args:
        color_grid: (H, W, 3) numpy uint8 颜色网格
        max_colors: 最大颜色数量

    Returns:
        (H, W, 3) numpy uint8 量化后的颜色网格
    """
    h, w = color_grid.shape[:2]
    pixels = color_grid.reshape(-1, 3).astype(np.float64)

    # 先统计当前有多少种唯一颜色
    unique_colors = len(np.unique(pixels, axis=0))

    if unique_colors <= max_colors:
        # 不需要量化
        return color_grid

    # 中值切割得到调色板
    palette = median_cut(pixels, max_colors)  # (K, 3)

    # 将每个像素映射到最近的调色板颜色（在 RGB 空间中）
    # 使用广播计算距离
    # pixels: (N, 3), palette: (K, 3)
    # diff: (N, K, 3)
    diff = pixels[:, np.newaxis, :] - palette[np.newaxis, :, :]  # (N, K, 3)
    dist = np.sum(diff ** 2, axis=2)  # (N, K)
    nearest = np.argmin(dist, axis=1)  # (N,)

    # 用调色板颜色替换
    quantized_pixels = palette[nearest].astype(np.uint8)
    quantized_grid = quantized_pixels.reshape(h, w, 3)

    return quantized_grid
