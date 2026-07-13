import React from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import type { ProcessResult } from '../pixelizer';

interface Props {
  result: ProcessResult;
}

export default function ColorLegend({ result }: Props) {
  const { colorSummary } = result;
  const total = colorSummary.reduce((s, c) => s + c.count, 0);

  return (
    <View style={styles.container}>
      <FlatList
        data={colorSummary}
        keyExtractor={(item) => item.code}
        renderItem={({ item }) => (
          <View style={styles.row}>
            <View style={[styles.swatch, { backgroundColor: item.hex }]} />
            <Text style={styles.code}>{item.code}</Text>
            <Text style={styles.count}>{item.count} 颗</Text>
          </View>
        )}
        ListFooterComponent={
          <Text style={styles.total}>
            共 {colorSummary.length} 色，总计 {total} 颗
          </Text>
        }
        style={styles.list}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { maxHeight: 260 },
  list: { flexGrow: 0 },
  row: { flexDirection: 'row', alignItems: 'center', paddingVertical: 3, paddingHorizontal: 4 },
  swatch: { width: 20, height: 14, borderRadius: 2, marginRight: 8, borderWidth: 1, borderColor: '#e5e7eb' },
  code: { fontSize: 12, fontWeight: '600', minWidth: 38 },
  count: { fontSize: 12, color: '#888', marginLeft: 'auto' },
  total: { fontSize: 12, fontWeight: '600', color: '#555', marginTop: 8, paddingHorizontal: 4 },
});
