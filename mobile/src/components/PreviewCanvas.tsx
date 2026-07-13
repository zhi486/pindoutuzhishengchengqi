import React, { useMemo } from 'react';
import { View, StyleSheet, Dimensions } from 'react-native';
import { Canvas, Rect, Text, useFont } from '@shopify/react-native-skia';
import type { ProcessResult } from '../pixelizer';

const GRID_COLOR = '#DDD';
const EMPH_COLOR = '#444';
const BOARD_COLOR = '#5090d0';
const LABEL_COLOR = '#666';

interface Props {
  result: ProcessResult;
  tileSize: number;
  showGrid: boolean;
  showBoard: boolean;
  boardSize: number;
}

export default function PreviewCanvas({
  result, tileSize, showGrid, showBoard, boardSize,
}: Props) {
  const { matchedGrid, beadW, beadH } = result;
  const marginLeft = 30;
  const marginTop = 24;

  const canvasW = beadW * tileSize + marginLeft;
  const canvasH = beadH * tileSize + marginTop;

  // 生成 Skia 绘制元素
  const elements = useMemo(() => {
    const els: React.ReactElement[] = [];
    let key = 0;

    // 像素色块
    for (let r = 0; r < beadH; r++) {
      for (let c = 0; c < beadW; c++) {
        const [rr, gg, bb] = matchedGrid[r][c];
        els.push(
          <Rect
            key={key++}
            x={marginLeft + c * tileSize}
            y={marginTop + r * tileSize}
            width={tileSize}
            height={tileSize}
            color={`rgb(${rr},${gg},${bb})`}
          />,
        );
      }
    }

    // 网格线
    if (showGrid) {
      for (let y = 0; y <= beadH; y++) {
        const emph = y % 5 === 0;
        const lw = emph ? 2 : 1;
        for (let dy = 0; dy < lw; dy++) {
          els.push(
            <Rect
              key={key++}
              x={marginLeft}
              y={marginTop + y * tileSize + dy}
              width={beadW * tileSize}
              height={1}
              color={emph ? EMPH_COLOR : GRID_COLOR}
            />,
          );
        }
      }
      for (let x = 0; x <= beadW; x++) {
        const emph = x % 5 === 0;
        const lw = emph ? 2 : 1;
        for (let dx = 0; dx < lw; dx++) {
          els.push(
            <Rect
              key={key++}
              x={marginLeft + x * tileSize + dx}
              y={marginTop}
              width={1}
              height={beadH * tileSize}
              color={emph ? EMPH_COLOR : GRID_COLOR}
            />,
          );
        }
      }

      // 交叉点恢复原色（断点效果）
      for (let y = 0; y < beadH; y++) {
        for (let x = 0; x < beadW; x++) {
          const hEmph = y % 5 === 0;
          const vEmph = x % 5 === 0;
          const gap = Math.max(hEmph ? 2 : 1, vEmph ? 2 : 1);
          const [rr, gg, bb] = matchedGrid[y][x];
          els.push(
            <Rect
              key={key++}
              x={marginLeft + x * tileSize}
              y={marginTop + y * tileSize}
              width={gap}
              height={gap}
              color={`rgb(${rr},${gg},${bb})`}
            />,
          );
        }
      }
    }

    // 底板边界
    if (showGrid && showBoard) {
      for (let y = boardSize; y < beadH; y += boardSize) {
        els.push(
          <Rect
            key={key++}
            x={marginLeft}
            y={marginTop + y * tileSize}
            width={beadW * tileSize}
            height={1}
            color={BOARD_COLOR}
          />,
        );
      }
      for (let x = boardSize; x < beadW; x += boardSize) {
        els.push(
          <Rect
            key={key++}
            x={marginLeft + x * tileSize}
            y={marginTop}
            width={1}
            height={beadH * tileSize}
            color={BOARD_COLOR}
          />,
        );
      }
    }

    // 坐标数字
    const interval = Math.max(beadW, beadH) < 30 ? 1 : 5;
    for (let c = 0; c < beadW; c += interval) {
      els.push(
        <Text
          key={key++}
          x={marginLeft + c * tileSize + tileSize / 2 - 8}
          y={marginTop - 6}
          text={String(c + 1)}
          color={LABEL_COLOR}
        />,
      );
    }
    for (let r = 0; r < beadH; r += interval) {
      els.push(
        <Text
          key={key++}
          x={marginLeft - 22}
          y={marginTop + r * tileSize + tileSize / 2 + 4}
          text={String(r + 1)}
          color={LABEL_COLOR}
        />,
      );
    }

    return els;
  }, [matchedGrid, beadW, beadH, tileSize, showGrid, showBoard, boardSize]);

  return (
    <View style={styles.container}>
      <Canvas style={{ width: canvasW, height: canvasH }}>
        {elements}
      </Canvas>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 8,
    overflow: 'hidden',
  },
});
