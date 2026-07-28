"""预览画布 —— 像素网格实时预览区。"""

import customtkinter as ctk
from PIL import Image, ImageTk
from typing import Optional


CARD   = "#fffdf8"
ACCENT = "#e05a2b"
SUB    = "#8a8378"
RADIUS = 12


class PreviewCanvas(ctk.CTkFrame):
    """像素预览画布。"""

    DEFAULT_TILE_SIZE = 20
    GRID_COLOR = (215, 207, 191)    # 暖灰
    BOARD_COLOR = (224, 90, 43)     # 陶土橙

    def __init__(self, master):
        super().__init__(master, fg_color=CARD, corner_radius=RADIUS,
                         border_width=1, border_color="#e7e1d4")
        self.current_image: Optional[ImageTk.PhotoImage] = None
        self.canvas_image_id = None

        # Canvas
        self.canvas = ctk.CTkCanvas(self, bg="#fffdf8", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=2, pady=2)

        # 居中占位文字（使用 Label 而非 canvas.create_text，自动居中）
        self.placeholder = ctk.CTkLabel(
            self, text="请先加载图片",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14),
            text_color=SUB,
        )
        self.placeholder.place(relx=0.5, rely=0.5, anchor="center")

        # 滚动条
        self.scrollbar_y = ctk.CTkScrollbar(
            self, orientation="vertical", command=self.canvas.yview)
        self.scrollbar_x = ctk.CTkScrollbar(
            self, orientation="horizontal", command=self.canvas.xview)
        self.canvas.configure(
            yscrollcommand=self.scrollbar_y.set,
            xscrollcommand=self.scrollbar_x.set,
        )
        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")

    def show_pattern(self, pattern, params: dict, palette=None, tile_size: int = None):
        if tile_size is None:
            tile_size = self.DEFAULT_TILE_SIZE
        if pattern.grid is None or pattern.grid.size == 0:
            return

        # 隐藏占位文字
        self.placeholder.place_forget()

        # 延迟导入避免循环依赖
        from app.core.pixelizer import (upsample_for_preview, draw_grid_lines,
                                        draw_board_lines, add_coordinate_labels,
                                        draw_color_codes)

        preview = upsample_for_preview(pattern.grid, tile_size)

        show_grid = params.get("show_grid", True)
        show_boards = params.get("show_board_lines", True)
        show_codes = params.get("show_color_codes", False)

        if show_grid:
            preview = draw_grid_lines(preview, tile_size, self.GRID_COLOR)
        if show_grid and show_boards:
            bw = params.get("board_width", 29)
            bh = params.get("board_height", 29)
            preview = draw_board_lines(preview, tile_size, bw, bh, self.BOARD_COLOR)
        if show_codes and palette is not None:
            preview = draw_color_codes(preview, pattern.indices, palette, tile_size)

        bead_w, bead_h = pattern.bead_size
        preview = add_coordinate_labels(preview, tile_size, bead_w, bead_h)

        self.current_image = ImageTk.PhotoImage(preview)
        self.canvas.delete("all")
        self.canvas_image_id = self.canvas.create_image(
            0, 0, anchor="nw", image=self.current_image)
        self.canvas.configure(scrollregion=(0, 0, preview.width, preview.height))
        self.scrollbar_y.set(0, 1)
        self.scrollbar_x.set(0, 1)
