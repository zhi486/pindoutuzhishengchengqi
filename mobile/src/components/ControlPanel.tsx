import React from 'react';
import {
  View, Text, TextInput, Switch, StyleSheet, ScrollView,
  TouchableOpacity,
} from 'react-native';

interface Props {
  beadH: number; beadW: number;
  maxColors: number;
  showGrid: boolean; showBoard: boolean;
  boardSize: number; tileSize: number;
  onBeadHChange: (v: number) => void;
  onMaxColorsChange: (v: number) => void;
  onShowGridChange: (v: boolean) => void;
  onShowBoardChange: (v: boolean) => void;
  onBoardSizeChange: (v: number) => void;
  onZoomIn: () => void; onZoomOut: () => void; onZoomReset: () => void;
  onExportPNG: () => void; onExportPDF: () => void;
}

const BOARD_SIZES = [52, 72, 102];

function NumberStepper({ value, min, max, step, onChange, label }: {
  value: number; min: number; max: number; step: number;
  onChange: (v: number) => void; label: string;
}) {
  return (
    <View>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.stepperRow}>
        <TouchableOpacity
          style={styles.stepBtn}
          onPress={() => onChange(Math.max(min, value - step))}
        >
          <Text style={styles.stepBtnText}>−</Text>
        </TouchableOpacity>
        <TextInput
          style={styles.input}
          value={String(value)}
          onChangeText={(t) => {
            const v = parseInt(t);
            if (!isNaN(v) && v >= min && v <= max) onChange(v);
          }}
          keyboardType="number-pad"
        />
        <TouchableOpacity
          style={styles.stepBtn}
          onPress={() => onChange(Math.min(max, value + step))}
        >
          <Text style={styles.stepBtnText}>+</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

export default function ControlPanel(props: Props) {
  const { beadH, beadW, maxColors, showGrid, showBoard, boardSize, tileSize,
    onBeadHChange, onMaxColorsChange, onShowGridChange, onShowBoardChange,
    onBoardSizeChange, onZoomIn, onZoomOut, onZoomReset, onExportPNG, onExportPDF,
  } = props;

  return (
    <ScrollView style={styles.panel} contentContainerStyle={styles.content}>
      <NumberStepper value={beadH} min={5} max={200} step={5}
        label="豆子长度（行数）" onChange={onBeadHChange} />
      <Text style={styles.hint}>宽度: {beadW} 列（自动按比例）</Text>

      <NumberStepper value={maxColors} min={4} max={150} step={4}
        label="最大颜色数" onChange={onMaxColorsChange} />

      <View style={styles.switchRow}>
        <Text>显示网格线</Text>
        <Switch value={showGrid} onValueChange={onShowGridChange} />
      </View>
      <View style={styles.switchRow}>
        <Text>显示底板边界</Text>
        <Switch value={showBoard} onValueChange={onShowBoardChange} />
      </View>

      <Text style={styles.label}>底板尺寸</Text>
      <View style={styles.chipRow}>
        {BOARD_SIZES.map((s) => (
          <TouchableOpacity
            key={s}
            style={[styles.chip, boardSize === s && styles.chipActive]}
            onPress={() => onBoardSizeChange(s)}
          >
            <Text style={[styles.chipText, boardSize === s && styles.chipTextActive]}>
              {s}×{s}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.label}>预览缩放</Text>
      <View style={styles.stepperRow}>
        <TouchableOpacity style={styles.zoomBtn} onPress={onZoomOut}>
          <Text style={styles.zoomBtnText}>−</Text>
        </TouchableOpacity>
        <Text style={styles.zoomLabel}>{tileSize}px</Text>
        <TouchableOpacity style={styles.zoomBtn} onPress={onZoomIn}>
          <Text style={styles.zoomBtnText}>+</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.resetBtn} onPress={onZoomReset}>
          <Text style={styles.resetBtnText}>↺</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.label}>导出图纸</Text>
      <View style={styles.exportRow}>
        <TouchableOpacity style={styles.exportBtn} onPress={onExportPNG}>
          <Text style={styles.exportBtnText}>导出 PNG</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.exportBtn, styles.exportBtnPdf]} onPress={onExportPDF}>
          <Text style={styles.exportBtnText}>导出 PDF</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  panel: { flex: 1 },
  content: { padding: 12, gap: 4 },
  label: { fontSize: 13, fontWeight: '600', color: '#666', marginTop: 14, marginBottom: 6 },
  hint: { fontSize: 12, color: '#999', marginBottom: 2 },
  stepperRow: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  stepBtn: { width: 36, height: 34, borderWidth: 1, borderColor: '#ddd', borderRadius: 6, alignItems: 'center', justifyContent: 'center', backgroundColor: '#fff' },
  stepBtnText: { fontSize: 18, color: '#555' },
  input: { width: 60, height: 34, borderWidth: 1, borderColor: '#ddd', borderRadius: 6, textAlign: 'center', fontSize: 14, fontWeight: '600', padding: 4 },
  switchRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 6, marginTop: 8 },
  chipRow: { flexDirection: 'row', gap: 8 },
  chip: { paddingHorizontal: 14, paddingVertical: 7, borderRadius: 6, borderWidth: 1, borderColor: '#ddd', backgroundColor: '#fff' },
  chipActive: { backgroundColor: '#3b82f6', borderColor: '#3b82f6' },
  chipText: { fontSize: 13, color: '#333' },
  chipTextActive: { color: '#fff' },
  zoomBtn: { width: 36, height: 30, borderWidth: 1, borderColor: '#ddd', borderRadius: 4, alignItems: 'center', justifyContent: 'center', backgroundColor: '#fff' },
  zoomBtnText: { fontSize: 16, color: '#333' },
  zoomLabel: { fontSize: 14, fontWeight: '700', minWidth: 44, textAlign: 'center' },
  resetBtn: { paddingHorizontal: 10, paddingVertical: 5, borderWidth: 1, borderColor: '#ddd', borderRadius: 4 },
  resetBtnText: { fontSize: 14, color: '#666' },
  exportRow: { flexDirection: 'row', gap: 10, marginTop: 4 },
  exportBtn: { flex: 1, paddingVertical: 13, borderRadius: 8, backgroundColor: '#3b82f6', alignItems: 'center' },
  exportBtnPdf: { backgroundColor: '#ef4444' },
  exportBtnText: { color: '#fff', fontSize: 14, fontWeight: '600' },
});
