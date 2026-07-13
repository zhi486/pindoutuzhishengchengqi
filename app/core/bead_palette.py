"""拼豆色卡数据加载与管理。

支持 MARD 221 色号体系 (A01-H23 + M/P/R系列)。
提供色卡 JSON 文件加载、LAB 色彩空间预计算、以及基于 K-D 树的
最近邻颜色匹配接口。
"""

import json
import os
from pathlib import Path
from typing import Optional

import numpy as np
from scipy.spatial import cKDTree

from app.utils.color_space import rgb_to_lab


class BeadPalette:
    """拼豆品牌色卡。

    负责：
    1. 从 JSON 文件加载色卡数据（MARD 色号格式）
    2. 预计算 L*a*b* 值
    3. 构建 K-D 树用于快速最近邻颜色搜索

    Attributes:
        brand: 品牌名称
        codes: 色号列表 (如 ["A01", "A02", ...])
        names: 颜色中文名称列表
        rgb_values: (N, 3) RGB 数组（0-255）
        lab_values: (N, 3) CIE L*a*b* 数组
        categories: 颜色系列列表
        n_colors: 颜色总数
    """

    def __init__(self, json_path: Optional[str] = None):
        """初始化色卡。

        Args:
            json_path: 色卡 JSON 文件路径。
                       默认使用 data/perler_colors.json
        """
        if json_path is None:
            json_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data",
                "perler_colors.json",
            )

        data = self._load_json(json_path)
        self.brand = data["brand"]
        self.description = data.get("description", "")

        # 提取字段
        self.codes = [c.get("code", "") for c in data["colors"]]
        self.names = [c.get("name", "") for c in data["colors"]]
        self.categories = [c.get("category", "solid") for c in data["colors"]]

        # 提取 RGB 值 (N, 3) float64, 范围 0-255
        self.rgb_values = np.array(
            [c["rgb"] for c in data["colors"]], dtype=np.float64
        )
        self.n_colors = len(self.rgb_values)

        # 预计算 L*a*b* 值
        self.lab_values = rgb_to_lab(self.rgb_values)

        # 构建 K-D 树
        self._tree = cKDTree(self.lab_values)

    @staticmethod
    def _load_json(path: str) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def match(self, rgb_array: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """将 RGB 像素数组匹配到最近似的色卡颜色。

        在 CIE L*a*b* 色彩空间中使用欧几里得距离 (Delta-E CIE76)
        搜索最近邻。

        Args:
            rgb_array: (H, W, 3) 或 (N, 3) 的 RGB 数组，值范围 0-255

        Returns:
            (matched_rgb, indices) 元组:
                - matched_rgb: (H, W, 3) 或 (N, 3) 匹配后的 RGB 值
                - indices: (H, W) 或 (N,) 色卡索引
        """
        original_shape = rgb_array.shape

        # 展平为 (N, 3)
        if rgb_array.ndim == 3:
            h, w, c = rgb_array.shape
            pixels = rgb_array.reshape(-1, 3)
        else:
            h, w = None, None
            pixels = rgb_array

        # RGB → LAB
        lab_pixels = rgb_to_lab(pixels)

        # K-D 树查询最近邻
        distances, indices = self._tree.query(lab_pixels, k=1)

        # 获取匹配后的 RGB
        matched_rgb = self.rgb_values[indices]

        # 恢复原始形状
        if h is not None:
            matched_rgb = matched_rgb.reshape(h, w, 3)
            indices = indices.reshape(h, w)

        return matched_rgb.astype(np.uint8), indices

    def get_color_info(self, index: int) -> dict:
        """根据索引获取颜色信息（含 MARD 色号）。"""
        r, g, b = self.rgb_values[index].astype(int)
        return {
            "code": self.codes[index],
            "name": self.names[index],
            "rgb": [int(r), int(g), int(b)],
            "hex": f"#{r:02X}{g:02X}{b:02X}",
            "category": self.categories[index],
        }

    def get_hex_color(self, index: int) -> str:
        """获取指定索引颜色的十六进制字符串。"""
        r, g, b = self.rgb_values[index].astype(int)
        return f"#{r:02X}{g:02X}{b:02X}"

    def get_color_count_map(self, indices: np.ndarray) -> dict:
        """统计每种颜色在索引数组中的出现次数。

        Args:
            indices: (H, W) 色卡索引数组

        Returns:
            dict: {color_index: count} 按 count 降序排列
        """
        unique, counts = np.unique(indices, return_counts=True)
        sorted_idx = np.argsort(-counts)  # 降序
        return {
            int(unique[i]): int(counts[i]) for i in sorted_idx
        }

    def filter_by_category(self, categories: list[str]) -> "BeadPalette":
        """按类别筛选颜色，返回新的 BeadPalette。"""
        keep_indices = [
            i for i, cat in enumerate(self.categories)
            if cat in categories
        ]
        if not keep_indices:
            raise ValueError(f"没有类别为 {categories} 的颜色")

        new_palette = BeadPalette.__new__(BeadPalette)
        new_palette.brand = self.brand
        new_palette.description = f"{self.description} (filtered: {categories})"
        new_palette.codes = [self.codes[i] for i in keep_indices]
        new_palette.names = [self.names[i] for i in keep_indices]
        new_palette.categories = [self.categories[i] for i in keep_indices]
        new_palette.rgb_values = self.rgb_values[keep_indices]
        new_palette.lab_values = self.lab_values[keep_indices]
        new_palette.n_colors = len(keep_indices)
        new_palette._tree = cKDTree(new_palette.lab_values)
        return new_palette
