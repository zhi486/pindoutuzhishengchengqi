"""PNG 图纸导出器。

生成高清晰像素图纸，包含:
- 像素网格（带色号标注）
- 网格线/底板边界
- 右侧颜色图例
"""

from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from app.core.pixelizer import (upsample_for_preview, draw_grid_lines,
                                draw_board_lines, add_coordinate_labels)


# 图例区域的像素宽度
LEGEND_WIDTH = 280
LEGEND_PADDING = 40
TITLE_HEIGHT = 50


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    """获取字体，优先使用系统中文字体。"""
    font_candidates = [
        "C:/Windows/Fonts/msyh.ttc",       # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",     # 黑体
        "C:/Windows/Fonts/simsun.ttc",     # 宋体
        "C:/Windows/Fonts/arial.ttf",      # Arial fallback
    ]
    for font_path in font_candidates:
        try:
            return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _draw_legend(
    draw: ImageDraw.ImageDraw,
    color_summary: list[dict],
    start_x: int,
    start_y: int,
    font: ImageFont.FreeTypeFont,
    small_font: ImageFont.FreeTypeFont,
):
    """在图例区域绘制颜色列表。"""
    x = start_x
    y = start_y

    # 标题
    draw.text((x, y), "颜色图例", fill=(0, 0, 0), font=font)
    y += 35

    total = sum(c["count"] for c in color_summary)

    for color in color_summary:
        if y > start_y + 1100:  # 防止图例超出
            break

        hex_color = color.get("hex", "#000000")
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)

        # 色块
        draw.rectangle([x, y, x + 24, y + 16], fill=(r, g, b), outline=(180, 180, 180))

        # 色号 + 数量
        code = color.get("code", "")
        text = f"{code}  ×{color['count']}"
        draw.text((x + 30, y - 1), text, fill=(60, 60, 60), font=small_font)

        y += 20

    # 总计
    y += 5
    draw.text((x, y), f"共 {len(color_summary)} 色  {total} 颗", fill=(0, 0, 0), font=font)


def export_png(
    pattern,
    palette,
    filepath: str,
    params: dict,
    tile_size: int = 30,
):
    """导出高清 PNG 图纸。

    Args:
        pattern: Pattern 对象
        palette: BeadPalette 色卡对象
        filepath: 保存路径
        params: 参数字典
        tile_size: 每个豆子的像素大小（导出用更大值，默认30）
    """
    if pattern.grid is None:
        raise ValueError("无图案数据")

    font = _get_font(18)
    small_font = _get_font(13)

    grid_w = pattern.bead_size[0] * tile_size
    grid_h = pattern.bead_size[1] * tile_size

    # Canvas 尺寸: 网格 + 间距 + 图例
    canvas_w = grid_w + LEGEND_PADDING + LEGEND_WIDTH + 40
    canvas_h = max(grid_h, 800) + TITLE_HEIGHT + 20

    # 创建画布
    canvas = Image.new("RGB", (canvas_w, canvas_h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # 标题
    draw.text(
        (20, 15),
        f"拼豆图纸  {pattern.bead_size[0]}×{pattern.bead_size[1]}   "
        f"像素大小:{pattern.pixel_size}  颜色:{pattern.unique_colors}种",
        fill=(0, 0, 0),
        font=font,
    )

    # 渲染像素网格
    grid_img = upsample_for_preview(pattern.grid, tile_size)

    # 网格线
    if params.get("show_grid", True):
        grid_img = draw_grid_lines(grid_img, tile_size, (210, 210, 210))

    # 底板边界
    if params.get("show_board_lines", True):
        bw = params.get("board_width", 29)
        bh = params.get("board_height", 29)
        grid_img = draw_board_lines(grid_img, tile_size, bw, bh, (50, 50, 50))

    # 行列号标注
    bead_w, bead_h = pattern.bead_size
    grid_img = add_coordinate_labels(grid_img, tile_size, bead_w, bead_h)

    # 贴到画布上
    grid_y = TITLE_HEIGHT
    canvas.paste(grid_img, (20, grid_y))

    # 图例
    legend_x = 20 + grid_w + LEGEND_PADDING
    _draw_legend(draw, pattern.color_summary, legend_x, grid_y, font, small_font)

    # 底板信息
    if pattern.board_layout:
        bl = pattern.board_layout
        draw.text(
            (20, grid_y + grid_h + 10),
            f"底板: {bl.total} 块 ({bl.cols}×{bl.rows})  "
            f"每块 {bl.board_w}×{bl.board_h}",
            fill=(100, 100, 100),
            font=small_font,
        )

    # 保存
    canvas.save(filepath, "PNG", dpi=(300, 300))
