import React, { useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  AreaChart,
  Area
} from 'recharts';

export default function EquityCurveChart({ backtestData }) {
  const [showUnderwater, setShowUnderwater] = useState(false);

  if (!backtestData || !backtestData.equity_curves) {
    return (
      <div className="h-80 flex items-center justify-center text-[#94A3B8] text-xs font-mono border border-[#1A263D] rounded-xl bg-[#0D1322] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06)]">
        Run Walk-Forward backtest to generate comparative multi-strategy equity curves.
      </div>
    );
  }

  const { dates, equity_curves, drawdowns } = backtestData;

  // Format data into Recharts friendly structure
  const chartData = dates.map((date, idx) => {
    const item = { date };
    Object.keys(equity_curves).forEach((strat) => {
      item[strat] = equity_curves[strat][idx];
      if (drawdowns && drawdowns[strat]) {
        item[`${strat}_dd`] = drawdowns[strat][idx];
      }
    });
    return item;
  });

  const colors = {
    'Maximum Sharpe': '#3B82F6',
    'Minimum Variance': '#10B981',
    'Risk Parity': '#06B6D4',
    'Hierarchical Risk Parity': '#8B5CF6',
    'Black-Litterman': '#F59E0B',
    'Equal Weight': '#38BDF8',
    'Nifty 50 Benchmark': '#64748B'
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#080D18] border border-[#1A263D] p-3 rounded-lg shadow-2xl text-xs font-mono">
          <div className="text-[#F8FAFC] font-bold mb-2 pb-1 border-b border-[#1A263D]">{label}</div>
          <div className="space-y-1">
            {payload.map((entry, index) => (
              <div key={index} className="flex items-center justify-between gap-4">
                <span style={{ color: entry.color }}>{entry.name}:</span>
                <span className="text-[#F8FAFC] font-semibold tabular-nums">
                  {showUnderwater ? `${entry.value}%` : `₹${Number(entry.value).toLocaleString('en-IN')}`}
                </span>
              </div>
            ))}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-5 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06),0_4px_20px_-2px_rgba(0,0,0,0.5)]">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">
            {showUnderwater ? 'Underwater Drawdown History (%)' : 'Walk-Forward Equity Curves (Initial ₹10,00,000)'}
          </h3>
          <p className="text-[11px] text-[#64748B]">Point-in-time walk-forward evaluation including Indian fees & slippage</p>
        </div>
        <div className="flex items-center gap-1 bg-[#080D18] p-1 rounded-lg border border-[#1A263D]">
          <button
            onClick={() => setShowUnderwater(false)}
            className={`px-2.5 py-1 text-xs font-medium rounded transition-all ${
              !showUnderwater ? 'bg-[#1A263D] text-white shadow-sm ring-1 ring-white/10' : 'text-[#94A3B8] hover:text-white'
            }`}
          >
            NAV Curves
          </button>
          <button
            onClick={() => setShowUnderwater(true)}
            className={`px-2.5 py-1 text-xs font-medium rounded transition-all ${
              showUnderwater ? 'bg-[#1A263D] text-white shadow-sm ring-1 ring-white/10' : 'text-[#94A3B8] hover:text-white'
            }`}
          >
            Drawdowns
          </button>
        </div>
      </div>

      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          {showUnderwater ? (
            <AreaChart data={chartData} margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
              <CartesianGrid stroke="#1A263D" strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                stroke="#94A3B8"
                tick={{ fontSize: 10, fill: '#94A3B8', fontFamily: 'monospace' }}
              />
              <YAxis
                stroke="#94A3B8"
                tick={{ fontSize: 10, fill: '#94A3B8', fontFamily: 'monospace' }}
                unit="%"
                domain={['auto', 0]}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              {Object.keys(equity_curves).map((strat) => (
                <Area
                  key={strat}
                  type="monotone"
                  dataKey={`${strat}_dd`}
                  name={strat}
                  stroke={colors[strat] || '#94A3B8'}
                  fill={colors[strat] || '#94A3B8'}
                  fillOpacity={0.15}
                  strokeWidth={1.5}
                />
              ))}
            </AreaChart>
          ) : (
            <LineChart data={chartData} margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
              <CartesianGrid stroke="#1A263D" strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                stroke="#94A3B8"
                tick={{ fontSize: 10, fill: '#94A3B8', fontFamily: 'monospace' }}
              />
              <YAxis
                stroke="#94A3B8"
                tick={{ fontSize: 10, fill: '#94A3B8', fontFamily: 'monospace' }}
                tickFormatter={(v) => `₹${(v / 100000).toFixed(1)}L`}
                domain={['auto', 'auto']}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              {Object.keys(equity_curves).map((strat) => (
                <Line
                  key={strat}
                  type="monotone"
                  dataKey={strat}
                  name={strat}
                  stroke={colors[strat] || '#94A3B8'}
                  strokeWidth={strat === 'Maximum Sharpe' || strat === 'Hierarchical Risk Parity' ? 2.5 : 1.5}
                  strokeDasharray={strat === 'Nifty 50 Benchmark' ? '5 5' : undefined}
                  dot={false}
                />
              ))}
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
