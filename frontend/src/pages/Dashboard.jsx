import React, { useState, useEffect } from 'react';
import {
  Wallet,
  TrendingUp,
  Percent,
  Layers,
  RotateCcw,
  ArrowRight,
  RefreshCw,
  PlusCircle,
  Clock,
  CheckCircle,
  FileText
} from 'lucide-react';
import StatCard from '../components/StatCard';
import PositionsTable from '../components/PositionsTable';
import AllocationDonut from '../components/AllocationDonut';
import OrderModal from '../components/OrderModal';
import { getPortfolioState, resetPortfolio } from '../api';

export default function Dashboard({ setActiveTab, upstoxStatus }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState('RELIANCE.NS');

  const loadState = async () => {
    try {
      const res = await getPortfolioState();
      setData(res);
    } catch (err) {
      console.error('Failed to load portfolio state:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadState();
    const interval = setInterval(loadState, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleReset = async () => {
    if (window.confirm('Reset virtual paper trading ledger back to initial ₹10,00,000 cash?')) {
      await resetPortfolio();
      loadState();
    }
  };

  const portfolio = data?.portfolio || {
    nav: 1000000,
    cash: 1000000,
    invested_value: 0,
    total_pnl: 0,
    total_pnl_pct: 0,
    holdings: []
  };

  // Convert holdings to weights dictionary for donut
  const weights = {};
  if (portfolio.holdings && portfolio.nav > 0) {
    portfolio.holdings.forEach((h) => {
      weights[h.symbol] = h.weight;
    });
    if (portfolio.cash > 0) {
      weights['CASH'] = portfolio.cash / portfolio.nav;
    }
  }

  return (
    <div className="space-y-6">
      {/* Top Header Bar */}
      <div className="flex items-center justify-between pb-2 border-b border-[#1A263D]">
        <div className="flex items-center gap-2.5">
          <h1 className="text-base font-semibold text-[#F8FAFC] tracking-tight">Portfolio Overview</h1>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#121B2F] text-[#94A3B8] border border-[#1A263D]">
            {data?.execution_mode || 'PAPER MODE'}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => { setRefreshing(true); loadState(); }}
            className="p-1.5 rounded-lg bg-[#0D1322] hover:bg-[#121B2F] text-[#94A3B8] hover:text-white border border-[#1A263D] transition-colors"
            title="Refresh Quotes"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin text-[#3B82F6]' : ''}`} />
          </button>
          <button
            onClick={() => { setSelectedSymbol('RELIANCE.NS'); setModalOpen(true); }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-[#3B82F6] to-[#10B981] hover:from-[#2563EB] hover:to-[#059669] text-white text-xs font-semibold shadow-md shadow-blue-500/20 hover:shadow-emerald-500/20 transition-all"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>New Order</span>
          </button>
          <button
            onClick={handleReset}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-[#0D1322] hover:bg-[#121B2F] text-[#94A3B8] hover:text-[#F43F5E] text-xs font-medium border border-[#1A263D] transition-colors"
            title="Reset to ₹10L Cash"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
        </div>
      </div>

      {/* Hero Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Portfolio NAV"
          value={portfolio.nav.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          prefix="₹"
          change={portfolio.total_pnl_pct}
          isPositive={portfolio.total_pnl >= 0}
          icon={Wallet}
          subValue={`Base: ₹${(portfolio.initial_capital || 1000000).toLocaleString('en-IN')}`}
        />
        <StatCard
          title="Unrealized P&L"
          value={Math.abs(portfolio.total_pnl).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          prefix={portfolio.total_pnl >= 0 ? '+₹' : '-₹'}
          change={portfolio.total_pnl_pct}
          isPositive={portfolio.total_pnl >= 0}
          icon={TrendingUp}
          subValue="Mark-to-Market"
        />
        <StatCard
          title="Invested Equity"
          value={portfolio.invested_value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          prefix="₹"
          icon={Layers}
          subValue={`${portfolio.holdings?.length || 0} Holdings`}
        />
        <StatCard
          title="Free Cash Reserve"
          value={portfolio.cash.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          prefix="₹"
          icon={Percent}
          subValue={`${((portfolio.cash / (portfolio.nav || 1)) * 100).toFixed(1)}% Allocation`}
        />
      </div>

      {/* Main Grid: Positions (8 cols) & Allocation (4 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8">
          <PositionsTable
            holdings={portfolio.holdings}
            onTradeClick={(sym) => { setSelectedSymbol(sym); setModalOpen(true); }}
          />
        </div>

        <div className="lg:col-span-4">
          <AllocationDonut
            weights={weights}
            sectorAllocations={portfolio.sector_allocations}
          />
        </div>
      </div>

      {/* Recent Orders Execution Ledger */}
      <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl overflow-hidden shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06),0_4px_20px_-2px_rgba(0,0,0,0.5)]">
        <div className="px-4 py-3 border-b border-[#1A263D] flex items-center justify-between">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">Execution Ledger</h3>
          <span className="text-[11px] font-mono text-[#64748B]">
            {data?.recent_orders?.length || 0} Orders
          </span>
        </div>

        {data?.recent_orders && data.recent_orders.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-[#080D18] text-[#94A3B8] uppercase tracking-wider border-b border-[#1A263D] text-[10px]">
                <tr>
                  <th className="py-2.5 px-4 font-medium">Time</th>
                  <th className="py-2.5 px-4 font-medium">Instrument</th>
                  <th className="py-2.5 px-4 font-medium">Side</th>
                  <th className="py-2.5 px-4 text-right font-medium">Qty</th>
                  <th className="py-2.5 px-4 text-right font-medium">LTP (₹)</th>
                  <th className="py-2.5 px-4 text-right font-medium">Fill (₹)</th>
                  <th className="py-2.5 px-4 text-right font-medium">Slippage</th>
                  <th className="py-2.5 px-4 text-right font-medium">Fees (₹)</th>
                  <th className="py-2.5 px-4 text-center font-medium">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1A263D]/60">
                {data.recent_orders.map((ord) => (
                  <tr key={ord.id} className="hover:bg-[#121B2F]/50 transition-colors">
                    <td className="py-2.5 px-4 text-[#64748B] text-[11px]">
                      {ord.executed_at ? new Date(ord.executed_at).toLocaleTimeString() : '-'}
                    </td>
                    <td className="py-2.5 px-4 font-semibold text-[#F8FAFC]">
                      {ord.symbol.replace('.NS', '')}
                    </td>
                    <td className="py-2.5 px-4">
                      <span
                        className={`inline-flex px-1.5 py-0.5 rounded text-[10px] font-bold border ${
                          ord.order_type === 'BUY'
                            ? 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]/25'
                            : 'bg-[#F43F5E]/10 text-[#F43F5E] border-[#F43F5E]/25'
                        }`}
                      >
                        {ord.order_type}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-right tabular-nums text-[#F8FAFC]">
                      {ord.shares}
                    </td>
                    <td className="py-2.5 px-4 text-right tabular-nums text-[#94A3B8]">
                      ₹{ord.price?.toLocaleString('en-IN', { maximumFractionDigits: 1 })}
                    </td>
                    <td className="py-2.5 px-4 text-right tabular-nums font-semibold text-[#F8FAFC]">
                      ₹{ord.fill_price?.toLocaleString('en-IN', { maximumFractionDigits: 1 })}
                    </td>
                    <td className="py-2.5 px-4 text-right tabular-nums text-[#64748B]">
                      {ord.slippage_pct ? `${ord.slippage_pct}%` : '0%'}
                    </td>
                    <td className="py-2.5 px-4 text-right tabular-nums text-[#64748B]">
                      ₹{ord.fees?.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                    </td>
                    <td className="py-2.5 px-4 text-center">
                      <span className="inline-flex items-center gap-1 text-[11px] text-[#10B981] font-medium">
                        <CheckCircle className="w-3 h-3" />
                        <span>Filled</span>
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-6 text-center text-[#64748B] text-xs font-mono">
            No executed orders in current ledger session.
          </div>
        )}
      </div>

      {/* Manual Order Modal */}
      <OrderModal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); loadState(); }}
        defaultSymbol={selectedSymbol}
      />
    </div>
  );
}

