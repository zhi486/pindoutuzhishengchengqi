"""主窗口 —— 顶层布局管理。

使用 customtkinter 构建三栏布局：
  左侧: 图片上传区 + 预览画布
  中间: 参数控制面板
  右侧: 颜色图例
  底部: 状态栏
"""

import customtkinter as ctk
from pathlib import Path
from typing import Optional

from PIL import Image

from app.app_controller import AppController


class MainWindow(ctk.CTk):
    """拼豆图纸生成器主窗口。"""

    WINDOW_TITLE = "拼豆图纸生成器 - Pixel Bead Studio"
    DEFAULT_WIDTH = 1400
    DEFAULT_HEIGHT = 850
    MIN_WIDTH = 1000
    MIN_HEIGHT = 650

    def __init__(self):
        super().__init__()

        # 窗口设置
        self.title(self.WINDOW_TITLE)
        self.geometry(f"{self.DEFAULT_WIDTH}x{self.DEFAULT_HEIGHT}")
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)

        # 主题
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # 控制器 + 缩放状态
        self.controller = AppController()
        self._tile_size = 20  # 当前预览缩放

        # 延迟导入 UI 组件
        from app.ui.image_drop_zone import ImageDropZone
        from app.ui.preview_canvas import PreviewCanvas
        from app.ui.control_panel import ControlPanel
        from app.ui.color_legend import ColorLegendPanel
        from app.ui.status_bar import StatusBar

        # --- 布局网格 ---
        # 左侧: 图片区 + 预览 (权重 2)
        # 中间: 控制面板 (权重 1)
        # 右侧: 颜色图例 (权重 1)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)  # 状态栏

        # --- 左侧面板 ---
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(0, weight=0)  # 上传区
        self.left_frame.grid_rowconfigure(1, weight=1)  # 预览区

        # 图片上传区
        self.drop_zone = ImageDropZone(
            self.left_frame,
            on_image_loaded=self._on_image_loaded,
            height=150,
        )
        self.drop_zone.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 2))

        # 预览画布
        self.preview_canvas = PreviewCanvas(self.left_frame)
        self.preview_canvas.grid(row=1, column=0, sticky="nsew", padx=5, pady=(2, 5))

        # --- 中间面板 ---
        self.control_panel = ControlPanel(
            self,
            on_param_changed=self._on_param_changed,
            on_zoom_changed=self._on_zoom_changed,
            on_export_png=self._on_export_png,
            on_export_pdf=self._on_export_pdf,
            on_material_changed=self._on_material_changed,
        )
        self.control_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # --- 右侧面板 ---
        self.color_legend = ColorLegendPanel(self)
        self.color_legend.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        # --- 状态栏 ---
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=(0, 5))

    # ── 回调 ──────────────────────────────────────

    def _on_image_loaded(self, filepath: str):
        """图片加载回调。"""
        try:
            self.controller.load_image(filepath)
            self.status_bar.show(f"已加载: {Path(filepath).name}")
            self._regenerate()
        except Exception as e:
            self.status_bar.show(f"加载失败: {e}")

    # 仅影响显示、不需要重新计算管道的参数
    _DISPLAY_ONLY_PARAMS = {"show_grid", "show_board_lines", "show_color_codes"}

    def _on_param_changed(self, key: str, value):
        """参数变更回调。显示类参数仅重渲染，不重新计算。"""
        self.controller.set_param(key, value)
        if key in self._DISPLAY_ONLY_PARAMS:
            self._rerender()
        else:
            self._regenerate()

    def _on_material_changed(self, material: str):
        """豆子材质切换回调 —— 重新处理并更新提示。"""
        self.controller.material_mode = material
        self._update_material_note()
        self.status_bar.show(f"已切换材质: {material} · {self.controller.palette.n_colors} 色")
        self._regenerate()

    def _update_material_note(self):
        """显示半透明材质提示。"""
        note = self.controller.get_material_note()
        self.control_panel.show_material_note(note)

    def _on_zoom_changed(self, tile_size: int):
        """缩放变更回调 —— 仅重渲染预览，不重新计算管道。"""
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
        """重新计算图案并刷新预览和图例。"""
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
            # 显示自动计算的宽度
            self.control_panel.set_bead_w_display(params["max_beads_w"])
        except Exception as e:
            self.status_bar.show(f"处理错误: {e}")
            import traceback
            traceback.print_exc()

    def _rerender(self):
        """仅刷新预览渲染，不重新计算管道（用于显示选项变更）。"""
        if not self.controller.current_pattern:
            return
        pattern = self.controller.current_pattern
        params = self.controller.get_params()
        self.preview_canvas.show_pattern(
            pattern, params,
            palette=self.controller.palette,
            tile_size=self._tile_size,
        )
        # 图例数据未变，不需要刷新

    def _build_status_text(self, pattern) -> str:
        """构建状态栏文本。"""
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
        """PNG 导出回调。"""
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
        """PDF 导出回调。"""
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
