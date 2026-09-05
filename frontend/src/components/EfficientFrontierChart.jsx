import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ReferenceDot
} from 'recharts';

export default function EfficientFrontierChart({ frontierData }) {
  if (!frontierData || !frontierData.frontier_curve) {
    return (
      <div className="h-80 flex items-center justify-center text-[#9CA3AF] text-sm border border-[#262C3A] rounded-xl bg-[#151922]">
        Run optimization to plot the Efficient Frontier.
      </div>
    );
  }

  const {
    frontier_curve,
    capital_allocation_line,
    minimum_variance_portfolio,
    tangency_portfolio,
    individual_assets,
    risk_free_rate
  } = frontierData;

  // Custom institutional tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-[#0B0E14] border border-[#262C3A] p-3 rounded-lg shadow-xl text-xs font-mono">
          {data.symbol && <div className="text-white font-bold mb-1">{data.symbol}</div>}
          <div className="text-[#9CA3AF]">Volatility (Risk): <span className="text-white font-bold">{data.volatility}%</span></div>
          <div className="text-[#9CA3AF]">Expected Return: <span className="text-[#10B981] font-bold">{data.expected_return}%</span></div>
          {data.sharpe !== undefined && (
            <div className="text-[#9CA3AF]">Sharpe Ratio: <span className="text-[#3B82F6] font-bold">{data.sharpe}</span></div>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-[#151922] border border-[#262C3A] rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-white tracking-wide">Markowitz Efficient Frontier & CAL</h3>
          <p className="text-xs text-[#9CA3AF]">Convex frontier generated with risk-free rate Rf = {risk_free_rate}%</p>
        </div>
        <div className="flex items-center gap-3 text-xs font-mono">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]" />
            <span className="text-[#9CA3AF]">Min Var ({minimum_variance_portfolio?.volatility}%)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#3B82F6]" />
            <span className="text-[#9CA3AF]">Tangency ({tangency_portfolio?.volatility}%)</span>
          </div>
        </div>
      </div>

      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
            <CartesianGrid stroke="#262C3A" strokeDasharray="3 3" />
            <XAxis
              type="number"
              dataKey="volatility"
              name="Volatility (%)"
              stroke="#9CA3AF"
              tick={{ fontSize: 11, fill: '#9CA3AF', fontFamily: 'monospace' }}
              domain={['auto', 'auto']}
              unit="%"
            />
            <YAxis
              type="number"
              dataKey="expected_return"
              name="Return (%)"
              stroke="#9CA3AF"
              tick={{ fontSize: 11, fill: '#9CA3AF', fontFamily: 'monospace' }}
              domain={['auto', 'auto']}
              unit="%"
            />
            <Tooltip content={<CustomTooltip />} />

            {/* Capital Allocation Line */}
            <Line
              data={capital_allocation_line}
              dataKey="expected_return"
              stroke="#3B82F6"
              strokeWidth={1.5}
              strokeDasharray="4 4"
              dot={false}
              name="Capital Allocation Line"
            />

            {/* Efficient Frontier Curve */}
            <Line
              data={frontier_curve}
              dataKey="expected_return"
              stroke="#10B981"
              strokeWidth={2.5}
              dot={false}
              name="Efficient Frontier"
            />

            {/* Individual Assets */}
            <Scatter
              data={individual_assets}
              dataKey="expected_return"
              fill="#F59E0B"
              name="NSE Assets"
            />

            {/* Minimum Variance Dot */}
            {minimum_variance_portfolio && (
              <ReferenceDot
                x={minimum_variance_portfolio.volatility}
                y={minimum_variance_portfolio.expected_return}
                r={6}
                fill="#10B981"
                stroke="#ffffff"
                strokeWidth={2}
              />
            )}

            {/* Tangency Portfolio Dot */}
            {tangency_portfolio && (
              <ReferenceDot
                x={tangency_portfolio.volatility}
                y={tangency_portfolio.expected_return}
                r={6}
                fill="#3B82F6"
                stroke="#ffffff"
                strokeWidth={2}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
