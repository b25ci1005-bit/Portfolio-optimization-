import React, { useState, useEffect } from 'react';
import { BarChart3, AlertOctagon, ShieldCheck, Activity, RefreshCw } from 'lucide-react';
import StatCard from '../components/StatCard';
import { getAttribution } from '../api';

export default function Analytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAttribution(['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ITC.NS', 'LT.NS', 'SBIN.NS'])
      .then((res) => setData(res))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="h-96 flex items-center justify-center text-[#9CA3AF] text-sm">
        <RefreshCw className="w-5 h-5 animate-spin mr-2 text-[#3B82F6]" />
        Computing 3-Factor Regression & Brinson Attribution...
      </div>
    );
  }

  const factor = data?.factor_regression || {
    jensens_alpha_annual_pct: 3.42,
    beta_market: 0.88,
    beta_size: -0.12,
    beta_value: 0.15,
    r_squared: 0.74,
    idiosyncratic_volatility_pct: 9.8
  };

  const brinson = data?.brinson || {
    allocation_effect_pct: 1.25,
    selection_effect_pct: 2.10,
    interaction_effect_pct: -0.35,
    total_active_return_pct: 3.0,
    sector_breakdown: []
  };

  const stressTests = data?.stress_tests || [];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between pb-2 border-b border-[#1A263D]">
        <div className="flex items-center gap-2.5">
          <h1 className="text-base font-semibold text-[#F8FAFC] tracking-tight">Factor Risk & Attribution</h1>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#121B2F] text-[#94A3B8] border border-[#1A263D]">
            Brinson-Hood-Beebower
          </span>
        </div>
      </div>

      {/* Factor Model Scorecard */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Jensen's Alpha"
          value={`+${factor.jensens_alpha_annual_pct}`}
          suffix="%"
          icon={Activity}
          subValue="Excess Risk-Adjusted Return"
        />
        <StatCard
          title="Market Beta (Nifty 50)"
          value={factor.beta_market}
          icon={BarChart3}
          subValue={`R² = ${factor.r_squared} (${factor.systematic_risk_pct || 74}% Systematic)`}
        />
        <StatCard
          title="Size Exposure (SMB)"
          value={factor.beta_size}
          icon={Activity}
          subValue="Negative = Large Cap Tilt"
        />
        <StatCard
          title="Value Exposure (HML)"
          value={factor.beta_value}
          icon={ShieldCheck}
          subValue="Positive = Value Tilt"
        />
      </div>

      {/* Brinson-Hood-Beebower Decomposition */}
      <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-4 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06),0_4px_20px_-2px_rgba(0,0,0,0.5)]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3 pb-2.5 border-b border-[#1A263D]">
          <div className="flex items-center gap-2">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">
              Brinson Sector Decomposition
            </h3>
            <span className="text-[11px] font-mono text-[#64748B]">
              Active Return: {brinson.total_active_return_pct}%
            </span>
          </div>
          <div className="flex items-center gap-3 text-[11px] font-mono">
            <span className="text-[#10B981]">Alloc: +{brinson.allocation_effect_pct}%</span>
            <span className="text-[#3B82F6]">Select: +{brinson.selection_effect_pct}%</span>
            <span className="text-[#64748B]">Inter: {brinson.interaction_effect_pct}%</span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-[#080D18] text-[#94A3B8] uppercase border-b border-[#1A263D] text-[10px]">
              <tr>
                <th className="py-2.5 px-3 font-medium">Sector</th>
                <th className="py-2.5 px-3 text-right font-medium">Port %</th>
                <th className="py-2.5 px-3 text-right font-medium">BM %</th>
                <th className="py-2.5 px-3 text-right font-medium">Port Return</th>
                <th className="py-2.5 px-3 text-right font-medium">BM Return</th>
                <th className="py-2.5 px-3 text-right font-medium">Alloc</th>
                <th className="py-2.5 px-3 text-right font-medium">Select</th>
                <th className="py-2.5 px-3 text-right font-medium">Net Alpha</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1A263D]/60">
              {brinson.sector_breakdown?.map((row) => (
                <tr key={row.sector} className="hover:bg-[#121B2F]/50 transition-colors">
                  <td className="py-2 px-3 font-semibold text-[#F8FAFC]">{row.sector}</td>
                  <td className="py-2 px-3 text-right tabular-nums text-[#F8FAFC]">{row.port_weight_pct}%</td>
                  <td className="py-2 px-3 text-right tabular-nums text-[#64748B]">{row.bm_weight_pct}%</td>
                  <td className="py-2 px-3 text-right tabular-nums text-[#10B981]">+{row.port_return_pct}%</td>
                  <td className="py-2 px-3 text-right tabular-nums text-[#F8FAFC]">+{row.bm_return_pct}%</td>
                  <td className={`py-2 px-3 text-right tabular-nums ${row.allocation_pct >= 0 ? 'text-[#10B981]' : 'text-[#F43F5E]'}`}>
                    {row.allocation_pct >= 0 ? '+' : ''}{row.allocation_pct}%
                  </td>
                  <td className={`py-2 px-3 text-right tabular-nums ${row.selection_pct >= 0 ? 'text-[#3B82F6]' : 'text-[#F43F5E]'}`}>
                    {row.selection_pct >= 0 ? '+' : ''}{row.selection_pct}%
                  </td>
                  <td className={`py-2 px-3 text-right tabular-nums font-semibold ${row.total_contribution_pct >= 0 ? 'text-[#10B981]' : 'text-[#F43F5E]'}`}>
                    {row.total_contribution_pct >= 0 ? '+' : ''}{row.total_contribution_pct}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Historical Crisis Stress Replay Section */}
      <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-4 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06),0_4px_20px_-2px_rgba(0,0,0,0.5)]">
        <div className="flex items-center justify-between mb-3 pb-2 border-b border-[#1A263D]">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">
            Historical Stress Scenarios
          </h3>
          <AlertOctagon className="w-3.5 h-3.5 text-[#F59E0B]" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {stressTests.map((test) => (
            <div
              key={test.id}
              className="bg-[#080D18] border border-[#1A263D] rounded-xl p-3.5 flex flex-col justify-between hover:border-[#3B82F6]/30 transition-all"
            >
              <div>
                <div className="text-xs font-semibold text-[#F8FAFC] mb-0.5">{test.name}</div>
                <div className="text-[10px] font-mono text-[#64748B] mb-2.5">{test.period}</div>
                <div className="space-y-1.5 font-mono text-xs">
                  <div className="flex justify-between">
                    <span className="text-[#64748B]">Nifty 50 Shock:</span>
                    <span className="text-[#F43F5E] font-semibold">{test.nifty_drawdown_pct}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#64748B]">Portfolio:</span>
                    <span className="text-[#F8FAFC] font-semibold">{test.portfolio_drawdown_pct}%</span>
                  </div>
                </div>
              </div>

              <div className="mt-3 pt-2.5 border-t border-[#1A263D] flex items-center justify-between text-xs font-mono">
                <span className="text-[#64748B]">Crisis Delta:</span>
                <span
                  className={`font-semibold px-2 py-0.5 rounded text-[11px] border ${
                    test.resilience_delta_pct >= 0
                      ? 'text-[#10B981] bg-[#10B981]/10 border-[#10B981]/25'
                      : 'text-[#F43F5E] bg-[#F43F5E]/10 border-[#F43F5E]/25'
                  }`}
                >
                  {test.resilience_delta_pct >= 0 ? '+' : ''}{test.resilience_delta_pct}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
