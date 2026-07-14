"""控制面板 —— 参数调节滑块与导出按钮。"""

import customtkinter as ctk
from typing import Callable


class ControlPanel(ctk.CTkScrollableFrame):
    """参数控制面板 —— 豆子长度、最大颜色、显示选项、导出。"""

    def __init__(
        self,
        master,
        on_param_changed: Callable[[str, object], None],
        on_zoom_changed: Callable[[int], None],
        on_export_png: Callable[[], None],
        on_export_pdf: Callable[[], None],
        on_palette_mode_changed: Callable[[str], None] = None,
    ):
        super().__init__(master, label_text="参数设置", width=250)
        self.on_param_changed = on_param_changed
        self.on_zoom_changed = on_zoom_changed
        self.on_palette_mode_changed = on_palette_mode_changed
        self._tile_size = 20

        # ── 色卡模式切换 ──
        ctk.CTkLabel(self, text="色卡模式", anchor="w").pack(
            fill="x", padx=10, pady=(10, 0)
        )

        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.pack(fill="x", padx=10, pady=(2, 0))

        self.palette_mode_var = ctk.StringVar(value="291")
        self.btn_291 = ctk.CTkButton(
            mode_frame, text="291 色", width=90, height=30,
            command=lambda: self._on_palette_mode("291"),
            fg_color="#3B82F6", hover_color="#2563EB",
        )
        self.btn_291.pack(side="left", padx=(0, 5))

        self.btn_221 = ctk.CTkButton(
            mode_frame, text="221 色", width=90, height=30,
            command=lambda: self._on_palette_mode("221"),
            fg_color="#6B7280", hover_color="#4B5563",
        )
        self.btn_221.pack(side="left")

        # ── 豆子长度（行数）──
        ctk.CTkLabel(self, text="豆子长度（行数）", anchor="w").pack(
            fill="x", padx=10, pady=(10, 0)
        )

        bh_frame = ctk.CTkFrame(self, fg_color="transparent")
        bh_frame.pack(fill="x", padx=10, pady=(2, 0))

        self.bead_h_var = ctk.IntVar(value=52)
        self.bead_h_slider = ctk.CTkSlider(
            bh_frame,
            from_=5, to=200,
            number_of_steps=39,
            variable=self.bead_h_var,
            command=self._on_bead_h_slider,
        )
        self.bead_h_slider.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.bead_h_entry = ctk.CTkEntry(bh_frame, width=50, textvariable=self.bead_h_var)
        self.bead_h_entry.pack(side="right")
        self.bead_h_entry.bind("<Return>", self._on_bead_h_entry)
        self.bead_h_entry.bind("<FocusOut>", self._on_bead_h_entry)

        self.bead_w_label = ctk.CTkLabel(self, text="宽度: — 列", anchor="w",
                                          font=ctk.CTkFont(size=11), text_color="gray50")
        self.bead_w_label.pack(fill="x", padx=10, pady=(0, 0))

        # ── 最大颜色数 ──
        ctk.CTkLabel(self, text="最大颜色数", anchor="w").pack(
            fill="x", padx=10, pady=(10, 0)
        )

        mc_frame = ctk.CTkFrame(self, fg_color="transparent")
        mc_frame.pack(fill="x", padx=10, pady=(2, 0))

        self.max_colors_var = ctk.IntVar(value=50)
        self.max_colors_slider = ctk.CTkSlider(
            mc_frame,
            from_=4, to=150,
            number_of_steps=50,
            variable=self.max_colors_var,
            command=self._on_max_colors_slider,
        )
        self.max_colors_slider.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.max_colors_entry = ctk.CTkEntry(mc_frame, width=50, textvariable=self.max_colors_var)
        self.max_colors_entry.pack(side="right")
        self.max_colors_entry.bind("<Return>", self._on_max_colors_entry)
        self.max_colors_entry.bind("<FocusOut>", self._on_max_colors_entry)

        # ── 显示选项 ──
        ctk.CTkLabel(self, text="显示选项", anchor="w").pack(
            fill="x", padx=10, pady=(15, 0)
        )

        self.show_grid_var = ctk.BooleanVar(value=True)
        self.grid_cb = ctk.CTkCheckBox(
            self, text="显示网格线",
            variable=self.show_grid_var,
            command=lambda: self._emit("show_grid", self.show_grid_var.get()),
        )
        self.grid_cb.pack(fill="x", padx=15, pady=(5, 0))

        self.show_boards_var = ctk.BooleanVar(value=True)
        self.boards_cb = ctk.CTkCheckBox(
            self, text="显示底板边界",
            variable=self.show_boards_var,
            command=lambda: self._emit("show_board_lines", self.show_boards_var.get()),
        )
        self.boards_cb.pack(fill="x", padx=15, pady=(2, 0))

        self.show_codes_var = ctk.BooleanVar(value=True)
        self.codes_cb = ctk.CTkCheckBox(
            self, text="显示色号",
            variable=self.show_codes_var,
            command=lambda: self._emit("show_color_codes", self.show_codes_var.get()),
        )
        self.codes_cb.pack(fill="x", padx=15, pady=(2, 0))

        # ── 底板尺寸 ──
        ctk.CTkLabel(self, text="底板尺寸", anchor="w").pack(
            fill="x", padx=10, pady=(15, 0)
        )
        self.board_type_var = ctk.StringVar(value="52×52")
        self.board_menu = ctk.CTkOptionMenu(
            self,
            values=["52×52", "72×72", "102×102"],
            variable=self.board_type_var,
            command=self._on_board_type,
        )
        self.board_menu.pack(fill="x", padx=10, pady=(2, 0))

        # ── 预览缩放 ──
        ctk.CTkLabel(self, text="预览缩放", anchor="w").pack(
            fill="x", padx=10, pady=(15, 0)
        )

        zoom_frame = ctk.CTkFrame(self, fg_color="transparent")
        zoom_frame.pack(fill="x", padx=10, pady=(5, 0))

        self.zoom_out_btn = ctk.CTkButton(
            zoom_frame, text="−", width=36, height=30,
            command=self._zoom_out,
            fg_color="#6B7280", hover_color="#4B5563",
        )
        self.zoom_out_btn.pack(side="left", padx=(0, 5))

        self.zoom_label = ctk.CTkLabel(
            zoom_frame, text="20 px", width=50,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.zoom_label.pack(side="left")

        self.zoom_in_btn = ctk.CTkButton(
            zoom_frame, text="+", width=36, height=30,
            command=self._zoom_in,
            fg_color="#6B7280", hover_color="#4B5563",
        )
        self.zoom_in_btn.pack(side="left", padx=(5, 0))

        self.zoom_reset_btn = ctk.CTkButton(
            zoom_frame, text="↺", width=30, height=30,
            command=self._zoom_reset,
            fg_color="transparent", text_color="#6B7280",
            hover_color="#E5E7EB", border_width=1,
        )
        self.zoom_reset_btn.pack(side="right")

        # ── 导出按钮 ──
        ctk.CTkLabel(self, text="导出图纸", anchor="w").pack(
            fill="x", padx=10, pady=(20, 0)
        )

        self.export_png_btn = ctk.CTkButton(
            self, text="导出 PNG",
            command=on_export_png,
            width=200, height=36,
            fg_color="#3B82F6", hover_color="#2563EB",
        )
        self.export_png_btn.pack(pady=(5, 0))

        self.export_pdf_btn = ctk.CTkButton(
            self, text="导出 PDF",
            command=on_export_pdf,
            width=200, height=36,
            fg_color="#EF4444", hover_color="#DC2626",
        )
        self.export_pdf_btn.pack(pady=(5, 10))

    # ── 色卡模式 ──────────────────────────────────

    def _on_palette_mode(self, mode: str):
        """切换色卡模式，更新按钮高亮状态。"""
        self.palette_mode_var.set(mode)
        if mode == "291":
            self.btn_291.configure(fg_color="#3B82F6", hover_color="#2563EB")
            self.btn_221.configure(fg_color="#6B7280", hover_color="#4B5563")
        else:
            self.btn_221.configure(fg_color="#3B82F6", hover_color="#2563EB")
            self.btn_291.configure(fg_color="#6B7280", hover_color="#4B5563")
        if self.on_palette_mode_changed:
            self.on_palette_mode_changed(mode)

    # ── 豆子长度 ──────────────────────────────────

    def set_bead_w_display(self, w: int):
        """由主窗口调用，显示自动计算的宽度。"""
        self.bead_w_label.configure(text=f"宽度: {w} 列")

    def _on_bead_h_slider(self, val):
        v = int(float(val))
        self.bead_h_var.set(v)
        self._emit("max_beads_h", v)

    def _on_bead_h_entry(self, event):
        try:
            v = int(self.bead_h_entry.get())
            v = max(5, min(200, v))
            self.bead_h_var.set(v)
            self._emit("max_beads_h", v)
        except ValueError:
            self.bead_h_var.set(self.params_get()["max_beads_h"])

    # ── 最大颜色数 ────────────────────────────────

    def _on_max_colors_slider(self, val):
        v = int(float(val))
        self.max_colors_var.set(v)
        self._emit("max_colors", v)

    def _on_max_colors_entry(self, event):
        try:
            v = int(self.max_colors_entry.get())
            v = max(4, min(150, v))
            self.max_colors_var.set(v)
            self._emit("max_colors", v)
        except ValueError:
            self.max_colors_var.set(self.params_get()["max_colors"])

    # ── 底板 ─────────────────────────────────────

    def _on_board_type(self, choice):
        size = int(choice.replace("×", "").split("x")[0]) if "×" in choice else 52
        self._emit("board_width", size)
        self._emit("board_height", size)

    # ── 通用 ──────────────────────────────────────

    def _emit(self, key, value):
        self.on_param_changed(key, value)

    def params_get(self) -> dict:
        """获取当前所有参数（不含自动计算的宽度）。"""
        size = int(self.board_type_var.get().split("×")[0])
        return {
            "max_beads_h": int(self.bead_h_var.get()),
            "max_colors": int(self.max_colors_var.get()),
            "show_grid": bool(self.show_grid_var.get()),
            "show_board_lines": bool(self.show_boards_var.get()),
            "show_color_codes": bool(self.show_codes_var.get()),
            "board_width": size,
            "board_height": size,
        }

    # ── 缩放控制 ──────────────────────────────────

    ZOOM_LEVELS = [5, 8, 10, 12, 15, 18, 20, 25, 30, 40, 50]
    DEFAULT_ZOOM = 20

    def _zoom_in(self):
        current = self._tile_size
        for z in self.ZOOM_LEVELS:
            if z > current:
                self._tile_size = z
                break
        else:
            self._tile_size = min(current + 10, 50)
        self._update_zoom()

    def _zoom_out(self):
        current = self._tile_size
        for z in reversed(self.ZOOM_LEVELS):
            if z < current:
                self._tile_size = z
                break
        else:
            self._tile_size = max(current - 10, 3)
        self._update_zoom()

    def _zoom_reset(self):
        self._tile_size = self.DEFAULT_ZOOM
        self._update_zoom()

    def _update_zoom(self):
        self.zoom_label.configure(text=f"{self._tile_size} px")
        self.on_zoom_changed(self._tile_size)
