"""图片加载区域 —— 网页版上传区风格。"""

import os
import customtkinter as ctk
from PIL import Image
from typing import Callable, Optional


ACCENT        = "#e05a2b"
ACCENT_SOFT   = "#fbe9df"
CARD          = "#fffdf8"
SUB           = "#8a8378"
BORDER_STRONG = "#d6cfbf"


class ImageDropZone(ctk.CTkFrame):
    """图片加载区域 —— 虚线边框 + 居中内容。"""

    def __init__(
        self,
        master,
        on_image_loaded: Callable[[str], None],
        height: int = 150,
    ):
        super().__init__(master, height=height, fg_color=CARD,
                         corner_radius=12, border_width=2, border_color=BORDER_STRONG)
        self.on_image_loaded = on_image_loaded
        self.current_filepath: Optional[str] = None
        self.grid_propagate(False)

        # 用 pack 垂直居中所有内容
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        # 图标方块（accent 柔和底色）
        icon_frame = ctk.CTkFrame(inner, fg_color=ACCENT_SOFT,
                                   width=46, height=46, corner_radius=12)
        icon_frame.pack(pady=(0, 8))
        icon_frame.pack_propagate(False)
        ctk.CTkLabel(icon_frame, text="🖼️", font=ctk.CTkFont(size=20)).pack(expand=True)

        # 主提示
        self.label = ctk.CTkLabel(
            inner,
            text="点击选择图片",
            font=ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold"),
            text_color="#4a443c",
        )
        self.label.pack()

        # 副提示
        hint = ctk.CTkLabel(
            inner,
            text="拍照或从相册选取 · 图片仅在本地处理",
            font=ctk.CTkFont(family="Microsoft YaHei", size=11),
            text_color=SUB,
        )
        hint.pack(pady=(2, 0))

        # 整个区域可点击
        for w in (self, inner, icon_frame, self.label, hint):
            w.bind("<Button-1>", lambda e: self._browse_file())

    def _browse_file(self):
        filepath = ctk.filedialog.askopenfilename(
            title="选择图片",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tiff"),
                ("所有文件", "*.*"),
            ],
        )
        if filepath and os.path.isfile(filepath):
            self._load_file(filepath)

    def _load_file(self, filepath: str):
        try:
            img = Image.open(filepath)
            w, h = img.size
            fname = os.path.basename(filepath)
            self.label.configure(text=f"{fname}  ({w} × {h})")
            self.current_filepath = filepath
            self.on_image_loaded(filepath)
        except Exception as e:
            self.label.configure(text=f"加载失败: {e}")
