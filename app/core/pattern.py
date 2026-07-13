"""图案数据模型。

表示一个完整的拼豆设计方案，包含：
- 像素化后的颜色网格
- 色卡匹配结果
- 底板布局信息
- 颜色统计
"""

from dataclasses import dataclass, field
from typing import Optional

import numpy as np


@dataclass
class BoardLayout:
    """底板布局信息。"""
    cols: int          # 水平方向底板数
    rows: int          # 垂直方向底板数
    total: int         # 总底板数
    board_w: int = 29  # 每块底板宽度 (豆子数)
    board_h: int = 29  # 每块底板高度 (豆子数)


@dataclass
class Pattern:
    """拼豆图案数据模型。

    这是整个管道的输出产物，供预览渲染和导出模块消费。
    """

    # 核心数据
    grid: np.ndarray          # (H, W, 3) 最终匹配后的 RGB 颜色网格
    indices: np.ndarray       # (H, W) 色卡索引

    # 中间产物（可选，用于调试/重新匹配）
    raw_grid: Optional[np.ndarray] = None  # 降采样后的原始颜色（匹配前）

    # 统计信息
    color_summary: list[dict] = field(default_factory=list)
    unique_colors: int = 0
    total_beads: int = 0

    # 底板
    board_layout: Optional[BoardLayout] = None

    # 参数记录
    pixel_size: int = 1
    max_colors: int = 256
    brand: str = "MARD"

    # 原始图片信息
    original_size: tuple[int, int] = (0, 0)

    @property
    def bead_size(self) -> tuple[int, int]:
        """返回 (宽, 高) 豆子数。"""
        if self.grid is not None and self.grid.ndim == 3:
            h, w = self.grid.shape[:2]
            return (w, h)
        return (0, 0)

    @property
    def aspect_ratio(self) -> float:
        """宽高比。"""
        w, h = self.bead_size
        if h > 0:
            return w / h
        return 1.0

    def compute_stats(self, palette):
        """根据 grid 和 indices 重新计算统计信息。"""
        from app.core.color_matcher import generate_color_summary

        self.unique_colors = len(np.unique(self.indices))
        self.total_beads = int(np.prod(self.indices.shape))
        self.color_summary = generate_color_summary(self.indices, palette)

    def compute_board_layout(self, board_w: int = 29, board_h: int = 29):
        """计算底板布局。"""
        import math

        bead_w, bead_h = self.bead_size
        cols = math.ceil(bead_w / board_w)
        rows = math.ceil(bead_h / board_h)

        self.board_layout = BoardLayout(
            cols=cols,
            rows=rows,
            total=cols * rows,
            board_w=board_w,
            board_h=board_h,
        )
