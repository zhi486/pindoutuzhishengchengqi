"""主窗口 —— 暖纸底 · 陶土橙 · 网页版对齐。

使用 customtkinter 构建两栏布局：
  顶部: 深色 Header（标题 + 彩虹装饰条）
  左侧: 图片上传区 + 预览画布
  右侧: 参数控制面板 + 颜色图例（上下排列）
  底部: 状态栏
"""

import customtkinter as ctk
from pathlib import Path
from typing import Optional

from PIL import Image

from app.app_controller import AppController


# ═══════════════ 设计令牌 ═══════════════

ACCENT       = "#e05a2b"
ACCENT_HOVER = "#c94e24"
ACCENT_SOFT  = "#fbe9df"
BG           = "#f3f0ea"
CARD         = "#fffdf8"
TEXT         = "#211d19"
SUB          = "#8a8378"
BORDER       = "#e7e1d4"
BORDER_STRONG = "#d6cfbf"
HEADER_BG    = "#231f1a"
RADIUS       = 12  # 统一圆角


class MainWindow(ctk.CTk):
    """拼豆图纸生成器主窗口。"""

    WINDOW_TITLE = "拼豆图纸生成器 - Pixel Bead Studio"
    DEFAULT_WIDTH = 1400
    DEFAULT_HEIGHT = 850
    MIN_WIDTH = 1000
    MIN_HEIGHT = 650

    def __init__(self):
        super().__init__()

        self.title(self.WINDOW_TITLE)
        self.geometry(f"{self.DEFAULT_WIDTH}x{self.DEFAULT_HEIGHT}")
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=BG)

        self.controller = AppController()
        self._tile_size = 20

        # 延迟导入 UI 组件
        from app.ui.image_drop_zone import ImageDropZone
        from app.ui.preview_canvas import PreviewCanvas
        from app.ui.control_panel import ControlPanel
        from app.ui.color_legend import ColorLegendPanel
        from app.ui.status_bar import StatusBar

        # --- 布局网格 ---
        self.grid_columnconfigure(0, weight=2)   # 左侧: 图片+预览
        self.grid_columnconfigure(1, weight=1)   # 右侧: 控制+图例
        self.grid_rowconfigure(0, weight=0)      # Header
        self.grid_rowconfigure(1, weight=1)      # 主区域
        self.grid_rowconfigure(2, weight=0)      # 状态栏

        # ═══ Header ═══
        self._build_header()

        # ═══ 主区域 ═══
        main_area = ctk.CTkFrame(self, fg_color="transparent")
        main_area.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 5))
        main_area.grid_columnconfigure(0, weight=2)
        main_area.grid_columnconfigure(1, weight=1)
        main_area.grid_rowconfigure(0, weight=1)

        # --- 左侧面板 ---
        left_frame = ctk.CTkFrame(main_area, fg_color=CARD, corner_radius=RADIUS,
                                   border_width=1, border_color=BORDER)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=0)   # 上传区
        left_frame.grid_rowconfigure(1, weight=1)   # 预览区

        self.drop_zone = ImageDropZone(
            left_frame,
            on_image_loaded=self._on_image_loaded,
            height=140,
        )
        self.drop_zone.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))

        self.preview_canvas = PreviewCanvas(left_frame)
        self.preview_canvas.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 8))

        # --- 右侧面板（控制 + 图例 上下排列） ---
        right_frame = ctk.CTkFrame(main_area, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=0)   # 控制面板
        right_frame.grid_rowconfigure(1, weight=1)   # 颜色图例

        self.control_panel = ControlPanel(
            right_frame,
            on_param_changed=self._on_param_changed,
            on_zoom_changed=self._on_zoom_changed,
            on_export_png=self._on_export_png,
            on_export_pdf=self._on_export_pdf,
            on_material_changed=self._on_material_changed,
        )
        self.control_panel.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        self.color_legend = ColorLegendPanel(right_frame)
        self.color_legend.grid(row=1, column=0, sticky="nsew")

        # ═══ 状态栏 ═══
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 6))

    # ── Header ────────────────────────────────────

    def _build_header(self):
        """构建深色顶栏 + 彩虹装饰条。"""
        header = ctk.CTkFrame(self, fg_color=HEADER_BG, corner_radius=0, height=52)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_propagate(False)

        # 标题
        title_label = ctk.CTkLabel(
            header,
            text="拼豆图纸生成器",
            font=ctk.CTkFont(family="Microsoft YaHei", size=18, weight="bold"),
            text_color="#f7f3ec",
        )
        title_label.pack(side="left", padx=18, pady=10)

        # 副标题
        sub_label = ctk.CTkLabel(
            header,
            text="图片转拼豆图纸 · 自动匹配色号清单",
            font=ctk.CTkFont(family="Microsoft YaHei", size=11),
            text_color="#a2988a",
        )
        sub_label.pack(side="left", padx=(0, 0), pady=16)

        # 版本标签（右侧）
        ver_tag = ctk.CTkLabel(
            header,
            text="桌面版",
            font=ctk.CTkFont(family="Microsoft YaHei", size=10),
            text_color="#cfc6b8",
        )
        ver_tag.pack(side="right", padx=18, pady=14)

        # 彩虹装饰条
        rainbow = ctk.CTkFrame(self, fg_color="transparent", height=3, corner_radius=0)
        rainbow.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(52, 0))
        rainbow.grid_propagate(False)
        # 用多个彩色 Label 拼出彩虹条
        colors = ["#f94144", "#f8961e", "#f9c74f", "#90be6d",
                   "#43aa8b", "#577590", "#9b5de5", "#f15bb5"]
        for c in colors:
            seg = ctk.CTkFrame(rainbow, fg_color=c, corner_radius=0)
            seg.pack(side="left", fill="both", expand=True)

    # ── 回调 ──────────────────────────────────────

    def _on_image_loaded(self, filepath: str):
        try:
            self.controller.load_image(filepath)
            self.status_bar.show(f"已加载: {Path(filepath).name}")
            self._regenerate()
        except Exception as e:
            self.status_bar.show(f"加载失败: {e}")

    _DISPLAY_ONLY_PARAMS = {"show_grid", "show_board_lines", "show_color_codes"}

    def _on_param_changed(self, key: str, value):
        self.controller.set_param(key, value)
        if key in self._DISPLAY_ONLY_PARAMS:
            self._rerender()
        else:
            self._regenerate()

    def _on_material_changed(self, material: str):
        self.controller.material_mode = material
        self._update_material_note()
        self.status_bar.show(f"已切换材质: {material} · {self.controller.palette.n_colors} 色")
        self._regenerate()

    def _update_material_note(self):
        note = self.controller.get_material_note()
        self.control_panel.show_material_note(note)

    def _on_zoom_changed(self, tile_size: int):
        self._tile_size = tile_size
        if not self.controller.current_pattern:
            return
        self.preview_canvas.show_pattern(
            self.controller.current_pattern,
            self.controller.get_params(),
            palette=self.controller.palette,
            tile_size=tile_size,
        )

    def _regenerate(self):
        if not self.controller.has_image():
            return
        try:
            pattern = self.controller.process()
            params = self.controller.get_params()
            self.preview_canvas.show_pattern(
                pattern, params,
                palette=self.controller.palette,
                tile_size=self._tile_size,
            )
            self.color_legend.show_legend(pattern.color_summary)
            self.status_bar.show(self._build_status_text(pattern))
            self.control_panel.set_bead_w_display(params["max_beads_w"])
        except Exception as e:
            self.status_bar.show(f"处理错误: {e}")
            import traceback
            traceback.print_exc()

    def _rerender(self):
        if not self.controller.current_pattern:
            return
        pattern = self.controller.current_pattern
        params = self.controller.get_params()
        self.preview_canvas.show_pattern(
            pattern, params,
            palette=self.controller.palette,
            tile_size=self._tile_size,
        )

    def _build_status_text(self, pattern) -> str:
        w, h = pattern.bead_size
        parts = [f"{w} × {h} 豆子"]
        parts.append(f"MARD · {self.controller.material_mode}")
        parts.append(f"{pattern.unique_colors} 种颜色")
        parts.append(f"共 {pattern.total_beads} 颗")
        if pattern.board_layout:
            bl = pattern.board_layout
            parts.append(f"{bl.total} 块底板 ({bl.cols}×{bl.rows})")
        return " | ".join(parts)

    def _on_export_png(self):
        if not self.controller.current_pattern:
            self.status_bar.show("请先加载图片")
            return
        filepath = ctk.filedialog.asksaveasfilename(
            title="导出 PNG 图纸",
            defaultextension=".png",
            filetypes=[("PNG 图片", "*.png")],
        )
        if filepath:
            try:
                from app.export.png_exporter import export_png
                export_png(
                    self.controller.current_pattern,
                    self.controller.palette,
                    filepath,
                    self.controller.get_params(),
                )
                self.status_bar.show(f"PNG 已导出: {Path(filepath).name}")
            except Exception as e:
                self.status_bar.show(f"PNG 导出失败: {e}")

    def _on_export_pdf(self):
        if not self.controller.current_pattern:
            self.status_bar.show("请先加载图片")
            return
        filepath = ctk.filedialog.asksaveasfilename(
            title="导出 PDF 图纸",
            defaultextension=".pdf",
            filetypes=[("PDF 文件", "*.pdf")],
        )
        if filepath:
            try:
                from app.export.pdf_exporter import export_pdf
                export_pdf(
                    self.controller.current_pattern,
                    self.controller.palette,
                    filepath,
                    self.controller.get_params(),
                )
                self.status_bar.show(f"PDF 已导出: {Path(filepath).name}")
            except Exception as e:
                self.status_bar.show(f"PDF 导出失败: {e}")
