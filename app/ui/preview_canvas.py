"""预览画布 —— 像素网格实时预览区。

将 Pattern 渲染为像素块图片，叠加网格线和底板边界，
通过 tkinter Canvas 显示。
"""

import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
from typing import Optional
import numpy as np

from app.core.pixelizer import (upsample_for_preview, draw_grid_lines,
                                draw_board_lines, add_coordinate_labels,
                                draw_color_codes)


class PreviewCanvas(ctk.CTkFrame):
    """像素预览画布。"""

    DEFAULT_TILE_SIZE = 20
    GRID_COLOR = (215, 207, 191)   # 暖灰 #d7cfbf
    BOARD_COLOR = (224, 90, 43)    # 陶土橙 #e05a2b

    def __init__(self, master):
        super().__init__(master)
        self.current_image: Optional[ImageTk.PhotoImage] = None
        self.canvas_image_id = None

        # Canvas
        self.canvas = ctk.CTkCanvas(self, bg="#fffdf8", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # 滚动条
        self.scrollbar_y = ctk.CTkScrollbar(
            self, orientation="vertical", command=self.canvas.yview
        )
        self.scrollbar_x = ctk.CTkScrollbar(
            self, orientation="horizontal", command=self.canvas.xview
        )
        self.canvas.configure(
            yscrollcommand=self.scrollbar_y.set,
            xscrollcommand=self.scrollbar_x.set,
        )

        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")

        # 占位提示
        self.canvas.create_text(
            200, 200,
            text="请先加载图片",
            fill="#8a8378",
            font=("Microsoft YaHei", 14),
        )

    def show_pattern(
        self,
        pattern,
        params: dict,
        palette=None,
        tile_size: int = None,
    ):
        """渲染并显示图案预览。

        Args:
            pattern: Pattern 对象
            params: 参数字典 (show_grid, show_board_lines, show_color_codes, board_width, board_height)
            palette: BeadPalette 色卡对象 (色号标注时需要)
            tile_size: 每个豆子的显示像素大小
        """
        if tile_size is None:
            tile_size = self.DEFAULT_TILE_SIZE

        if pattern.grid is None or pattern.grid.size == 0:
            return

        # 上采样
        preview = upsample_for_preview(pattern.grid, tile_size)

        show_grid = params.get("show_grid", True)
        show_boards = params.get("show_board_lines", True)
        show_codes = params.get("show_color_codes", False)

        # 网格线（含每5格强调线）
        if show_grid:
            preview = draw_grid_lines(preview, tile_size, self.GRID_COLOR)

        # 底板边界（仅在网格开启时有对齐参考意义）
        if show_grid and show_boards:
            bw = params.get("board_width", 29)
            bh = params.get("board_height", 29)
            preview = draw_board_lines(preview, tile_size, bw, bh, self.BOARD_COLOR)

        # 色号标注（在坐标标注之前，因为坐标标注会加边距）
        if show_codes and palette is not None:
            preview = draw_color_codes(preview, pattern.indices, palette, tile_size)

        # 行列号标注
        bead_w, bead_h = pattern.bead_size
        preview = add_coordinate_labels(preview, tile_size, bead_w, bead_h)

        # 显示在 Canvas
        self.current_image = ImageTk.PhotoImage(preview)
        self.canvas.delete("all")
        self.canvas_image_id = self.canvas.create_image(
            0, 0, anchor="nw", image=self.current_image
        )
        self.canvas.configure(scrollregion=(0, 0, preview.width, preview.height))

        # 更新滚动条
        self.scrollbar_y.set(0, 1)
        self.scrollbar_x.set(0, 1)
