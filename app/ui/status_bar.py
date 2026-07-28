"""状态栏 —— 底部信息栏（绿点指示器）。"""

import customtkinter as ctk


BG   = "#f3f0ea"
SUB  = "#8a8378"
GREEN = "#57a773"


class StatusBar(ctk.CTkFrame):
    """底部状态栏，带绿色状态点。"""

    def __init__(self, master):
        super().__init__(master, height=32, fg_color=BG)
        self.pack_propagate(False)

        # 绿点
        dot = ctk.CTkFrame(self, fg_color=GREEN, width=8, height=8,
                            corner_radius=4)
        dot.pack(side="left", padx=(12, 6), pady=10)
        dot.pack_propagate(False)

        self.label = ctk.CTkLabel(
            self, text="就绪 · 请先加载图片",
            font=ctk.CTkFont(family="Microsoft YaHei", size=11),
            text_color=SUB, anchor="w",
        )
        self.label.pack(side="left", padx=2, pady=6)

    def show(self, text: str):
        self.label.configure(text=text)
