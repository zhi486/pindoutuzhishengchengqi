"""颜色匹配器 —— 将像素颜色映射到最近似的拼豆色卡颜色。

使用 CIE L*a*b* 色彩空间 + K-D 树实现感知准确的最近邻搜索。
"""

import numpy as np

from app.core.bead_palette import BeadPalette


def match_colors(
    color_grid: np.ndarray, palette: BeadPalette
) -> tuple[np.ndarray, np.ndarray]:
    """将降采样后的颜色网格匹配到拼豆色卡。

    这是颜色匹配的核心入口函数。对于颜色网格中的每个像素块，
    在 LAB 空间中寻找最接近的拼豆颜色。

    Args:
        color_grid: (H, W, 3) numpy uint8 颜色网格
        palette: BeadPalette 色卡对象

    Returns:
        (matched_grid, indices) 元组:
            - matched_grid: (H, W, 3) 匹配后的 RGB 颜色
            - indices: (H, W) 色卡索引（用于统计和查找颜色名称/色号）
    """
    return palette.match(color_grid)


def generate_color_summary(
    indices: np.ndarray, palette: BeadPalette
) -> list[dict]:
    """生成颜色汇总列表，用于填充 UI 中的颜色图例。

    Args:
        indices: (H, W) 色卡索引数组
        palette: BeadPalette 色卡对象

    Returns:
        按数量降序排列的颜色信息列表，每项包含:
            - code: MARD 色号 (如 "A01")
            - name: 颜色名称
            - rgb: [R, G, B]
            - hex: 十六进制颜色
            - count: 该颜色豆子数量
            - percentage: 占比 (%)
    """
    count_map = palette.get_color_count_map(indices)
    total = int(np.sum(list(count_map.values())))

    summary = []
    for idx, count in count_map.items():
        info = palette.get_color_info(idx)
        info["count"] = count
        info["percentage"] = round(count / total * 100, 1) if total > 0 else 0
        summary.append(info)

    return summary
