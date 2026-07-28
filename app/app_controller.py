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
        material_mode: 豆子材质类型（实色 / 半透明）
        params: 当前参数字典
    """

    def __init__(self):
        data_dir = _get_data_dir()

        # 加载三套色卡：全色、实色、半透明
        self._palette_full = BeadPalette(os.path.join(data_dir, "perler_colors.json"))
        self._palette_solid = None
        solid_path = os.path.join(data_dir, "perler_colors_221.json")
        if os.path.exists(solid_path):
            try:
                self._palette_solid = BeadPalette(solid_path)
            except Exception:
                self._palette_solid = None

        self._palette_trans = None
        trans_path = os.path.join(data_dir, "perler_colors_transparent.json")
        if os.path.exists(trans_path):
            try:
                self._palette_trans = BeadPalette(trans_path)
            except Exception:
                self._palette_trans = None

        self._material_mode = "实色"  # 实色 / 半透明
        self.original_image: Optional[Image.Image] = None
        self.current_pattern: Optional[Pattern] = None

        # 默认参数
        self.params = {
            "max_beads_h": 52,
            "max_colors": 50,
            "show_grid": True,
            "show_board_lines": True,
            "show_color_codes": True,
            "board_width": 52,
            "board_height": 52,
        }

    # ── 色卡 / 材质管理 ──────────────────────────────

    @property
    def palette(self) -> BeadPalette:
        """根据当前材质返回对应色卡：实色→221，半透明→70色透明。"""
        if self._material_mode == "半透明" and self._palette_trans is not None:
            return self._palette_trans
        if self._palette_solid is not None:
            return self._palette_solid
        return self._palette_full

    @property
    def material_mode(self) -> str:
        """当前豆子材质类型。"""
        return self._material_mode

    @material_mode.setter
    def material_mode(self, value: str):
        if value not in ("实色", "半透明"):
            raise ValueError(f"无效的材质类型: {value}")
        self._material_mode = value

    def get_material_note(self) -> str:
        """返回半透明材质的提示信息。"""
        if self._material_mode == "半透明":
            return ("⚠️ 半透明豆子拼在底板上会透出底板颜色，"
                    "成品效果与实色不同，建议先确认底板颜色。")
        return ""

    def has_solid_palette(self) -> bool:
        """实色色卡是否可用。"""
        return self._palette_solid is not None

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
