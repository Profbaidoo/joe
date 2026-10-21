import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  TextInput,
  StatusBar,
  Alert,
} from 'react-native';
import { THEME } from './src/constants/theme';
import { detectNetworkFromPrefix, mobileApi } from './src/services/api';
import { PaymentModal } from './src/components/PaymentModal';
import { ReceiptView } from './src/components/ReceiptView';

export default function App() {
  const [activeTab, setActiveTab] = useState<'home' | 'airtime' | 'data' | 'bills' | 'history'>('home');
  
  // Dummy or stored token for authenticated sessions
  const [token, setToken] = useState('demo-token');

  // Airtime State
  const [airtimePhone, setAirtimePhone] = useState('0241234567');
  const [detectedNetwork, setDetectedNetwork] = useState<'MTN' | 'TELECEL' | 'AT' | null>('MTN');
  const [airtimeAmount, setAirtimeAmount] = useState('10.00');

  // Data Bundle State
  const [dataNetwork, setDataNetwork] = useState<'MTN' | 'TELECEL' | 'AT'>('MTN');
  const [dataPhone, setDataPhone] = useState('0241234567');
  const [selectedPlan, setSelectedPlan] = useState<any>(null);

  // Utility Bill State
  const [meterNumber, setMeterNumber] = useState('142385920');
  const [meterType, setMeterType] = useState<'PREPAID' | 'POSTPAID'>('PREPAID');
  const [billAmount, setBillAmount] = useState('50.00');

  // Payment & Receipt Modals
  const [paymentVisible, setPaymentVisible] = useState(false);
  const [pendingOrder, setPendingOrder] = useState<any>(null);
  const [activeTrxRef, setActiveTrxRef] = useState<string>('');
  const [completedReceipt, setCompletedReceipt] = useState<any>(null);

  // Auto-detect network when phone number changes
  useEffect(() => {
    const net = detectNetworkFromPrefix(airtimePhone);
    if (net) setDetectedNetwork(net);
  }, [airtimePhone]);

  // Data Bundles Data
  const bundlePlans = [
    { id: 1, network: 'MTN', name: 'MTN 1GB Data', volume: '1 GB', validity: '30 Days', price: 12.00 },
    { id: 2, network: 'MTN', name: 'MTN 2.5GB Data', volume: '2.5 GB', validity: '30 Days', price: 25.00 },
    { id: 3, network: 'MTN', name: 'MTN 10GB Non-Expiry', volume: '10 GB', validity: 'Non-Expiry', price: 75.00 },
    { id: 4, network: 'TELECEL', name: 'Telecel 1.5GB Data', volume: '1.5 GB', validity: '30 Days', price: 12.00 },
    { id: 5, network: 'TELECEL', name: 'Telecel 6GB Non-Expiry', volume: '6 GB', validity: 'Non-Expiry', price: 38.00 },
    { id: 6, network: 'AT', name: 'AT 2GB Big Time Data', volume: '2 GB', validity: 'Non-Expiry', price: 10.00 },
    { id: 7, network: 'AT', name: 'AT 10GB Big Time Data', volume: '10 GB', validity: 'Non-Expiry', price: 35.00 },
  ];

  const handleCheckoutAirtime = () => {
    if (!detectedNetwork) {
      Alert.alert('Invalid Phone', 'Please enter a valid Ghanaian mobile number.');
      return;
    }
    const order = {
      order_reference: `ORD-${Date.now().toString(16).toUpperCase()}`,
      recipient_phone: airtimePhone,
      network_code: detectedNetwork,
      total_amount: parseFloat(airtimeAmount),
      order_type: 'AIRTIME',
    };
    setPendingOrder(order);
    setActiveTrxRef(`TRX-${Date.now().toString(16).toUpperCase()}`);
    setPaymentVisible(true);
  };

  const handleCheckoutData = (plan: any) => {
    const order = {
      order_reference: `ORD-${Date.now().toString(16).toUpperCase()}`,
      recipient_phone: dataPhone,
      network_code: plan.network,
      total_amount: plan.price,
      order_type: 'DATA_BUNDLE',
      plan_name: plan.name,
    };
    setPendingOrder(order);
    setActiveTrxRef(`TRX-${Date.now().toString(16).toUpperCase()}`);
    setPaymentVisible(true);
  };

  const handleCheckoutBill = () => {
    const order = {
      order_reference: `ECG-${Date.now().toString(16).toUpperCase()}`,
      recipient_phone: '0240000000',
      network_code: 'ECG',
      total_amount: parseFloat(billAmount),
      order_type: 'UTILITY_BILL',
      meter_number: meterNumber,
    };
    setPendingOrder(order);
    setActiveTrxRef(`TRX-${Date.now().toString(16).toUpperCase()}`);
    setPaymentVisible(true);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#FFCC00" />

      {/* Top Header */}
      <View style={styles.topBar}>
        <View style={styles.brandRow}>
          <View style={styles.logoBadge}>
            <Text style={styles.logoSymbol}>₵</Text>
          </View>
          <View>
            <Text style={styles.appName}>{THEME.business.name}</Text>
            <Text style={styles.appSubtitle}>MoMo & Telecom Services</Text>
          </View>
        </View>
        <View style={styles.statusPill}>
          <Text style={styles.statusPillText}>SANDBOX</Text>
        </View>
      </View>

      <ScrollView style={styles.mainScroll} contentContainerStyle={styles.scrollContent}>
        {completedReceipt && (
          <View style={{ marginBottom: 20 }}>
            <ReceiptView
              order={completedReceipt.order || pendingOrder}
              transaction={completedReceipt}
              onDone={() => setCompletedReceipt(null)}
            />
          </View>
        )}

        {/* TAB 1: HOME */}
        {activeTab === 'home' && (
          <View style={styles.section}>
            {/* Wallet Balance Card */}
            <View style={styles.walletCard}>
              <Text style={styles.walletLabel}>CUSTOMER WALLET BALANCE</Text>
              <Text style={styles.walletAmount}>GH₵ 150.00</Text>
              <Text style={styles.walletSub}>Ready for instant Airtime & Data checkout</Text>
            </View>

            {/* Quick Actions */}
            <Text style={styles.sectionTitle}>Services</Text>
            <View style={styles.grid}>
              <TouchableOpacity
                style={styles.actionCard}
                onPress={() => setActiveTab('airtime')}
              >
                <View style={[styles.iconCircle, { backgroundColor: '#FEF3C7' }]}>
                  <Text style={styles.iconEmoji}>📱</Text>
                </View>
                <Text style={styles.actionTitle}>Buy Airtime</Text>
                <Text style={styles.actionDesc}>MTN • Telecel • AT</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.actionCard}
                onPress={() => setActiveTab('data')}
              >
                <View style={[styles.iconCircle, { backgroundColor: '#EDE9FE' }]}>
                  <Text style={styles.iconEmoji}>🌐</Text>
                </View>
                <Text style={styles.actionTitle}>Data Bundles</Text>
                <Text style={styles.actionDesc}>4G / 5G High Speed</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.actionCard}
                onPress={() => setActiveTab('bills')}
              >
                <View style={[styles.iconCircle, { backgroundColor: '#DCFCE7' }]}>
                  <Text style={styles.iconEmoji}>⚡</Text>
                </View>
                <Text style={styles.actionTitle}>ECG Bills</Text>
                <Text style={styles.actionDesc}>Prepaid & Postpaid</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.actionCard}
                onPress={() => setActiveTab('history')}
              >
                <View style={[styles.iconCircle, { backgroundColor: '#E0F2FE' }]}>
                  <Text style={styles.iconEmoji}>🧾</Text>
                </View>
                <Text style={styles.actionTitle}>Receipts</Text>
                <Text style={styles.actionDesc}>Transaction History</Text>
              </TouchableOpacity>
            </View>

            {/* Safety Guarantee */}
            <View style={styles.securityBanner}>
              <Text style={styles.securityTitle}>🔒 Bank-Grade Security</Text>
              <Text style={styles.securityBody}>
                All transactions are confirmed via official telco authorization prompts. We never ask for or store your Mobile Money PIN.
              </Text>
            </View>
          </View>
        )}

        {/* TAB 2: AIRTIME */}
        {activeTab === 'airtime' && (
          <View style={styles.section}>
            <Text style={styles.screenHeading}>Buy Airtime Top-Up</Text>
            <Text style={styles.screenSub}>Instant delivery to any Ghanaian mobile number</Text>

            <View style={styles.formCard}>
              <Text style={styles.inputLabel}>Recipient Phone Number</Text>
              <TextInput
                style={styles.input}
                value={airtimePhone}
                onChangeText={setAirtimePhone}
                placeholder="0241234567"
                keyboardType="phone-pad"
              />

              {detectedNetwork && (
                <View style={styles.detectedRow}>
                  <Text style={styles.detectedLabel}>Detected Telco Network:</Text>
                  <View style={[styles.networkBadge, { backgroundColor: THEME.colors.networks[detectedNetwork]?.bg || '#FFCC00' }]}>
                    <Text style={[styles.networkBadgeText, { color: THEME.colors.networks[detectedNetwork]?.text || '#000000' }]}>
                      {detectedNetwork}
                    </Text>
                  </View>
                </View>
              )}

              <Text style={[styles.inputLabel, { marginTop: 16 }]}>Select Amount (GH₵)</Text>
              <View style={styles.amountPills}>
                {['2.00', '5.00', '10.00', '20.00', '50.00', '100.00'].map((amt) => (
                  <TouchableOpacity
                    key={amt}
                    style={[styles.amtPill, airtimeAmount === amt && styles.amtPillActive]}
                    onPress={() => setAirtimeAmount(amt)}
                  >
                    <Text style={[styles.amtPillText, airtimeAmount === amt && styles.amtPillTextActive]}>
                      GH₵ {amt}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>

              <TouchableOpacity style={styles.primaryButton} onPress={handleCheckoutAirtime}>
                <Text style={styles.primaryButtonText}>Pay GH₵ {airtimeAmount} with MoMo</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        {/* TAB 3: DATA BUNDLES */}
        {activeTab === 'data' && (
          <View style={styles.section}>
            <Text style={styles.screenHeading}>Internet Data Bundles</Text>
            <Text style={styles.screenSub}>Superfast data with non-expiry options</Text>

            {/* Network Selector Tabs */}
            <View style={styles.tabRow}>
              {(['MTN', 'TELECEL', 'AT'] as const).map((net) => (
                <TouchableOpacity
                  key={net}
                  style={[styles.netTab, dataNetwork === net && styles.netTabActive]}
                  onPress={() => setDataNetwork(net)}
                >
                  <Text style={[styles.netTabText, dataNetwork === net && styles.netTabTextActive]}>
                    {net}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <View style={styles.formCard}>
              <Text style={styles.inputLabel}>Recipient Phone Number</Text>
              <TextInput
                style={styles.input}
                value={dataPhone}
                onChangeText={setDataPhone}
                placeholder="0241234567"
                keyboardType="phone-pad"
              />
            </View>

            {/* Plan Cards */}
            <View style={{ gap: 12, marginTop: 12 }}>
              {bundlePlans
                .filter((p) => p.network === dataNetwork)
                .map((plan) => (
                  <TouchableOpacity
                    key={plan.id}
                    style={styles.planCard}
                    onPress={() => handleCheckoutData(plan)}
                  >
                    <View style={{ flex: 1 }}>
                      <Text style={styles.planName}>{plan.name}</Text>
                      <View style={styles.planMeta}>
                        <Text style={styles.planVolume}>{plan.volume}</Text>
                        <Text style={styles.planValidity}>• {plan.validity}</Text>
                      </View>
                    </View>
                    <View style={styles.planBuyCol}>
                      <Text style={styles.planPrice}>GH₵ {plan.price.toFixed(2)}</Text>
                      <View style={styles.buyBtn}>
                        <Text style={styles.buyBtnText}>Buy Now</Text>
                      </View>
                    </View>
                  </TouchableOpacity>
                ))}
            </View>
          </View>
        )}

        {/* TAB 4: BILLS */}
        {activeTab === 'bills' && (
          <View style={styles.section}>
            <Text style={styles.screenHeading}>ECG Electricity Bill</Text>
            <Text style={styles.screenSub}>Prepaid top-up & Postpaid bill settlement</Text>

            <View style={styles.formCard}>
              <Text style={styles.inputLabel}>Meter Account Number</Text>
              <TextInput
                style={styles.input}
                value={meterNumber}
                onChangeText={setMeterNumber}
                placeholder="Enter 8-10 digit meter number"
                keyboardType="number-pad"
              />

              <View style={styles.meterTypeRow}>
                <TouchableOpacity
                  style={[styles.meterTypeBtn, meterType === 'PREPAID' && styles.meterTypeBtnActive]}
                  onPress={() => setMeterType('PREPAID')}
                >
                  <Text style={[styles.meterTypeText, meterType === 'PREPAID' && styles.meterTypeTextActive]}>
                    Prepaid Meter
                  </Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.meterTypeBtn, meterType === 'POSTPAID' && styles.meterTypeBtnActive]}
                  onPress={() => setMeterType('POSTPAID')}
                >
                  <Text style={[styles.meterTypeText, meterType === 'POSTPAID' && styles.meterTypeTextActive]}>
                    Postpaid Meter
                  </Text>
                </TouchableOpacity>
              </View>

              <Text style={[styles.inputLabel, { marginTop: 16 }]}>Payment Amount (GH₵)</Text>
              <TextInput
                style={styles.input}
                value={billAmount}
                onChangeText={setBillAmount}
                keyboardType="numeric"
              />

              <TouchableOpacity style={styles.primaryButton} onPress={handleCheckoutBill}>
                <Text style={styles.primaryButtonText}>Pay GH₵ {billAmount} via MoMo</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        {/* TAB 5: HISTORY */}
        {activeTab === 'history' && (
          <View style={styles.section}>
            <Text style={styles.screenHeading}>Transaction History</Text>
            <Text style={styles.screenSub}>Recent orders and official digital receipts</Text>

            <View style={{ gap: 10, marginTop: 12 }}>
              {[
                { ref: 'ORD-18F3B0-A97A', desc: 'MTN 1GB Data Bundle', phone: '0241234567', amt: 12.00, status: 'COMPLETED' },
                { ref: 'ORD-18F3B0-C2B1', desc: 'Telecel Airtime Top-up', phone: '0209876543', amt: 20.00, status: 'COMPLETED' },
                { ref: 'ORD-18F3B0-D4E9', desc: 'ECG Prepaid Electricity', phone: '0241234567', amt: 50.00, status: 'COMPLETED' },
              ].map((item, idx) => (
                <View key={idx} style={styles.historyCard}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.histDesc}>{item.desc}</Text>
                    <Text style={styles.histPhone}>{item.phone} • {item.ref}</Text>
                  </View>
                  <View style={{ alignItems: 'flex-end' }}>
                    <Text style={styles.histAmt}>GH₵ {item.amt.toFixed(2)}</Text>
                    <Text style={styles.histBadge}>{item.status}</Text>
                  </View>
                </View>
              ))}
            </View>
          </View>
        )}
      </ScrollView>

      {/* Bottom Tab Bar */}
      <View style={styles.bottomNav}>
        {[
          { id: 'home', label: 'Home', icon: '🏠' },
          { id: 'airtime', label: 'Airtime', icon: '📱' },
          { id: 'data', label: 'Data', icon: '🌐' },
          { id: 'bills', label: 'Bills', icon: '⚡' },
          { id: 'history', label: 'History', icon: '🧾' },
        ].map((tab) => (
          <TouchableOpacity
            key={tab.id}
            style={styles.navItem}
            onPress={() => setActiveTab(tab.id as any)}
          >
            <Text style={styles.navIcon}>{tab.icon}</Text>
            <Text style={[styles.navLabel, activeTab === tab.id && styles.navLabelActive]}>
              {tab.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Payment Processing & Push Modal */}
      {paymentVisible && (
        <PaymentModal
          visible={paymentVisible}
          order={pendingOrder}
          transactionRef={activeTrxRef}
          token={token}
          onSuccess={(receipt) => {
            setPaymentVisible(false);
            setCompletedReceipt(receipt);
          }}
          onCancel={() => setPaymentVisible(false)}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  topBar: {
    backgroundColor: THEME.colors.primary,
    paddingHorizontal: 20,
    paddingVertical: 14,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  brandRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  logoBadge: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#0F172A',
    justifyContent: 'center',
    alignItems: 'center',
  },
  logoSymbol: {
    color: '#FFCC00',
    fontSize: 20,
    fontWeight: '900',
  },
  appName: {
    fontSize: 16,
    fontWeight: '900',
    color: '#0F172A',
  },
  appSubtitle: {
    fontSize: 11,
    fontWeight: '600',
    color: '#334155',
  },
  statusPill: {
    backgroundColor: 'rgba(15, 23, 42, 0.1)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  statusPillText: {
    fontSize: 10,
    fontWeight: '800',
    color: '#0F172A',
  },
  mainScroll: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 40,
  },
  section: {
    gap: 16,
  },
  walletCard: {
    backgroundColor: '#0F172A',
    borderRadius: 24,
    padding: 24,
    shadowColor: '#000',
    shadowOpacity: 0.12,
    shadowRadius: 10,
    elevation: 4,
  },
  walletLabel: {
    color: '#94A3B8',
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 1,
  },
  walletAmount: {
    color: '#FFFFFF',
    fontSize: 34,
    fontWeight: '900',
    marginVertical: 6,
  },
  walletSub: {
    color: '#CBD5E1',
    fontSize: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#0F172A',
    marginTop: 8,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  actionCard: {
    width: '48%',
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  iconCircle: {
    width: 44,
    height: 44,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  iconEmoji: {
    fontSize: 20,
  },
  actionTitle: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  actionDesc: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 2,
  },
  securityBanner: {
    backgroundColor: '#EFF6FF',
    padding: 16,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#BFDBFE',
    marginTop: 8,
  },
  securityTitle: {
    fontSize: 13,
    fontWeight: '800',
    color: '#1E40AF',
    marginBottom: 4,
  },
  securityBody: {
    fontSize: 12,
    color: '#3B82F6',
    lineHeight: 18,
  },
  screenHeading: {
    fontSize: 22,
    fontWeight: '900',
    color: '#0F172A',
  },
  screenSub: {
    fontSize: 13,
    color: '#64748B',
    marginTop: -8,
    marginBottom: 8,
  },
  formCard: {
    backgroundColor: '#FFFFFF',
    padding: 20,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  inputLabel: {
    fontSize: 12,
    fontWeight: '700',
    color: '#475569',
    marginBottom: 6,
  },
  input: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: 14,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 15,
    fontWeight: '700',
    color: '#0F172A',
  },
  detectedRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginTop: 10,
  },
  detectedLabel: {
    fontSize: 12,
    color: '#64748B',
    fontWeight: '600',
  },
  networkBadge: {
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 8,
  },
  networkBadgeText: {
    fontSize: 11,
    fontWeight: '900',
  },
  amountPills: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginVertical: 12,
  },
  amtPill: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 12,
    backgroundColor: '#F1F5F9',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  amtPillActive: {
    backgroundColor: '#0F172A',
    borderColor: '#0F172A',
  },
  amtPillText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#334155',
  },
  amtPillTextActive: {
    color: '#FFCC00',
  },
  primaryButton: {
    backgroundColor: '#FFCC00',
    paddingVertical: 14,
    borderRadius: 16,
    alignItems: 'center',
    marginTop: 16,
    shadowColor: '#000',
    shadowOpacity: 0.08,
    shadowRadius: 6,
    elevation: 2,
  },
  primaryButtonText: {
    fontSize: 14,
    fontWeight: '900',
    color: '#0F172A',
  },
  tabRow: {
    flexDirection: 'row',
    gap: 8,
  },
  netTab: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    paddingVertical: 10,
    borderRadius: 14,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  netTabActive: {
    backgroundColor: '#0F172A',
    borderColor: '#0F172A',
  },
  netTabText: {
    fontSize: 13,
    fontWeight: '800',
    color: '#475569',
  },
  netTabTextActive: {
    color: '#FFFFFF',
  },
  planCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    flexDirection: 'row',
    alignItems: 'center',
  },
  planName: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  planMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginTop: 4,
  },
  planVolume: {
    fontSize: 13,
    fontWeight: '800',
    color: '#4F46E5',
  },
  planValidity: {
    fontSize: 12,
    color: '#64748B',
  },
  planBuyCol: {
    alignItems: 'flex-end',
    gap: 6,
  },
  planPrice: {
    fontSize: 16,
    fontWeight: '900',
    color: '#0F172A',
  },
  buyBtn: {
    backgroundColor: '#0F172A',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 10,
  },
  buyBtnText: {
    color: '#FFCC00',
    fontSize: 11,
    fontWeight: '800',
  },
  meterTypeRow: {
    flexDirection: 'row',
    gap: 8,
    marginVertical: 12,
  },
  meterTypeBtn: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 12,
    backgroundColor: '#F1F5F9',
    alignItems: 'center',
  },
  meterTypeBtnActive: {
    backgroundColor: '#0F172A',
  },
  meterTypeText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#475569',
  },
  meterTypeTextActive: {
    color: '#FFFFFF',
  },
  historyCard: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  histDesc: {
    fontSize: 14,
    fontWeight: '700',
    color: '#0F172A',
  },
  histPhone: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 2,
  },
  histAmt: {
    fontSize: 15,
    fontWeight: '800',
    color: '#0F172A',
  },
  histBadge: {
    fontSize: 10,
    fontWeight: '800',
    color: '#059669',
    marginTop: 2,
  },
  bottomNav: {
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
    flexDirection: 'row',
    paddingVertical: 8,
    paddingBottom: 16,
  },
  navItem: {
    flex: 1,
    alignItems: 'center',
    gap: 2,
  },
  navIcon: {
    fontSize: 18,
  },
  navLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: '#64748B',
  },
  navLabelActive: {
    color: '#0F172A',
    fontWeight: '900',
  },
});
