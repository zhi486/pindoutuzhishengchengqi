"""图片像素化引擎。

将普通图片通过降采样和最近邻上采样转换为像素风格。
核心流程：加载图片 → Box降采样 → 颜色量化(可选) → 色卡匹配 → 上采样预览。
"""

from typing import Optional, Tuple

import numpy as np
from PIL import Image


def load_image(filepath: str) -> Image.Image:
    """加载图片并转为 RGB 模式。"""
    img = Image.open(filepath)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def resize_to_beads(img: Image.Image, target_w: int, target_h: int) -> np.ndarray:
    """直接将图片缩放到目标豆子尺寸。

    使用 Lanczos 重采样，既保留了区域平均的效果，
    又能精确控制输出尺寸，不会像 pixel_size 间接计算那样产生误差。

    Args:
        img: PIL Image (RGB 模式)
        target_w: 目标宽度（豆子列数）
        target_h: 目标高度（豆子行数）

    Returns:
        (target_h, target_w, 3) numpy uint8 数组
    """
    if target_w < 1 or target_h < 1:
        raise ValueError(f"目标尺寸 {target_w}×{target_h} 无效，至少需要 1×1")
    small = img.resize((target_w, target_h), Image.LANCZOS)
    return np.array(small, dtype=np.uint8)


# 保留旧接口兼容性
def downsample(img: Image.Image, pixel_size: int) -> np.ndarray:
    """对图片进行 Box 降采样，返回各 block 的 RGB 均值。

    原理：将原图按 pixel_size × pixel_size 分块，每块取所有像素的
    RGB 平均值作为该位置"豆子"的颜色候选。这个方法的效果相当于
    相机的低通滤波——在减小分辨率的同时保留了每个区域的主要色调。

    Args:
        img: PIL Image (RGB 模式)
        pixel_size: 每个"豆子"覆盖的原始像素块边长。
                    pixel_size=4 意味着 4×4=16 个像素合并为 1 个豆子。

    Returns:
        (H, W, 3) numpy uint8 数组，是降采样后的平均颜色网格。
    """
    w, h = img.size
    new_w = w // pixel_size
    new_h = h // pixel_size

    if new_w < 1 or new_h < 1:
        raise ValueError(
            f"像素大小 {pixel_size} 过大，图片尺寸 {w}×{h} 至少需要 "
            f"产生 1×1 的网格 (当前计算结果: {new_w}×{new_h})"
        )

    # 裁剪到整数倍
    crop_w = new_w * pixel_size
    crop_h = new_h * pixel_size
    img_cropped = img.crop((0, 0, crop_w, crop_h))

    # 转为 numpy 并重排维度
    arr = np.array(img_cropped, dtype=np.float64)  # (H, W, 3)

    # 重排为 (new_H, pixel_size, new_W, pixel_size, 3)
    reshaped = arr.reshape(new_h, pixel_size, new_w, pixel_size, 3)

    # 对每个 block 求 RGB 均值 → (new_H, new_W, 3)
    averaged = reshaped.mean(axis=(1, 3)).round().astype(np.uint8)

    return averaged


def compute_pixel_size(
    img_width: int, img_height: int, max_beads_w: int, max_beads_h: int
) -> int:
    """根据豆子宽度和长度约束自动计算像素块大小。

    保持豆子为正方形，向上取整确保实际豆子数不超过设定值。
    例如: 800px图, 设58列 → pixel_size=14 → 输出57列 (≤58 ✓)

    Args:
        img_width, img_height: 原始图片尺寸
        max_beads_w: 目标豆子列数（实际 ≤ 此值）
        max_beads_h: 目标豆子行数（实际 ≤ 此值）

    Returns:
        计算出的 pixel_size (至少为 1)
    """
    # 四舍五入使输出最接近目标值
    ps_w = max(1, round(img_width / max_beads_w))
    ps_h = max(1, round(img_height / max_beads_h))
    pixel_size = max(ps_w, ps_h)
    return pixel_size


def upsample_for_preview(
    grid: np.ndarray, tile_size: int = 20
) -> Image.Image:
    """将像素网格最近邻上采样，生成带像素块效果的预览图。

    使用 PIL 的 NEAREST 滤镜做上采样——这保证了每个"豆子"
    在预览中是一个清晰的方块，不会因为双线性插值而模糊。

    Args:
        grid: (H, W, 3) numpy uint8 颜色网格
        tile_size: 每个豆子在预览图中的像素边长

    Returns:
        PIL Image，尺寸为 (W * tile_size, H * tile_size)
    """
    h, w = grid.shape[:2]
    # 先转为小图再 NEAREST 放大 —— 这保证了完美的像素块效果
    small_img = Image.fromarray(grid, mode="RGB")
    preview = small_img.resize(
        (w * tile_size, h * tile_size),
        resample=Image.NEAREST,
    )
    return preview


def draw_grid_lines(
    img: Image.Image, tile_size: int,
    grid_color=(200, 200, 200), emphasis_color=(60, 60, 60),
) -> Image.Image:
    """在预览图上绘制网格线，每5格画一条加粗强调线。

    横线竖线在交叉点处恢复原始色块颜色，形成"断点"效果——
    两条线互相切断，交叉处露出豆子的颜色，视觉上更干净。

    Args:
        img: 已上采样的预览图
        tile_size: 每个 tile 的像素大小
        grid_color: 普通网格线颜色
        emphasis_color: 每5格强调线颜色

    Returns:
        带网格线的新 PIL Image
    """
    w, h = img.size
    grid_img = img.copy()
    original = img.copy()  # 保存原图，用于恢复交叉点
    orig_pixels = original.load()
    pixels = grid_img.load()

    # 水平线
    for y in range(0, h, tile_size):
        bead_row = y // tile_size
        color = emphasis_color if bead_row % 5 == 0 else grid_color
        line_w = 2 if bead_row % 5 == 0 else 1
        for dy in range(line_w):
            yy = y + dy
            if yy < h:
                for x in range(w):
                    pixels[x, yy] = color

    # 竖直线
    for x in range(0, w, tile_size):
        bead_col = x // tile_size
        color = emphasis_color if bead_col % 5 == 0 else grid_color
        line_w = 2 if bead_col % 5 == 0 else 1
        for dx in range(line_w):
            xx = x + dx
            if xx < w:
                for y in range(h):
                    pixels[xx, y] = color

    # 交叉点恢复原色 —— 让横线竖线互相"切断"
    for y in range(0, h, tile_size):
        bead_row = y // tile_size
        h_emph = (bead_row % 5 == 0)
        h_line_w = 2 if h_emph else 1
        for x in range(0, w, tile_size):
            bead_col = x // tile_size
            v_emph = (bead_col % 5 == 0)
            v_line_w = 2 if v_emph else 1
            # 交叉区域用最粗的线宽来恢复
            gap_w = max(h_line_w, v_line_w)
            for dy in range(gap_w):
                yy = y + dy
                if yy >= h:
                    continue
                for dx in range(gap_w):
                    xx = x + dx
                    if xx >= w:
                        continue
                    pixels[xx, yy] = orig_pixels[xx, yy]

    return grid_img


def draw_board_lines(
    img: Image.Image,
    tile_size: int,
    board_width: int = 29,
    board_height: int = 29,
    board_color=(170, 170, 170),
) -> Image.Image:
    """在预览图上用细线标记拼豆底板边界。

    Args:
        img: 带基本网格的预览图
        tile_size: 每个 tile 的像素大小
        board_width, board_height: 底板尺寸（默认 29×29）
        board_color: 底板边界线颜色（浅色，不抢夺主视觉）

    Returns:
        带底板边界线的新 PIL Image
    """
    w, h = img.size
    board_img = img.copy()
    pixels = board_img.load()

    line_width = 1

    # 水平底板边界
    for y in range(board_height * tile_size, h, board_height * tile_size):
        for dy in range(line_width):
            yy = y + dy
            if yy < h:
                for x in range(w):
                    pixels[x, yy] = board_color

    # 竖直底板边界
    for x in range(board_width * tile_size, w, board_width * tile_size):
        for dx in range(line_width):
            xx = x + dx
            if xx < w:
                for y in range(h):
                    pixels[xx, y] = board_color

    return board_img


def add_coordinate_labels(
    img: Image.Image,
    tile_size: int,
    grid_width: int,
    grid_height: int,
) -> Image.Image:
    """在像素图外围添加行列号标注。

    列号标在上方，行号标在左侧，每隔5标注一次（小图则每个都标）。
    使用 PIL 内置字体绘制数字，帮助快速定位指定豆子的坐标。

    Args:
        img: 已渲染的预览图
        tile_size: 每个 tile 的像素大小
        grid_width: 豆子列数
        grid_height: 豆子行数

    Returns:
        带坐标标注的新 PIL Image
    """
    from PIL import ImageDraw, ImageFont

    # 加载字体
    font = None
    for fp in ["C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/arial.ttf"]:
        try:
            font = ImageFont.truetype(fp, size=max(9, tile_size - 4))
            break
        except (OSError, IOError):
            continue
    if font is None:
        font = ImageFont.load_default()

    # 标注间隔：小于30格时每格标，否则每5格标
    interval = 1 if max(grid_width, grid_height) < 30 else 5

    # 计算左边距（行号宽度）和上边距（列号高度）
    max_label_w = font.getbbox(f"{grid_height}")[2] if hasattr(font, 'getbbox') else len(str(grid_height)) * 7
    label_h = max(12, tile_size - 2)
    margin_left = max_label_w + 8
    margin_top = label_h + 4

    # 创建带边距的新画布
    w, h = img.size
    new_w = w + margin_left
    new_h = h + margin_top
    canvas = Image.new("RGB", (new_w, new_h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # 贴上原图
    canvas.paste(img, (margin_left, margin_top))

    # 列号（上方）
    text_color = (80, 80, 80)
    for col in range(0, grid_width, interval):
        x = margin_left + col * tile_size + tile_size // 2
        label = str(col + 1)
        if hasattr(font, 'getbbox'):
            tw = font.getbbox(label)[2]
        else:
            tw = len(label) * 7
        draw.text((x - tw // 2, 2), label, fill=text_color, font=font)

    # 行号（左侧）
    for row in range(0, grid_height, interval):
        y = margin_top + row * tile_size + tile_size // 2
        label = str(row + 1)
        if hasattr(font, 'getbbox'):
            tw = font.getbbox(label)[2]
            th = font.getbbox(label)[3]
        else:
            tw = len(label) * 7
            th = 10
        draw.text((margin_left - tw - 4, y - th // 2), label, fill=text_color, font=font)

    return canvas


def pixelize(
    img: Image.Image,
    pixel_size: int,
    tile_size: int = 20,
    show_grid: bool = True,
    show_board_lines: bool = True,
    board_width: int = 29,
    board_height: int = 29,
) -> Tuple[np.ndarray, Image.Image]:
    """完整的像素化 + 预览渲染管道。

    这是核心流程的外层封装，一步完成降采样和预览生成。

    Args:
        img: PIL Image (RGB 模式)
        pixel_size: 降采样块大小
        tile_size: 预览中每个豆子的像素大小
        show_grid: 是否显示网格线
        show_board_lines: 是否显示底板边界
        board_width, board_height: 底板尺寸

    Returns:
        (color_grid, preview_image) 元组:
            - color_grid: (H, W, 3) numpy rgb array (降采样后的原始色块)
            - preview_image: 带网格/底板线的预览 PIL Image
    """
    # Step 1: 降采样
    grid = downsample(img, pixel_size)

    # Step 2: 上采样为预览
    preview = upsample_for_preview(grid, tile_size)

    # Step 3: 画网格
    if show_grid:
        preview = draw_grid_lines(preview, tile_size)

    # Step 4: 画底板边界
    if show_board_lines:
        preview = draw_board_lines(
            preview, tile_size, board_width, board_height
        )

    return grid, preview
