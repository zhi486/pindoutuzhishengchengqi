"""PDF 图纸导出器。

生成可打印的多页 PDF 图纸，包含:
- 按底板分页的像素网格
- 底板编号和对齐标记
- 颜色图例页
- 购物清单（每种颜色数量）
"""

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib import colors as rl_colors
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── 注册中文字体 ──────────────────────────────────
_CN_FONT_NAME = "Helvetica"  # fallback
_CN_FONT_BOLD = "Helvetica-Bold"
for _font_path, _font_name, _bold_name in [
    ("C:/Windows/Fonts/simhei.ttf", "SimHei", "SimHei"),
    ("C:/Windows/Fonts/msyh.ttc", "MSYH", "MSYH"),
    ("C:/Windows/Fonts/simsun.ttc", "SimSun", "SimSun"),
]:
    try:
        pdfmetrics.registerFont(TTFont(_font_name, _font_path))
        _CN_FONT_NAME = _font_name
        _CN_FONT_BOLD = _bold_name
        break
    except Exception:
        continue


# A4 尺寸
PAGE_W, PAGE_H = A4  # 594.96 x 840.99 points (210 x 297 mm)
MARGIN = 15 * mm


def _hex_to_rl_color(hex_str: str):
    """将 #RRGGBB 转换为 reportlab Color。"""
    r = int(hex_str[1:3], 16) / 255.0
    g = int(hex_str[3:5], 16) / 255.0
    b = int(hex_str[5:7], 16) / 255.0
    return rl_colors.Color(r, g, b)


def export_pdf(
    pattern,
    palette,
    filepath: str,
    params: dict,
):
    """导出可打印的 PDF 图纸，自动缩放保证每块底板完整显示在一页内。

    Args:
        pattern: Pattern 对象
        palette: BeadPalette 色卡对象
        filepath: 保存路径
        params: 参数字典
    """
    if pattern.grid is None:
        raise ValueError("无图案数据")

    c = rl_canvas.Canvas(filepath, pagesize=A4)

    bead_w, bead_h = pattern.bead_size
    bw = params.get("board_width", 52)
    bh = params.get("board_height", 52)

    # 可用页面空间
    usable_w = PAGE_W - 2 * MARGIN
    usable_h = PAGE_H - 2 * MARGIN - 20 * mm  # 标题 + 行号标注

    # 自动计算 cell_mm，保证整块底板适于一页
    cell_pt = min(usable_w / bw, usable_h / bh)
    cell_mm_val = cell_pt / mm

    # 按底板分页
    import math
    board_cols = math.ceil(bead_w / bw)
    board_rows = math.ceil(bead_h / bh)

    for br in range(board_rows):
        for bc in range(board_cols):
            # 计算该底板的豆子范围
            r_start = br * bh
            r_end = min((br + 1) * bh, bead_h)
            c_start = bc * bw
            c_end = min((bc + 1) * bw, bead_w)

            board_bead_h = r_end - r_start
            board_bead_w = c_end - c_start

            # 提取该底板的数据
            sub_grid = pattern.grid[r_start:r_end, c_start:c_end]
            sub_indices = pattern.indices[r_start:r_end, c_start:c_end]

            # 绘制页面
            _draw_board_page(
                c,
                sub_grid,
                sub_indices,
                palette,
                cell_pt,
                MARGIN,
                PAGE_H - MARGIN - 12 * mm,  # 起始 Y
                board_num=br * board_cols + bc + 1,
                total_boards=board_rows * board_cols,
                bead_w=board_bead_w,
                bead_h=board_bead_h,
                show_color_codes=params.get("show_color_codes", False),
            )

            c.showPage()

    # 图例页
    _draw_legend_page(c, pattern, palette)
    c.showPage()

    c.save()


def _draw_board_page(c, grid, indices, palette, cell_pt, margin_x, start_y,
                     board_num, total_boards, bead_w, bead_h,
                     show_color_codes=False):
    """绘制单块底板的图案，含行列号标注。"""
    c.setFont(_CN_FONT_NAME, 8)

    # 计算标注边距
    label_margin = 14
    grid_start_x = margin_x + label_margin
    grid_start_y = start_y - bead_h * cell_pt

    # 标题
    c.setFillColor(rl_colors.black)
    c.drawString(
        grid_start_x, start_y + 6,
        f"底板 {board_num}/{total_boards}  {bead_w}×{bead_h}"
    )

    # 批量绘制：按颜色分组
    color_groups = {}
    for r in range(bead_h):
        for c_idx in range(bead_w):
            color_idx = int(indices[r, c_idx])
            if color_idx not in color_groups:
                color_groups[color_idx] = []
            color_groups[color_idx].append((c_idx, r))

    for color_idx, cells in color_groups.items():
        hex_color = palette.get_hex_color(color_idx)
        rl_c = _hex_to_rl_color(hex_color)
        c.setFillColor(rl_c)
        c.setStrokeColor(rl_colors.Color(0.8, 0.8, 0.8))
        c.setLineWidth(0.3)

        for cx, ry in cells:
            x = grid_start_x + cx * cell_pt
            y = grid_start_y + (bead_h - 1 - ry) * cell_pt
            c.rect(x, y, cell_pt, cell_pt, fill=1, stroke=1)

    # 底板边界
    c.setStrokeColor(rl_colors.black)
    c.setLineWidth(1.5)
    c.rect(
        grid_start_x, grid_start_y,
        bead_w * cell_pt, bead_h * cell_pt,
        fill=0, stroke=1,
    )

    # 色号标注
    if show_color_codes and cell_pt >= 8:
        font_size = max(4, cell_pt * 0.42)
        c.setFont(_CN_FONT_NAME, font_size)

        for r in range(bead_h):
            for col in range(bead_w):
                color_idx = int(indices[r, col])
                code = palette.codes[color_idx]
                hex_color = palette.get_hex_color(color_idx)

                # 计算背景亮度，选黑/白文字
                r_val = int(hex_color[1:3], 16)
                g_val = int(hex_color[3:5], 16)
                b_val = int(hex_color[5:7], 16)
                luminance = 0.299 * r_val + 0.587 * g_val + 0.114 * b_val

                if luminance > 128:
                    c.setFillColor(rl_colors.Color(0.15, 0.15, 0.15))
                else:
                    c.setFillColor(rl_colors.Color(0.9, 0.9, 0.9))

                # 居中文字
                x = grid_start_x + col * cell_pt + cell_pt * 0.15
                y = grid_start_y + (bead_h - 1 - r) * cell_pt + cell_pt * 0.3
                c.drawString(x, y, code)

    # 行号（左侧）/ 列号（上方），每5格标注
    interval = 1 if max(bead_w, bead_h) <= 30 else 5
    c.setFillColor(rl_colors.Color(0.35, 0.35, 0.35))
    c.setFont(_CN_FONT_NAME, 5)

    for r in range(0, bead_h, interval):
        y = grid_start_y + (bead_h - 1 - r) * cell_pt + cell_pt / 2 + 1
        c.drawString(margin_x + 2, y, str(r + 1))

    for c_idx in range(0, bead_w, interval):
        x = grid_start_x + c_idx * cell_pt + cell_pt / 2 - 2
        c.drawString(x, grid_start_y - 8, str(c_idx + 1))


def _draw_legend_page(c, pattern, palette):
    """绘制图例汇总页。"""
    margin = MARGIN
    y = PAGE_H - MARGIN

    c.setFont(_CN_FONT_BOLD, 14)
    c.setFillColor(rl_colors.black)
    c.drawString(margin, y, "颜色图例与购物清单")
    y -= 25

    c.setFont(_CN_FONT_NAME, 10)
    c.drawString(margin, y, f"总豆子数: {pattern.total_beads}    "
                 f"颜色数: {pattern.unique_colors}")
    y -= 20

    c.setFont(_CN_FONT_NAME, 9)
    for color_info in pattern.color_summary:
        if y < 40:  # 换页
            c.showPage()
            y = PAGE_H - MARGIN

        hex_color = color_info.get("hex", "#000000")
        code = color_info.get("code", "")
        count = color_info.get("count", 0)

        rl_c = _hex_to_rl_color(hex_color)
        c.setFillColor(rl_c)
        c.setStrokeColor(rl_colors.Color(0.7, 0.7, 0.7))
        c.rect(margin, y - 10, 14, 14, fill=1, stroke=1)

        c.setFillColor(rl_colors.black)
        c.drawString(margin + 22, y - 4, f"{code}    {count} 颗")

        y -= 18
