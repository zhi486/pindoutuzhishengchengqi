"""颜色图例面板 —— 色块 + 色号 + 数量。"""

import customtkinter as ctk


CARD   = "#fffdf8"
TEXT   = "#211d19"
SUB    = "#8a8378"
ACCENT = "#e05a2b"
BORDER = "#e7e1d4"
RADIUS = 10


class ColorLegendPanel(ctk.CTkFrame):
    """颜色图例。"""

    def __init__(self, master):
        super().__init__(master, fg_color=CARD, corner_radius=RADIUS,
                         border_width=1, border_color=BORDER)
        # 标题
        self._title()
        self.legend_items = []

    def _title(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(12, 6))
        bar = ctk.CTkFrame(row, fg_color=ACCENT, width=3, height=18, corner_radius=2)
        bar.pack(side="left", padx=(0, 8))
        bar.pack_propagate(False)
        ctk.CTkLabel(
            row, text="颜色图例",
            font=ctk.CTkFont(family="Microsoft YaHei", size=12, weight="bold"),
            text_color="#6f685d",
        ).pack(side="left")

    def show_legend(self, colors: list[dict]):
        for item in self.legend_items:
            item.destroy()
        self.legend_items.clear()

        if not colors:
            no_data = ctk.CTkLabel(self, text="暂无数据", text_color=SUB,
                                    font=ctk.CTkFont(family="Microsoft YaHei", size=12))
            no_data.pack(pady=8, padx=12)
            self.legend_items.append(no_data)
            return

        total = sum(c["count"] for c in colors)

        for color in colors:
            row = ctk.CTkFrame(self, fg_color="transparent", height=30)
            row.pack(fill="x", padx=10, pady=1)
            row.pack_propagate(False)

            # 色块
            swatch = ctk.CTkFrame(
                row, width=28, height=20, fg_color=color["hex"],
                corner_radius=4,
            )
            swatch.pack(side="left", padx=(6, 10))
            swatch.pack_propagate(False)

            # 色号
            code_lbl = ctk.CTkLabel(
                row, text=color["code"],
                font=ctk.CTkFont(family="Microsoft YaHei", size=12, weight="bold"),
                width=42, anchor="w", text_color=TEXT,
            )
            code_lbl.pack(side="left")

            # 数量
            count_lbl = ctk.CTkLabel(
                row, text=f"{color['count']} 颗",
                font=ctk.CTkFont(family="Microsoft YaHei", size=11),
                text_color=SUB, width=60, anchor="e",
            )
            count_lbl.pack(side="right", padx=(0, 6))

            self.legend_items.append(row)

        # 分隔线
        sep = ctk.CTkFrame(self, fg_color=BORDER, height=1)
        sep.pack(fill="x", padx=10, pady=(4, 2))
        self.legend_items.append(sep)

        # 汇总行
        total_row = ctk.CTkFrame(self, fg_color="transparent", height=28)
        total_row.pack(fill="x", padx=10)
        total_row.pack_propagate(False)
        ctk.CTkLabel(
            total_row, text=f"共 {len(colors)} 种颜色 · {total} 颗",
            font=ctk.CTkFont(family="Microsoft YaHei", size=11, weight="bold"),
            text_color="#6f685d",
        ).pack(side="left", padx=6)
        self.legend_items.append(total_row)
