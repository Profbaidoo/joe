import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Share } from 'react-native';
import { THEME } from '../constants/theme';

interface ReceiptViewProps {
  order: any;
  transaction: any;
  onDone: () => void;
}

export const ReceiptView: React.FC<ReceiptViewProps> = ({ order, transaction, onDone }) => {
  const handleShare = async () => {
    try {
      await Share.share({
        message: `Blessings Telecom Receipt\nRef: ${order.order_reference}\nPaid: GH₵ ${Number(order.total_amount).toFixed(2)}\nService: ${order.order_type} (${order.network_code})\nPhone: ${order.recipient_phone}\nStatus: COMPLETED`,
      });
    } catch (e) {
      // share canceled
    }
  };

  return (
    <View style={styles.card}>
      <View style={styles.badgeContainer}>
        <Text style={styles.badgeText}>✓ TRANSACTION RECEIPT</Text>
      </View>

      <Text style={styles.companyName}>{THEME.business.name}</Text>
      <Text style={styles.amount}>GH₵ {Number(order?.total_amount || 0).toFixed(2)}</Text>

      <View style={styles.divider} />

      <View style={styles.row}>
        <Text style={styles.label}>Order Ref</Text>
        <Text style={styles.valMono}>{order?.order_reference}</Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>Network</Text>
        <Text style={styles.valBold}>{order?.network_code}</Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>Recipient Phone</Text>
        <Text style={styles.val}>{order?.recipient_phone}</Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>Type</Text>
        <Text style={styles.val}>{order?.order_type}</Text>
      </View>

      <View style={styles.row}>
        <Text style={styles.label}>Time (Accra)</Text>
        <Text style={styles.val}>{new Date().toLocaleTimeString('en-GH')}</Text>
      </View>

      <View style={styles.actions}>
        <TouchableOpacity style={styles.shareButton} onPress={handleShare}>
          <Text style={styles.shareText}>Share Receipt</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.doneButton} onPress={onDone}>
          <Text style={styles.doneText}>Done</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 24,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08,
    shadowRadius: 12,
    elevation: 4,
  },
  badgeContainer: {
    backgroundColor: '#ECFDF5',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#A7F3D0',
    marginBottom: 12,
  },
  badgeText: {
    fontSize: 11,
    fontWeight: '800',
    color: '#065F46',
  },
  companyName: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0F172A',
  },
  amount: {
    fontSize: 32,
    fontWeight: '900',
    color: '#0F172A',
    marginVertical: 8,
  },
  divider: {
    height: 1,
    backgroundColor: '#F1F5F9',
    width: '100%',
    marginVertical: 12,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    paddingVertical: 6,
  },
  label: {
    fontSize: 13,
    color: '#64748B',
  },
  val: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1E293B',
  },
  valBold: {
    fontSize: 13,
    fontWeight: '800',
    color: '#0F172A',
  },
  valMono: {
    fontSize: 12,
    fontFamily: 'monospace',
    fontWeight: '700',
    color: '#0F172A',
  },
  actions: {
    flexDirection: 'row',
    marginTop: 20,
    gap: 12,
    width: '100%',
  },
  shareButton: {
    flex: 1,
    backgroundColor: '#F1F5F9',
    paddingVertical: 12,
    borderRadius: 14,
    alignItems: 'center',
  },
  shareText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#334155',
  },
  doneButton: {
    flex: 1,
    backgroundColor: '#0F172A',
    paddingVertical: 12,
    borderRadius: 14,
    alignItems: 'center',
  },
  doneText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#FFFFFF',
  },
});
