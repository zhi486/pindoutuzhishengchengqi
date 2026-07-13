# 拼豆图纸生成器 (Pixel Bead Studio)

将普通图片一键转换为拼豆（MARD 融合豆）像素图纸。支持实时预览、精准色彩匹配、PNG/PDF 导出。

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## ✨ 功能

- **图片像素化** — Lanczos 高质量缩放，精确控制豆子行列数，长宽比自动锁定
- **MARD 291 色色卡** — 内嵌完整 MARD 色卡（A-H + M/P/Q/R/Y/ZG 系列），CIE LAB 色彩空间 K-D 树精准匹配
- **颜色量化** — 中值切割算法自动减色，避免图案过于杂乱
- **实时预览** — 网格线（每 5 格加粗强调）、底板边界线、交叉点断点效果
- **行列号标注** — 预览图外边缘标注行列号，方便定位
- **精确控制** — 滑块 + 输入框双重调节，缩放 11 档可调
- **多格式导出** — PNG 高清图纸（带图例） + PDF 多页图纸（按底板分页，自动缩放适配 A4）
- **多底板支持** — 52×52 / 72×72 / 102×102 三种底板尺寸

## 安装

```bash
# 1. 克隆仓库
git clone https://github.com/zhi486/pindoutuzhishengchengqi.git
cd pindoutuzhishengchengqi

# 2. 安装依赖
pip install -r requirements.txt
```

## 使用

```bash
python main.py
```

1. 点击「选择图片」加载一张图片
2. 调整「豆子长度」滑块控制输出行数（宽度按原图长宽比自动计算）
3. 调整「最大颜色数」控制颜色复杂度
4. 选择底板尺寸（52×52 / 72×72 / 102×102）
5. 在预览区查看效果，用缩放按钮放大缩小
6. 点击「导出 PNG」或「导出 PDF」保存图纸

## 技术栈

| 层 | 库 | 用途 |
|---|---|---|
| GUI | customtkinter | 现代化桌面界面 |
| 图像处理 | Pillow + NumPy | 图片缩放与像素操作 |
| 色彩匹配 | SciPy cKDTree | LAB 空间最近邻搜索 |
| PDF 导出 | ReportLab | 多页矢量图纸生成 |

## 项目结构

```
├── main.py                     # 启动入口
├── requirements.txt
├── data/
│   └── perler_colors.json      # MARD 291色完整色卡
├── app/
│   ├── app_controller.py       # 中心控制器
│   ├── core/
│   │   ├── pixelizer.py        # 像素化引擎
│   │   ├── color_matcher.py    # 色卡颜色匹配
│   │   ├── color_quantizer.py  # 中值切割颜色量化
│   │   ├── bead_palette.py     # 色卡加载 + K-D 树
│   │   └── pattern.py          # 数据模型
│   ├── ui/
│   │   ├── main_window.py      # 主窗口（三栏布局）
│   │   ├── preview_canvas.py   # 像素预览渲染
│   │   ├── control_panel.py    # 参数控制面板
│   │   ├── color_legend.py     # 颜色图例
│   │   ├── image_drop_zone.py  # 图片加载
│   │   └── status_bar.py       # 底部状态栏
│   ├── export/
│   │   ├── png_exporter.py     # PNG 高清导出
│   │   └── pdf_exporter.py     # PDF 图纸导出
│   └── utils/
│       └── color_space.py      # RGB↔LAB 色彩空间转换
```

## 自定义色卡

`data/perler_colors.json` 可自行编辑，校准颜色以匹配你手上的实际豆子。格式：

```json
{
  "code": "A01",
  "name": "颜色名称",
  "hex": "#FAF4C8",
  "rgb": [250, 244, 200],
  "category": "A系列"
}
```

## License

MIT
