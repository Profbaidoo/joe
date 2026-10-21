import React, { useEffect, useState } from 'react';
import {
  Modal,
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { THEME } from '../constants/theme';
import { mobileApi } from '../services/api';

interface PaymentModalProps {
  visible: boolean;
  order: any;
  transactionRef: string;
  token: string;
  onSuccess: (receiptData: any) => void;
  onCancel: () => void;
}

export const PaymentModal: React.FC<PaymentModalProps> = ({
  visible,
  order,
  transactionRef,
  token,
  onSuccess,
  onCancel,
}) => {
  const [status, setStatus] = useState<'PENDING' | 'SUCCESSFUL' | 'FAILED'>('PENDING');
  const [statusMessage, setStatusMessage] = useState('Payment prompt sent. Please approve on your phone.');

  useEffect(() => {
    if (!visible || !transactionRef) return;

    let isMounted = true;
    const interval = setInterval(async () => {
      try {
        const res = await mobileApi.pollPaymentStatus(token, transactionRef);
        if (!isMounted) return;

        if (res.status === 'SUCCESSFUL') {
          setStatus('SUCCESSFUL');
          setStatusMessage('Payment verified! Order fulfilled.');
          clearInterval(interval);
          setTimeout(() => {
            onSuccess(res);
          }, 1500);
        } else if (res.status === 'FAILED') {
          setStatus('FAILED');
          setStatusMessage(res.reason || 'Payment rejected by subscriber.');
          clearInterval(interval);
        }
      } catch (e) {
        // keep polling
      }
    }, 3000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [visible, transactionRef]);

  if (!visible) return null;

  return (
    <Modal visible={visible} transparent animationType="fade">
      <View style={styles.overlay}>
        <View style={styles.card}>
          <View style={styles.header}>
            <Text style={styles.headerTitle}>Mobile Money Payment</Text>
            <Text style={styles.headerSubtitle}>MTN • Telecel • AT</Text>
          </View>

          <View style={styles.content}>
            <View style={styles.amountContainer}>
              <Text style={styles.amountLabel}>Total Payable</Text>
              <Text style={styles.amountValue}>
                GH₵ {Number(order?.total_amount || 0).toFixed(2)}
              </Text>
            </View>

            {status === 'PENDING' && (
              <View style={styles.statusBox}>
                <ActivityIndicator size="large" color={THEME.colors.primaryDark} />
                <Text style={styles.statusTitle}>Approve Prompt on Handset</Text>
                <Text style={styles.statusText}>
                  A payment authorization prompt has been pushed to{' '}
                  <Text style={styles.bold}>{order?.recipient_phone}</Text>. Please enter your MoMo PIN directly on your device.
                </Text>
                <Text style={styles.securityNotice}>
                  🔒 We will NEVER ask you for your MoMo PIN.
                </Text>
              </View>
            )}

            {status === 'SUCCESSFUL' && (
              <View style={[styles.statusBox, styles.successBox]}>
                <Text style={styles.successIcon}>✓</Text>
                <Text style={styles.successTitle}>Payment Confirmed!</Text>
                <Text style={styles.statusText}>{statusMessage}</Text>
              </View>
            )}

            {status === 'FAILED' && (
              <View style={[styles.statusBox, styles.failedBox]}>
                <Text style={styles.failedTitle}>Payment Failed</Text>
                <Text style={styles.statusText}>{statusMessage}</Text>
              </View>
            )}

            <TouchableOpacity
              style={styles.cancelButton}
              onPress={onCancel}
            >
              <Text style={styles.cancelText}>
                {status === 'SUCCESSFUL' ? 'Close' : 'Cancel Transaction'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.75)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  card: {
    width: '100%',
    maxWidth: 380,
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    overflow: 'hidden',
  },
  header: {
    backgroundColor: THEME.colors.primary,
    padding: 20,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
  },
  headerSubtitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#334155',
    marginTop: 2,
  },
  content: {
    padding: 20,
  },
  amountContainer: {
    alignItems: 'center',
    marginBottom: 20,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  amountLabel: {
    fontSize: 12,
    color: '#64748B',
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  amountValue: {
    fontSize: 28,
    fontWeight: '900',
    color: '#0F172A',
    marginTop: 4,
  },
  statusBox: {
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#FFFBEB',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#FDE68A',
    marginBottom: 20,
  },
  successBox: {
    backgroundColor: '#ECFDF5',
    borderColor: '#A7F3D0',
  },
  failedBox: {
    backgroundColor: '#FEF2F2',
    borderColor: '#FECACA',
  },
  statusTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#92400E',
    marginTop: 12,
    marginBottom: 6,
  },
  successTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#065F46',
    marginTop: 6,
    marginBottom: 4,
  },
  failedTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#991B1B',
    marginBottom: 4,
  },
  successIcon: {
    fontSize: 28,
    color: '#059669',
    fontWeight: 'bold',
  },
  statusText: {
    fontSize: 12,
    color: '#475569',
    textAlign: 'center',
    lineHeight: 18,
  },
  bold: {
    fontWeight: '700',
    color: '#0F172A',
  },
  securityNotice: {
    fontSize: 11,
    color: '#B45309',
    fontWeight: '700',
    marginTop: 8,
  },
  cancelButton: {
    paddingVertical: 12,
    borderRadius: 14,
    backgroundColor: '#F1F5F9',
    alignItems: 'center',
  },
  cancelText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#475569',
  },
});
