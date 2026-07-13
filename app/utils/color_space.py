"""RGB ↔ CIE L*a*b* 色彩空间转换与 Delta-E 色差计算。

纯函数模块，零外部依赖（仅使用 math 和 numpy）。
参考: CIE 1976 (L*, a*, b*) 色彩空间标准。
"""

import math
import numpy as np

# D65 标准白点 (CIE 1931 2° 标准观察者)
REF_X = 0.95047
REF_Y = 1.00000
REF_Z = 1.08883

# sRGB 线性化阈值
_LIN_THRESHOLD = 0.04045
_LIN_DIVISOR = 12.92
_LIN_POWER_DIVISOR = 1.055
_LIN_POWER_OFFSET = 0.055
_LIN_GAMMA = 2.4

# LAB 转换中的 CIE 标准常数
_LAB_DELTA = 6.0 / 29.0  # (6/29)
_LAB_DELTA_CUBED = _LAB_DELTA ** 3
_LAB_K = 841.0 / 108.0   # 用于 t <= (6/29)^3 时的线性段
_LAB_OFFSET = 4.0 / 29.0


def srgb_to_linear(rgb: np.ndarray) -> np.ndarray:
    """将 sRGB 值（0-255 或 0.0-1.0）转换为线性 RGB。

    Args:
        rgb: numpy 数组，值范围 [0, 255]（整数）或 [0.0, 1.0]（浮点）

    Returns:
        线性 RGB，值范围 [0.0, 1.0]
    """
    if rgb.dtype == np.uint8 or rgb.max() > 1.0:
        rgb = rgb.astype(np.float64) / 255.0
    else:
        rgb = rgb.astype(np.float64)

    # 元素级 sRGB 逆向 gamma 校正
    out = np.where(
        rgb <= _LIN_THRESHOLD,
        rgb / _LIN_DIVISOR,
        ((rgb + _LIN_POWER_OFFSET) / _LIN_POWER_DIVISOR) ** _LIN_GAMMA,
    )
    return out


# RGB → XYZ 转换矩阵 (D65, sRGB 原色)
_MAT_RGB2XYZ = np.array(
    [
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ],
    dtype=np.float64,
)


def linear_rgb_to_xyz(linear_rgb: np.ndarray) -> np.ndarray:
    """将线性 RGB 转换为 CIE XYZ (D65)。

    支持单像素 (3,) 和批量 (N, 3) 两种输入形状。
    """
    shape = linear_rgb.shape
    if linear_rgb.ndim == 1:
        return np.dot(_MAT_RGB2XYZ, linear_rgb)
    elif linear_rgb.ndim == 2:
        return np.dot(linear_rgb, _MAT_RGB2XYZ.T)
    else:
        raise ValueError(f"期望形状为 (3,) 或 (N, 3)，实际为 {shape}")


def _lab_f(t: np.ndarray) -> np.ndarray:
    """CIE LAB 辅助函数 f(t)。"""
    return np.where(
        t > _LAB_DELTA_CUBED,
        np.cbrt(t),
        _LAB_K * t + _LAB_OFFSET,
    )


def xyz_to_lab(xyz: np.ndarray) -> np.ndarray:
    """将 CIE XYZ (D65) 转换为 CIE L*a*b*。

    支持单像素 (3,) 和批量 (N, 3) 两种输入形状。
    """
    # 除以参考白点
    xn = xyz[..., 0] / REF_X
    yn = xyz[..., 1] / REF_Y
    zn = xyz[..., 2] / REF_Z

    fy = _lab_f(yn)
    fx = _lab_f(xn)
    fz = _lab_f(zn)

    L = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)

    if xyz.ndim == 1:
        return np.array([L, a, b], dtype=np.float64)
    else:
        return np.stack([L, a, b], axis=-1)


def rgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    """将 sRGB 直接转换为 CIE L*a*b*。

    支持单像素 RGB (3,) 和批量 (N, 3) 两种输入。
    这是最常用的对外接口。

    Args:
        rgb: numpy 数组，值范围 [0, 255] 或 [0.0, 1.0]

    Returns:
        CIE L*a*b* 值: L* ∈ [0, 100], a* ∈ [-128, 128], b* ∈ [-128, 128]
    """
    linear = srgb_to_linear(rgb)
    xyz = linear_rgb_to_xyz(linear)
    return xyz_to_lab(xyz)


def delta_e_76(lab1: np.ndarray, lab2: np.ndarray) -> np.ndarray:
    """计算 CIE76 ΔE 色差（欧几里得距离）。

    支持单色比较和批量比较。

    Args:
        lab1: 形状 (3,) 或 (N, 3) 的 L*a*b* 值
        lab2: 形状 (3,) 或 (M, 3) 的 L*a*b* 值

    Returns:
        标量或 (N, M) 的色差矩阵
    """
    diff = lab1 - lab2
    return np.sqrt(np.sum(diff ** 2, axis=-1))


def rgb_to_lab_vectorized(rgb_array: np.ndarray) -> np.ndarray:
    """批量将 (N, 3) 的 sRGB 数组转换为 L*a*b*。

    优化版：一次性对整个数组做矩阵运算。
    """
    return rgb_to_lab(rgb_array)
