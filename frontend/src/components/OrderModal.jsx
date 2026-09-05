import React, { useState } from 'react';
import { X, AlertCircle, CheckCircle2 } from 'lucide-react';
import { placeManualOrder } from '../api';

export default function OrderModal({ isOpen, onClose, defaultSymbol = 'RELIANCE.NS', onOrderSuccess }) {
  const [symbol, setSymbol] = useState(defaultSymbol);
  const [orderType, setOrderType] = useState('BUY');
  const [shares, setShares] = useState(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const res = await placeManualOrder({
        symbol,
        order_type: orderType,
        shares: Number(shares)
      });
      if (res.status === 'FILLED') {
        setSuccessMsg(`Filled ${shares} shares of ${symbol} at ₹${res.fill_price}. Indian Fees: ₹${res.fees?.total_fees}`);
        if (onOrderSuccess) onOrderSuccess();
        setTimeout(() => {
          onClose();
        }, 1500);
      } else {
        setError(res.reason || 'Order execution failed');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-[#0D1322] border border-[#1A263D] rounded-2xl w-full max-w-md p-6 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.08),0_20px_50px_rgba(0,0,0,0.8)]">
        <div className="flex items-center justify-between pb-4 border-b border-[#1A263D]">
          <div>
            <h3 className="font-semibold text-[#F8FAFC] text-base">Execute Paper Order</h3>
            <p className="text-xs text-[#94A3B8]">Simulated trade with live Indian microstructure costs</p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-[#121B2F] text-[#94A3B8] hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 mt-4 font-mono text-xs">
          {error && (
            <div className="p-3 rounded-lg bg-[#EF4444]/10 border border-[#EF4444]/30 text-[#EF4444] flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {successMsg && (
            <div className="p-3 rounded-lg bg-[#10B981]/10 border border-[#10B981]/30 text-[#10B981] flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          <div>
            <label className="block text-[#94A3B8] uppercase mb-1">Instrument</label>
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              className="w-full bg-[#080D18] border border-[#1A263D] rounded-lg px-3 py-2 text-[#F8FAFC] font-semibold focus:border-[#3B82F6] outline-none"
              placeholder="e.g. RELIANCE.NS"
              required
            />
          </div>

          <div>
            <label className="block text-[#94A3B8] uppercase mb-1">Side</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setOrderType('BUY')}
                className={`py-2 rounded-lg font-semibold transition-all ${
                  orderType === 'BUY'
                    ? 'bg-[#10B981] text-white shadow-md shadow-emerald-500/30'
                    : 'bg-[#080D18] text-[#94A3B8] border border-[#1A263D] hover:text-white'
                }`}
              >
                BUY / DELIV
              </button>
              <button
                type="button"
                onClick={() => setOrderType('SELL')}
                className={`py-2 rounded-lg font-semibold transition-all ${
                  orderType === 'SELL'
                    ? 'bg-[#F43F5E] text-white shadow-md shadow-rose-500/30'
                    : 'bg-[#080D18] text-[#94A3B8] border border-[#1A263D] hover:text-white'
                }`}
              >
                SELL / DELIV
              </button>
            </div>
          </div>

          <div>
            <label className="block text-[#94A3B8] uppercase mb-1">Quantity (Shares)</label>
            <input
              type="number"
              min="1"
              step="1"
              value={shares}
              onChange={(e) => setShares(e.target.value)}
              className="w-full bg-[#080D18] border border-[#1A263D] rounded-lg px-3 py-2 text-[#F8FAFC] font-semibold focus:border-[#3B82F6] outline-none"
              required
            />
          </div>

          <div className="bg-[#080D18] p-3 rounded-lg border border-[#1A263D] text-[11px] text-[#94A3B8] space-y-1">
            <div className="flex justify-between">
              <span>Brokerage Cap:</span>
              <span className="text-[#F8FAFC]">min(0.03%, ₹20)</span>
            </div>
            <div className="flex justify-between">
              <span>STT (Delivery):</span>
              <span className="text-[#F8FAFC]">{orderType === 'SELL' ? '0.1% on sell' : '₹0.00'}</span>
            </div>
            <div className="flex justify-between">
              <span>Market Impact Slippage:</span>
              <span className="text-[#F8FAFC]">Square-root ADV model</span>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-[#080D18] hover:bg-[#121B2F] text-[#94A3B8] hover:text-white border border-[#1A263D] transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 rounded-lg bg-gradient-to-r from-[#3B82F6] to-[#10B981] hover:from-[#2563EB] hover:to-[#059669] text-white font-semibold shadow-md shadow-blue-500/20 hover:shadow-emerald-500/20 transition-all disabled:opacity-50"
            >
              {loading ? 'Executing...' : 'Submit Order'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
