"""拼豆图纸生成器 —— 主入口。

将普通图片转换为拼豆 (MARD 融合豆) 像素图纸。
支持实时预览、颜色匹配、PNG/PDF 导出。
"""

import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import customtkinter as ctk
from app.ui.main_window import MainWindow


def main():
    """启动应用。"""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
