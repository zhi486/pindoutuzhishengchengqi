"""状态栏 —— 底部信息栏。"""

import customtkinter as ctk


class StatusBar(ctk.CTkFrame):
    """底部状态栏。"""

    def __init__(self, master):
        super().__init__(master, height=28, fg_color="#f3f0ea")
        self.pack_propagate(False)

        self.label = ctk.CTkLabel(
            self,
            text="就绪",
            font=ctk.CTkFont(size=11),
            text_color="#8a8378",
            anchor="w",
        )
        self.label.pack(side="left", padx=10, pady=2)

    def show(self, text: str):
        """更新状态文本。"""
        self.label.configure(text=text)
