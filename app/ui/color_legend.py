"""颜色图例面板 —— 显示每种颜色的色号、色块、数量统计。"""

import customtkinter as ctk
from typing import Callable


class ColorLegendPanel(ctk.CTkScrollableFrame):
    """颜色图例 —— 按数量降序列出所有使用到的颜色。"""

    def __init__(self, master):
        super().__init__(master, label_text="颜色图例", fg_color="#fffdf8")
        self.legend_items = []

    def show_legend(self, colors: list[dict]):
        """刷新图例显示。

        Args:
            colors: 颜色信息列表，每项包含:
                code, name, hex, count, percentage
        """
        # 清除旧内容
        for item in self.legend_items:
            item.destroy()
        self.legend_items.clear()

        if not colors:
            no_data = ctk.CTkLabel(self, text="暂无数据", text_color="#8a8378")
            no_data.pack(pady=5)
            self.legend_items.append(no_data)
            return

        total = sum(c["count"] for c in colors)

        for color in colors:
            row = ctk.CTkFrame(self, fg_color="transparent", height=28)
            row.pack(fill="x", padx=5, pady=1)
            row.pack_propagate(False)

            # 色块
            swatch = ctk.CTkFrame(
                row, width=24, height=18, fg_color=color["hex"], corner_radius=2
            )
            swatch.pack(side="left", padx=(5, 8))
            swatch.pack_propagate(False)

            # 色号 (MARD 编号)
            code_label = ctk.CTkLabel(
                row,
                text=color["code"],
                font=ctk.CTkFont(size=12, weight="bold"),
                width=45,
                anchor="w",
            )
            code_label.pack(side="left")

            # 数量
            count_label = ctk.CTkLabel(
                row,
                text=f"{color['count']} 颗",
                font=ctk.CTkFont(size=11),
                text_color="#8a8378",
                width=55,
                anchor="e",
            )
            count_label.pack(side="right", padx=(0, 5))

            self.legend_items.append(row)

        # 总计行
        total_row = ctk.CTkFrame(self, fg_color="transparent", height=30)
        total_row.pack(fill="x", padx=5, pady=(5, 2))
        total_label = ctk.CTkLabel(
            total_row,
            text=f"共 {len(colors)} 种颜色，总计 {total} 颗",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#6f685d",
        )
        total_label.pack(side="left", padx=5)
        self.legend_items.append(total_row)
