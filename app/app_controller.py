"""应用控制器 —— 数据中心，串联图像处理全流程。

负责:
1. 管理原始图片和参数状态
2. 串联 pixelizer → color_quantizer → color_matcher → pattern
3. 向 UI 层提供数据
"""

from typing import Optional

import numpy as np
from PIL import Image

from app.core.pixelizer import load_image, resize_to_beads
from app.core.color_quantizer import quantize_grid
from app.core.color_matcher import match_colors, generate_color_summary
from app.core.bead_palette import BeadPalette
from app.core.pattern import Pattern


class AppController:
    """应用主控制器。

    Attributes:
        palette: 色卡对象
        original_image: 原始 PIL Image
        current_pattern: 当前处理结果 (Pattern)
        params: 当前参数字典
    """

    def __init__(self):
        self.palette = BeadPalette()
        self.original_image: Optional[Image.Image] = None
        self.current_pattern: Optional[Pattern] = None

        # 默认参数
        self.params = {
            "max_beads_h": 52,
            "max_colors": 50,
            "show_grid": True,
            "show_board_lines": True,
            "board_width": 52,
            "board_height": 52,
        }

    # ── 图片管理 ──────────────────────────────────

    def load_image(self, filepath: str) -> Image.Image:
        """加载图片并初始化默认豆子尺寸。"""
        self.original_image = load_image(filepath)
        w, h = self.original_image.size
        # 默认高度取 52（一块底板），宽度按比例
        self.params["max_beads_h"] = 52
        return self.original_image

    def has_image(self) -> bool:
        """是否已加载图片。"""
        return self.original_image is not None

    @property
    def _max_beads_w(self) -> int:
        """根据长宽比自动计算豆子宽度。"""
        if self.original_image is None:
            return 52
        w, h = self.original_image.size
        return max(1, round(w / h * self.params["max_beads_h"]))

    # ── 参数管理 ──────────────────────────────────

    def set_param(self, key: str, value):
        """设置单个参数。"""
        self.params[key] = value

    def get_params(self) -> dict:
        """获取参数副本（含自动计算的宽度）。"""
        d = dict(self.params)
        d["max_beads_w"] = self._max_beads_w
        return d

    # ── 核心处理管道 ──────────────────────────────

    def process(self) -> Pattern:
        """执行完整的图像处理流程。

        流程:
        1. 计算像素大小
        2. 降采样得到颜色网格
        3. 颜色量化（可选）
        4. 色卡匹配
        5. 统计与底板计算

        Returns:
            Pattern 对象
        """
        if self.original_image is None:
            raise ValueError("未加载图片")

        img = self.original_image
        w, h = img.size
        target_h = self.params["max_beads_h"]
        target_w = self._max_beads_w

        # Step 1: 直接缩放到目标豆子尺寸（高精度，无误差）
        raw_grid = resize_to_beads(img, target_w, target_h)

        # Step 3: 颜色量化 (如果颜色太多)
        quantized = quantize_grid(raw_grid, self.params["max_colors"])

        # Step 4: 色卡匹配
        matched_grid, indices = match_colors(quantized, self.palette)

        # Step 5: 构建 Pattern
        pattern = Pattern(
            grid=matched_grid,
            indices=indices,
            raw_grid=raw_grid,
            max_colors=self.params["max_colors"],
            brand=self.palette.brand,
            original_size=(w, h),
        )

        # 统计
        pattern.compute_stats(self.palette)

        # 底板
        pattern.compute_board_layout(
            self.params["board_width"],
            self.params["board_height"],
        )

        self.current_pattern = pattern
        return pattern
