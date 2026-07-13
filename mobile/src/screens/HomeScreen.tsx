import React, { useState, useCallback, useRef } from 'react';
import {
  View, Text, TouchableOpacity, ScrollView, StyleSheet,
  Alert, ActivityIndicator, useWindowDimensions,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import { Skia, useImage, Canvas, Image as SkiaImage } from '@shopify/react-native-skia';
import ViewShot from 'react-native-view-shot';

import PreviewCanvas from '../components/PreviewCanvas';
import ControlPanel from '../components/ControlPanel';
import ColorLegend from '../components/ColorLegend';
import { processPixels, computeBeadW, type ProcessResult } from '../pixelizer';

const ZOOM_LEVELS = [5, 8, 10, 12, 15, 18, 20, 25, 30, 40, 50];

export default function HomeScreen() {
  const { width: screenW } = useWindowDimensions();
  const viewShotRef = useRef<any>(null);

  // Image state
  const [imgUri, setImgUri] = useState<string | null>(null);
  const [imgDims, setImgDims] = useState({ w: 0, h: 0 });
  const [loading, setLoading] = useState(false);

  // Parameters
  const [beadH, setBeadH] = useState(52);
  const [maxColors, setMaxColors] = useState(50);
  const [showGrid, setShowGrid] = useState(true);
  const [showBoard, setShowBoard] = useState(true);
  const [boardSize, setBoardSize] = useState(52);
  const [tileSize, setTileSize] = useState(15);

  // Result
  const [result, setResult] = useState<ProcessResult | null>(null);

  const beadW = imgDims.w > 0 ? computeBeadW(imgDims.w, imgDims.h, beadH) : 0;

  // ── Image Picking ─────────────────────────────
  const pickImage = useCallback(async () => {
    const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!perm.granted) {
      Alert.alert('需要相册权限', '请在设置中允许访问相册');
      return;
    }

    const pickerResult = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      quality: 1,
    });

    if (!pickerResult.canceled && pickerResult.assets[0]) {
      setImgUri(pickerResult.assets[0].uri);
      const { width, height } = pickerResult.assets[0];
      setImgDims({ w: width, h: height });
    }
  }, []);

  // ── Processing ────────────────────────────────
  const processImage = useCallback(async () => {
    if (!imgUri) return;
    setLoading(true);

    try {
      const targetH = beadH;
      const targetW = beadW;

      // Use Skia to resize and read pixels
      const image = Skia.Image.MakeImageFromEncoded(
        Skia.Data.fromURI(imgUri),
      );
      if (!image) throw new Error('无法加载图片');

      // Create offscreen surface at target size
      const surface = Skia.Surface.Make(targetW, targetH);
      if (!surface) throw new Error('无法创建渲染面');

      const canvas = surface.getCanvas();
      canvas?.drawImageRect(
        image,
        { x: 0, y: 0, width: image.width(), height: image.height() },
        { x: 0, y: 0, width: targetW, height: targetH },
        Skia.Paint(),
      );

      const snap = surface.makeImageSnapshot();
      const pixels = snap.readPixels();
      if (!pixels) throw new Error('无法读取像素');

      const res = processPixels(pixels, targetW, targetH, maxColors);
      setResult(res);
    } catch (e: any) {
      Alert.alert('处理失败', e.message);
    } finally {
      setLoading(false);
    }
  }, [imgUri, beadH, beadW, maxColors]);

  // ── Zoom ──────────────────────────────────────
  const zoomIn = () => {
    const cur = tileSize;
    const next = ZOOM_LEVELS.find((z) => z > cur) || Math.min(cur + 10, 50);
    setTileSize(next);
  };
  const zoomOut = () => {
    const cur = tileSize;
    const reversed = [...ZOOM_LEVELS].reverse();
    const next = reversed.find((z) => z < cur) || Math.max(cur - 10, 3);
    setTileSize(next);
  };
  const zoomReset = () => setTileSize(20);

  // ── Exports ───────────────────────────────────
  const exportPNG = async () => {
    if (!result) return;
    try {
      const uri = await (viewShotRef.current as any)?.capture?.();
      if (uri) {
        await Sharing.shareAsync(uri, { mimeType: 'image/png' });
      }
    } catch (e: any) {
      Alert.alert('导出失败', e.message);
    }
  };

  const exportPDF = () => {
    Alert.alert('PDF 导出', '移动端 PDF 导出功能开发中，请使用网页版 bead_pattern.html 导出 PDF');
  };

  // ── Render ────────────────────────────────────
  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>拼豆图纸生成器</Text>
        {result && (
          <Text style={styles.status}>
            {beadW}×{beadH} | {result.colorSummary.length}色 | {result.colorSummary.reduce((s,c)=>s+c.count,0)}颗
          </Text>
        )}
      </View>

      <View style={styles.body}>
        {/* Left: Preview */}
        <View style={styles.previewArea}>
          <ViewShot ref={viewShotRef} options={{ format: 'png', quality: 1 }}>
            {result ? (
              <ScrollView horizontal showsHorizontalScrollIndicator>
                <ScrollView showsVerticalScrollIndicator>
                  <PreviewCanvas
                    result={result}
                    tileSize={tileSize}
                    showGrid={showGrid}
                    showBoard={showBoard}
                    boardSize={boardSize}
                  />
                </ScrollView>
              </ScrollView>
            ) : (
              <TouchableOpacity style={styles.uploadZone} onPress={pickImage}>
                <Text style={styles.uploadText}>
                  {imgUri ? '点击处理图片' : '📷 选择图片'}
                </Text>
              </TouchableOpacity>
            )}
          </ViewShot>

          {imgUri && (
            <TouchableOpacity
              style={[styles.processBtn, loading && { opacity: 0.5 }]}
              onPress={processImage}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.processBtnText}>生成图纸</Text>
              )}
            </TouchableOpacity>
          )}
        </View>

        {/* Right: Controls */}
        <ScrollView style={styles.controlArea}>
          <ControlPanel
            beadH={beadH}
            beadW={beadW}
            maxColors={maxColors}
            showGrid={showGrid}
            showBoard={showBoard}
            boardSize={boardSize}
            tileSize={tileSize}
            onBeadHChange={setBeadH}
            onMaxColorsChange={setMaxColors}
            onShowGridChange={setShowGrid}
            onShowBoardChange={setShowBoard}
            onBoardSizeChange={setBoardSize}
            onZoomIn={zoomIn}
            onZoomOut={zoomOut}
            onZoomReset={zoomReset}
            onExportPNG={exportPNG}
            onExportPDF={exportPDF}
          />

          {result && <ColorLegend result={result} />}
        </ScrollView>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f6f8' },
  header: {
    backgroundColor: '#fff', padding: 12,
    borderBottomWidth: 1, borderBottomColor: '#e5e7eb',
    alignItems: 'center',
  },
  title: { fontSize: 18, fontWeight: '700' },
  status: { fontSize: 12, color: '#888', marginTop: 4 },
  body: { flex: 1, flexDirection: 'row' },
  previewArea: { flex: 2, padding: 8, gap: 8 },
  controlArea: { flex: 1, minWidth: 250, maxWidth: 320, backgroundColor: '#fff', borderLeftWidth: 1, borderLeftColor: '#e5e7eb' },
  uploadZone: { flex: 1, borderWidth: 2, borderColor: '#ddd', borderStyle: 'dashed', borderRadius: 8, alignItems: 'center', justifyContent: 'center', minHeight: 200, backgroundColor: '#fff' },
  uploadText: { fontSize: 15, color: '#888' },
  processBtn: { backgroundColor: '#3b82f6', paddingVertical: 12, borderRadius: 8, alignItems: 'center' },
  processBtnText: { color: '#fff', fontSize: 14, fontWeight: '600' },
});
