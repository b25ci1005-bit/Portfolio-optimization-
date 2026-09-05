import React, { useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

export default function AllocationDonut({ weights = {}, sectorAllocations = {} }) {
  const [viewMode, setViewMode] = useState('assets'); // 'assets' | 'sectors'

  const COLORS = [
    '#3B82F6', '#10B981', '#06B6D4', '#8B5CF6', '#F59E0B',
    '#38BDF8', '#34D399', '#6366F1', '#EC4899', '#F97316',
    '#94A3B8', '#EAB308'
  ];

  const assetData = Object.entries(weights)
    .filter(([_, w]) => w > 0.005)
    .map(([symbol, weight]) => ({
      name: symbol.replace('.NS', ''),
      value: Math.round(weight * 1000) / 10
    }))
    .sort((a, b) => b.value - a.value);

  const sectorData = Object.entries(sectorAllocations)
    .filter(([_, w]) => w > 0.005)
    .map(([sector, weight]) => ({
      name: sector,
      value: Math.round(weight * 1000) / 10
    }))
    .sort((a, b) => b.value - a.value);

  const displayData = viewMode === 'assets' ? assetData : sectorData;

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      return (
        <div className="bg-[#080D18] border border-[#1A263D] p-2.5 rounded-lg shadow-xl text-xs font-mono">
          <div className="text-[#F8FAFC] font-bold">{data.name}</div>
          <div className="text-[#3B82F6] font-medium">{data.value}% allocation</div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-5 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06),0_4px_20px_-2px_rgba(0,0,0,0.5)]">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">Target Allocation</h3>
          <p className="text-[11px] text-[#64748B]">Active weights distribution</p>
        </div>
        <div className="flex items-center gap-1 bg-[#080D18] p-1 rounded-lg border border-[#1A263D]">
          <button
            onClick={() => setViewMode('assets')}
            className={`px-2.5 py-1 text-xs font-medium rounded transition-all ${
              viewMode === 'assets' ? 'bg-[#1A263D] text-white shadow-sm ring-1 ring-white/10' : 'text-[#94A3B8] hover:text-white'
            }`}
          >
            Assets
          </button>
          <button
            onClick={() => setViewMode('sectors')}
            className={`px-2.5 py-1 text-xs font-medium rounded transition-all ${
              viewMode === 'sectors' ? 'bg-[#1A263D] text-white shadow-sm ring-1 ring-white/10' : 'text-[#94A3B8] hover:text-white'
            }`}
          >
            Sectors
          </button>
        </div>
      </div>

      {displayData.length === 0 ? (
        <div className="h-64 flex items-center justify-center text-[#64748B] text-xs font-mono">
          No active allocations to display.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
          {/* Donut Chart */}
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Tooltip content={<CustomTooltip />} />
                <Pie
                  data={displayData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {displayData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Allocation Legend List */}
          <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
            {displayData.map((item, index) => (
              <div key={item.name} className="flex items-center justify-between text-xs font-mono">
                <div className="flex items-center gap-2 truncate pr-2">
                  <span
                    className="w-2 h-2 rounded-full flex-shrink-0 shadow-sm"
                    style={{ backgroundColor: COLORS[index % COLORS.length] }}
                  />
                  <span className="text-[#E2E8F0] truncate">{item.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-16 h-1.5 bg-[#080D18] rounded-full overflow-hidden border border-[#1A263D]/60">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${Math.min(item.value * 2, 100)}%`,
                        backgroundColor: COLORS[index % COLORS.length]
                      }}
                    />
                  </div>
                  <span className="text-[#F8FAFC] font-semibold w-12 text-right tabular-nums">{item.value}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
