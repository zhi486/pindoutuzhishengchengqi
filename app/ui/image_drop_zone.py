"""图片拖放/选择区域。

支持点击按钮选择图片，显示文件名和原始尺寸。
"""

import os
import customtkinter as ctk
from PIL import Image
from typing import Callable, Optional


class ImageDropZone(ctk.CTkFrame):
    """图片加载区域 —— 点击选择图片。"""

    def __init__(
        self,
        master,
        on_image_loaded: Callable[[str], None],
        height: int = 150,
    ):
        super().__init__(master, height=height)
        self.on_image_loaded = on_image_loaded
        self.current_filepath: Optional[str] = None

        # 内部布局
        self.grid_propagate(False)

        # 提示标签
        self.label = ctk.CTkLabel(
            self,
            text="拖放图片到此处\n或点击下方按钮选择",
            font=ctk.CTkFont(size=13),
            text_color="gray60",
        )
        self.label.place(relx=0.5, rely=0.35, anchor="center")

        # 选择按钮
        self.browse_btn = ctk.CTkButton(
            self,
            text="选择图片",
            command=self._browse_file,
            width=120,
            height=32,
        )
        self.browse_btn.place(relx=0.5, rely=0.65, anchor="center")

        # 文件信息标签
        self.info_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray50",
        )
        self.info_label.place(relx=0.5, rely=0.85, anchor="center")

    def _browse_file(self):
        """打开文件选择对话框。"""
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
        """加载并验证图片文件。"""
        try:
            img = Image.open(filepath)
            w, h = img.size
            fname = os.path.basename(filepath)
            self.info_label.configure(text=f"{fname}  ({w} × {h})")
            self.current_filepath = filepath
            self.on_image_loaded(filepath)
        except Exception as e:
            self.info_label.configure(text=f"加载失败: {e}")
