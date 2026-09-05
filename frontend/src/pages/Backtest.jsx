import React, { useState } from 'react';
import { Play, TrendingUp, RefreshCw, BarChart2, Shield, AlertTriangle } from 'lucide-react';
import EquityCurveChart from '../components/EquityCurveChart';
import { runWalkForwardBacktest } from '../api';

export default function Backtest() {
  const [lookbackDays, setLookbackDays] = useState(252);
  const [rebalanceDays, setRebalanceDays] = useState(21);
  const [covariance, setCovariance] = useState('ledoit_wolf');
  const [maxAssetWeight, setMaxAssetWeight] = useState(0.25);
  const [includeCosts, setIncludeCosts] = useState(true);

  const [loading, setLoading] = useState(false);
  const [backtestResult, setBacktestResult] = useState(null);
  const [error, setError] = useState(null);

  const handleRunBacktest = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await runWalkForwardBacktest({
        lookback_days: Number(lookbackDays),
        rebalance_days: Number(rebalanceDays),
        covariance,
        max_asset_weight: Number(maxAssetWeight),
        include_costs: includeCosts,
        start_date: '2021-01-01'
      });
      setBacktestResult(res);
    } catch (err) {
      setError(err.message || 'Backtest failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between pb-2 border-b border-[#1C2433]">
        <div className="flex items-center gap-2.5">
          <h1 className="text-base font-semibold text-white tracking-tight">Walk-Forward Backtesting</h1>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#161F30] text-[#64748B] border border-[#1C2433]">
            Out-of-Sample
          </span>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-[#EF4444]/10 border border-[#EF4444]/30 text-[#EF4444] text-xs font-mono">
          {error}
        </div>
      )}

      {/* Control Panel Bar */}
      <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-4 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06),0_4px_20px_-2px_rgba(0,0,0,0.5)]">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 items-end font-mono text-xs">
          <div>
            <label className="text-[10px] font-semibold uppercase tracking-wider text-[#94A3B8] block mb-1 font-sans">
              Lookback Window
            </label>
            <select
              value={lookbackDays}
              onChange={(e) => setLookbackDays(e.target.value)}
              className="w-full bg-[#080D18] border border-[#1A263D] rounded-lg px-2.5 py-2 text-[#F8FAFC] focus:border-[#3B82F6] outline-none"
            >
              <option value="126">126 Days (6M)</option>
              <option value="252">252 Days (1Y)</option>
              <option value="504">504 Days (2Y)</option>
            </select>
          </div>

          <div>
            <label className="text-[10px] font-semibold uppercase tracking-wider text-[#94A3B8] block mb-1 font-sans">
              Rebalance Cycle
            </label>
            <select
              value={rebalanceDays}
              onChange={(e) => setRebalanceDays(e.target.value)}
              className="w-full bg-[#080D18] border border-[#1A263D] rounded-lg px-2.5 py-2 text-[#F8FAFC] focus:border-[#3B82F6] outline-none"
            >
              <option value="10">10 Days</option>
              <option value="21">21 Days (Monthly)</option>
              <option value="63">63 Days (Quarterly)</option>
            </select>
          </div>

          <div>
            <label className="text-[10px] font-semibold uppercase tracking-wider text-[#94A3B8] block mb-1 font-sans">
              Covariance
            </label>
            <select
              value={covariance}
              onChange={(e) => setCovariance(e.target.value)}
              className="w-full bg-[#080D18] border border-[#1A263D] rounded-lg px-2.5 py-2 text-[#F8FAFC] focus:border-[#3B82F6] outline-none"
            >
              <option value="ledoit_wolf">Ledoit-Wolf</option>
              <option value="sample">Sample</option>
              <option value="rmt">RMT Cleaned</option>
              <option value="three_factor">3-Factor</option>
            </select>
          </div>

          <div className="flex items-center gap-2 pb-2">
            <input
              type="checkbox"
              id="costs_toggle"
              checked={includeCosts}
              onChange={(e) => setIncludeCosts(e.target.checked)}
              className="w-4 h-4 rounded border-[#1A263D] accent-[#3B82F6] cursor-pointer"
            />
            <label htmlFor="costs_toggle" className="text-[#F8FAFC] text-xs cursor-pointer select-none">
              Deduct Brokerage & STT
            </label>
          </div>

          <div>
            <button
              onClick={handleRunBacktest}
              disabled={loading}
              className="w-full py-2.5 rounded-lg bg-gradient-to-r from-[#3B82F6] to-[#10B981] hover:from-[#2563EB] hover:to-[#059669] text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-md shadow-blue-500/20 hover:shadow-emerald-500/20 transition-all disabled:opacity-50"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Simulating...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Run Walk-Forward</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Chart Section */}
      <EquityCurveChart backtestData={backtestResult} />

      {/* Performance Scorecard */}
      {backtestResult && backtestResult.metrics && (
        <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl overflow-hidden shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06),0_4px_20px_-2px_rgba(0,0,0,0.5)]">
          <div className="px-4 py-3 border-b border-[#1A263D] flex items-center justify-between">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">
              Strategy Comparison & Risk Metrics
            </h3>
            <span className="text-[11px] font-mono text-[#64748B]">
              {backtestResult.total_trading_days} Days Out-of-Sample (Rf: 6.5%)
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-[#080D18] text-[#94A3B8] uppercase border-b border-[#1A263D] text-[10px]">
                <tr>
                  <th className="py-2.5 px-4 font-medium">Strategy</th>
                  <th className="py-2.5 px-4 text-right font-medium">CAGR</th>
                  <th className="py-2.5 px-4 text-right font-medium">Annual Vol</th>
                  <th className="py-2.5 px-4 text-right font-medium">Sharpe</th>
                  <th className="py-2.5 px-4 text-right font-medium">Sortino</th>
                  <th className="py-2.5 px-4 text-right font-medium">Calmar</th>
                  <th className="py-2.5 px-4 text-right font-medium">Max DD</th>
                  <th className="py-2.5 px-4 text-right font-medium">Return</th>
                  <th className="py-2.5 px-4 text-right font-medium">Win Rate</th>
                  <th className="py-2.5 px-4 text-right font-medium">Turnover</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1A263D]/60">
                {Object.entries(backtestResult.metrics).map(([strat, m]) => {
                  const isBenchmark = strat.includes('Benchmark');
                  const isHighSharpe = m.sharpe_ratio >= 1.0;
                  return (
                    <tr
                      key={strat}
                      className={`hover:bg-[#121B2F]/50 transition-colors ${
                        isBenchmark ? 'bg-[#080D18]/50' : ''
                      }`}
                    >
                      <td className="py-2.5 px-4 font-semibold text-[#F8FAFC] flex items-center gap-2">
                        <span>{strat}</span>
                        {isBenchmark && (
                          <span className="text-[9px] uppercase font-mono px-1 py-0.2 rounded bg-[#121B2F] text-[#94A3B8] border border-[#1A263D]">
                            Benchmark
                          </span>
                        )}
                      </td>
                      <td className={`py-2.5 px-4 text-right tabular-nums font-semibold ${m.cagr >= 0 ? 'text-[#10B981]' : 'text-[#F43F5E]'}`}>
                        {m.cagr >= 0 ? '+' : ''}{m.cagr}%
                      </td>
                      <td className="py-2.5 px-4 text-right tabular-nums text-[#F8FAFC]">
                        {m.annual_volatility}%
                      </td>
                      <td className={`py-2.5 px-4 text-right tabular-nums font-semibold ${isHighSharpe ? 'text-[#3B82F6]' : 'text-[#F8FAFC]'}`}>
                        {m.sharpe_ratio}
                      </td>
                      <td className="py-2.5 px-4 text-right tabular-nums text-[#F8FAFC]">
                        {m.sortino_ratio}
                      </td>
                      <td className="py-2.5 px-4 text-right tabular-nums text-[#F8FAFC]">
                        {m.calmar_ratio}
                      </td>
                      <td className="py-2.5 px-4 text-right tabular-nums text-[#F43F5E]">
                        -{m.max_drawdown}%
                      </td>
                      <td className={`py-2.5 px-4 text-right tabular-nums ${m.cumulative_return >= 0 ? 'text-[#10B981]' : 'text-[#F43F5E]'}`}>
                        {m.cumulative_return >= 0 ? '+' : ''}{m.cumulative_return}%
                      </td>
                      <td className="py-2.5 px-4 text-right tabular-nums text-[#94A3B8]">
                        {m.win_rate}%
                      </td>
                      <td className="py-2.5 px-4 text-right tabular-nums text-[#64748B]">
                        {m.turnover}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
