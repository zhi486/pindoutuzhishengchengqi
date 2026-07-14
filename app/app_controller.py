"""应用控制器 —— 数据中心，串联图像处理全流程。

负责:
1. 管理原始图片和参数状态
2. 串联 pixelizer → color_quantizer → color_matcher → pattern
3. 向 UI 层提供数据
4. 管理 291/221 色卡切换
"""

import os
from typing import Optional

import numpy as np
from PIL import Image

from app.core.pixelizer import load_image, resize_to_beads
from app.core.color_quantizer import quantize_grid
from app.core.color_matcher import match_colors, generate_color_summary
from app.core.bead_palette import BeadPalette
from app.core.pattern import Pattern


def _get_data_dir():
    """获取 data 目录路径（兼容 PyInstaller 打包）。"""
    import sys
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "data")
    return os.path.join(os.path.dirname(__file__), "..", "data")


class AppController:
    """应用主控制器。

    Attributes:
        original_image: 原始 PIL Image
        current_pattern: 当前处理结果 (Pattern)
        palette_mode: "291" 或 "221"
        params: 当前参数字典
    """

    def __init__(self):
        data_dir = _get_data_dir()

        # 加载两套色卡
        self._palette_291 = BeadPalette(os.path.join(data_dir, "perler_colors.json"))
        self._palette_221_path = os.path.join(data_dir, "perler_colors_221.json")
        self._palette_221 = None
        if os.path.exists(self._palette_221_path):
            try:
                self._palette_221 = BeadPalette(self._palette_221_path)
            except Exception:
                self._palette_221 = None

        self._palette_mode = "291"
        self.original_image: Optional[Image.Image] = None
        self.current_pattern: Optional[Pattern] = None

        # 默认参数
        self.params = {
            "max_beads_h": 52,
            "max_colors": 50,
            "show_grid": True,
            "show_board_lines": True,
            "show_color_codes": True,  # 默认开启色号
            "board_width": 52,
            "board_height": 52,
        }

    # ── 色卡管理 ──────────────────────────────────

    @property
    def palette(self) -> BeadPalette:
        """当前激活的色卡。"""
        if self._palette_mode == "221" and self._palette_221 is not None:
            return self._palette_221
        return self._palette_291

    @property
    def palette_mode(self) -> str:
        return self._palette_mode

    @palette_mode.setter
    def palette_mode(self, mode: str):
        if mode not in ("291", "221"):
            raise ValueError(f"无效的色卡模式: {mode}")
        if mode == "221" and self._palette_221 is None:
            raise FileNotFoundError(f"221色数据文件不存在: {self._palette_221_path}")
        self._palette_mode = mode

    def has_221_palette(self) -> bool:
        """221 色卡是否可用。"""
        return self._palette_221 is not None

    # ── 图片管理 ──────────────────────────────────

    def load_image(self, filepath: str) -> Image.Image:
        """加载图片并初始化默认豆子尺寸。"""
        self.original_image = load_image(filepath)
        w, h = self.original_image.size
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
        """执行完整的图像处理流程。"""
        if self.original_image is None:
            raise ValueError("未加载图片")

        img = self.original_image
        w, h = img.size
        target_h = self.params["max_beads_h"]
        target_w = self._max_beads_w

        # Step 1: 直接缩放到目标豆子尺寸
        raw_grid = resize_to_beads(img, target_w, target_h)

        # Step 2: 颜色量化
        quantized = quantize_grid(raw_grid, self.params["max_colors"])

        # Step 3: 色卡匹配（使用当前激活的 palette）
        matched_grid, indices = match_colors(quantized, self.palette)

        # Step 4: 构建 Pattern
        pattern = Pattern(
            grid=matched_grid,
            indices=indices,
            raw_grid=raw_grid,
            max_colors=self.params["max_colors"],
            brand=self.palette.brand,
            original_size=(w, h),
        )

        pattern.compute_stats(self.palette)
        pattern.compute_board_layout(
            self.params["board_width"],
            self.params["board_height"],
        )

        self.current_pattern = pattern
        return pattern
