"""控制面板 —— 品牌·材质·参数·导出。

使用卡片式分区，每区带 accent 左侧色条标题。
"""

import customtkinter as ctk
from typing import Callable


# ═══════════════ 设计令牌 ═══════════════
ACCENT       = "#e05a2b"
ACCENT_HOVER = "#c94e24"
ACCENT_SOFT  = "#fbe9df"
CARD         = "#fffdf8"
TEXT         = "#211d19"
SUB          = "#8a8378"
BORDER       = "#e7e1d4"
RADIUS       = 10


def _make_card(parent, title: str) -> ctk.CTkFrame:
    """创建带 accent 色条标题的卡片。

    返回 (card_frame, content_frame) — content_frame 用来放置内容。
    """
    card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=RADIUS,
                         border_width=1, border_color=BORDER)
    # 标题行: accent 色条 + 文字
    title_row = ctk.CTkFrame(card, fg_color="transparent")
    title_row.pack(fill="x", padx=14, pady=(14, 4))
    # accent 色条
    bar = ctk.CTkFrame(title_row, fg_color=ACCENT, width=3, height=18, corner_radius=2)
    bar.pack(side="left", padx=(0, 8))
    bar.pack_propagate(False)
    title_lbl = ctk.CTkLabel(
        title_row,
        text=title,
        font=ctk.CTkFont(family="Microsoft YaHei", size=12, weight="bold"),
        text_color="#6f685d",
    )
    title_lbl.pack(side="left")
    # 内容区
    content = ctk.CTkFrame(card, fg_color="transparent")
    content.pack(fill="x", padx=14, pady=(4, 12))
    return card, content


class ControlPanel(ctk.CTkFrame):
    """参数控制面板。"""

    ZOOM_LEVELS = [5, 8, 10, 12, 15, 18, 20, 25, 30, 40, 50]
    DEFAULT_ZOOM = 20

    def __init__(
        self,
        master,
        on_param_changed: Callable[[str, object], None],
        on_zoom_changed: Callable[[int], None],
        on_export_png: Callable[[], None],
        on_export_pdf: Callable[[], None],
        on_material_changed: Callable[[str], None] = None,
    ):
        super().__init__(master, fg_color="transparent")
        self.on_param_changed = on_param_changed
        self.on_zoom_changed = on_zoom_changed
        self.on_material_changed = on_material_changed
        self._tile_size = self.DEFAULT_ZOOM

        # ═══ 卡片 1: 豆子品牌 ═══
        card1, c1 = _make_card(self, "豆子品牌")

        ctk.CTkLabel(c1, text="品牌", font=ctk.CTkFont(size=12),
                     text_color=SUB, anchor="w").pack(fill="x")
        ctk.CTkLabel(c1, text="MARD",
                     font=ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold"),
                     text_color=TEXT, anchor="w").pack(fill="x", pady=(2, 6))

        ctk.CTkLabel(c1, text="材质", font=ctk.CTkFont(size=12),
                     text_color=SUB, anchor="w").pack(fill="x")
        self.material_var = ctk.StringVar(value="实色")
        self.material_menu = ctk.CTkOptionMenu(
            c1,
            values=["实色", "半透明"],
            variable=self.material_var,
            command=self._on_material,
            fg_color="#fff",
            text_color=TEXT,
            button_color=ACCENT,
            button_hover_color=ACCENT_HOVER,
            corner_radius=8,
            font=ctk.CTkFont(family="Microsoft YaHei", size=13),
            dropdown_font=ctk.CTkFont(family="Microsoft YaHei", size=13),
        )
        self.material_menu.pack(fill="x")

        self.material_note = ctk.CTkLabel(
            c1, text="", anchor="w",
            text_color="#8a6d14",
            font=ctk.CTkFont(family="Microsoft YaHei", size=11),
            wraplength=220, justify="left",
        )

        card1.pack(fill="x", pady=(0, 8))

        # ═══ 卡片 2: 图纸参数 ═══
        card2, c2 = _make_card(self, "图纸参数")

        self.bead_h_var = ctk.IntVar(value=52)
        self._build_row(c2, "豆子长度", 5, 200, 52,
                        self.bead_h_var,
                        self._on_bead_h, self._on_bead_h)
        self.bead_w_label = ctk.CTkLabel(
            c2, text="宽度: — 列", anchor="w",
            font=ctk.CTkFont(family="Microsoft YaHei", size=11),
            text_color=SUB)
        self.bead_w_label.pack(fill="x", pady=(0, 4))

        self.max_colors_var = ctk.IntVar(value=50)
        self._build_row(c2, "最大颜色", 4, 150, 50,
                        self.max_colors_var,
                        self._on_max_colors, self._on_max_colors)

        card2.pack(fill="x", pady=(0, 8))

        # ═══ 卡片 3: 显示选项 ═══
        card3, c3 = _make_card(self, "显示选项")

        self.show_grid_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            c3, text="显示网格线",
            variable=self.show_grid_var,
            command=lambda: self._emit("show_grid", self.show_grid_var.get()),
            fg_color=ACCENT, hover_color=ACCENT_HOVER, checkmark_color="#fff",
            border_color=BORDER, text_color=TEXT,
            font=ctk.CTkFont(family="Microsoft YaHei", size=13),
        ).pack(fill="x", pady=2)

        self.show_boards_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            c3, text="显示底板边界",
            variable=self.show_boards_var,
            command=lambda: self._emit("show_board_lines", self.show_boards_var.get()),
            fg_color=ACCENT, hover_color=ACCENT_HOVER, checkmark_color="#fff",
            border_color=BORDER, text_color=TEXT,
            font=ctk.CTkFont(family="Microsoft YaHei", size=13),
        ).pack(fill="x", pady=2)

        self.show_codes_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            c3, text="显示色号",
            variable=self.show_codes_var,
            command=lambda: self._emit("show_color_codes", self.show_codes_var.get()),
            fg_color=ACCENT, hover_color=ACCENT_HOVER, checkmark_color="#fff",
            border_color=BORDER, text_color=TEXT,
            font=ctk.CTkFont(family="Microsoft YaHei", size=13),
        ).pack(fill="x", pady=2)

        # 底板尺寸
        row4 = ctk.CTkFrame(c3, fg_color="transparent")
        row4.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(row4, text="底板尺寸", font=ctk.CTkFont(size=12),
                     text_color=SUB).pack(side="left")
        self.board_type_var = ctk.StringVar(value="52×52")
        ctk.CTkOptionMenu(
            row4,
            values=["52×52", "104×104", "208×208"],
            variable=self.board_type_var,
            command=self._on_board_type,
            fg_color="#fff", text_color=TEXT,
            button_color=ACCENT, button_hover_color=ACCENT_HOVER,
            corner_radius=8,
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            dropdown_font=ctk.CTkFont(family="Microsoft YaHei", size=12),
            width=100,
        ).pack(side="right")

        card3.pack(fill="x", pady=(0, 8))

        # ═══ 卡片 4: 预览缩放 ═══
        card4, c4 = _make_card(self, "预览缩放")

        zoom_row = ctk.CTkFrame(c4, fg_color="transparent")
        zoom_row.pack()

        self.zoom_out_btn = ctk.CTkButton(
            zoom_row, text="−", width=34, height=28,
            command=self._zoom_out,
            fg_color=SUB, hover_color="#6f685d",
            corner_radius=8,
            font=ctk.CTkFont(size=16),
        )
        self.zoom_out_btn.pack(side="left", padx=2)

        self.zoom_label = ctk.CTkLabel(
            zoom_row, text="20 px", width=60,
            font=ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold"),
            text_color=TEXT,
        )
        self.zoom_label.pack(side="left")

        self.zoom_in_btn = ctk.CTkButton(
            zoom_row, text="+", width=34, height=28,
            command=self._zoom_in,
            fg_color=SUB, hover_color="#6f685d",
            corner_radius=8,
            font=ctk.CTkFont(size=16),
        )
        self.zoom_in_btn.pack(side="left", padx=2)

        self.zoom_reset_btn = ctk.CTkButton(
            zoom_row, text="↺", width=28, height=28,
            command=self._zoom_reset,
            fg_color="transparent", text_color=SUB,
            hover_color=ACCENT_SOFT,
            corner_radius=8,
            border_width=1, border_color=BORDER,
            font=ctk.CTkFont(size=13),
        )
        self.zoom_reset_btn.pack(side="left", padx=(6, 0))

        card4.pack(fill="x", pady=(0, 8))

        # ═══ 卡片 5: 导出图纸 ═══
        card5, c5 = _make_card(self, "导出图纸")

        btn_row = ctk.CTkFrame(c5, fg_color="transparent")
        btn_row.pack(fill="x")
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            btn_row, text="导出 PNG",
            command=on_export_png,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            corner_radius=10, height=38,
            font=ctk.CTkFont(family="Microsoft YaHei", size=13, weight="bold"),
            text_color="#fff",
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))

        ctk.CTkButton(
            btn_row, text="导出 PDF",
            command=on_export_pdf,
            fg_color="#2c2721", hover_color="#1e1a15",
            corner_radius=10, height=38,
            font=ctk.CTkFont(family="Microsoft YaHei", size=13, weight="bold"),
            text_color="#f2ede4",
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0))

        card5.pack(fill="x")

    # ── 控件构建辅助 ─────────────────────────

    def _build_row(self, parent, label, from_val, to_val, default, var, slider_cb, entry_cb):
        """构建一行: label + slider + entry。"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=2)

        ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=12),
                     text_color=SUB, width=68, anchor="w").pack(side="left")

        s = ctk.CTkSlider(
            row,
            from_=from_val, to=to_val,
            variable=var,
            command=slider_cb,
            progress_color=ACCENT,
            button_color=ACCENT,
            button_hover_color=ACCENT_HOVER,
            height=14,
        )
        s.pack(side="left", fill="x", expand=True, padx=4)
        # 设置初始值
        var.set(default)

        e = ctk.CTkEntry(row, width=50, height=26,
                         textvariable=var,
                         fg_color="#fff", border_color=BORDER,
                         corner_radius=6,
                         font=ctk.CTkFont(family="Microsoft YaHei", size=12),
                         text_color=TEXT)
        e.pack(side="right")
        e.bind("<Return>", entry_cb)
        e.bind("<FocusOut>", entry_cb)

    # ── 材质 ────────────────────────────────────

    def _on_material(self, choice: str):
        if self.on_material_changed:
            self.on_material_changed(choice)

    def show_material_note(self, text: str):
        if text:
            self.material_note.configure(text=text)
            self.material_note.pack(fill="x", pady=(6, 0))
        else:
            self.material_note.pack_forget()

    # ── 豆子长度 ────────────────────────────────

    def set_bead_w_display(self, w: int):
        self.bead_w_label.configure(text=f"宽度: {w} 列")

    def _on_bead_h(self, val):
        v = int(float(val))
        self.bead_h_var.set(v)
        self._emit("max_beads_h", v)

    # ── 最大颜色 ─────────────────────────────────

    def _on_max_colors(self, val):
        v = int(float(val))
        self.max_colors_var.set(v)
        self._emit("max_colors", v)

    # ── 底板 ─────────────────────────────────────

    def _on_board_type(self, choice):
        size = int(choice.split("×")[0])
        self._emit("board_width", size)
        self._emit("board_height", size)

    # ── 缩放 ─────────────────────────────────────

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

    # ── 通用 ─────────────────────────────────────

    def _emit(self, key, value):
        self.on_param_changed(key, value)

    def params_get(self) -> dict:
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
