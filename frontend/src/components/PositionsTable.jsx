import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

export default function PositionsTable({ holdings = [], onTradeClick }) {
  if (!holdings || holdings.length === 0) {
    return (
      <div className="bg-[#0F141E] border border-[#1C2433] rounded-xl p-8 text-center">
        <p className="text-[#94A3B8] text-xs font-medium">No open positions in portfolio.</p>
        <p className="text-[11px] text-[#64748B] mt-1 font-mono">Deploy an optimizer target allocation or submit an order to initialize positions.</p>
      </div>
    );
  }

  return (
    <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl overflow-hidden shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06),0_4px_20px_-2px_rgba(0,0,0,0.5)]">
      <div className="px-4 py-3 border-b border-[#1A263D] flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">Open Positions</h3>
        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#121B2F] text-[#94A3B8] border border-[#1A263D]">
          {holdings.length} Assets
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead className="bg-[#080D18] text-[#94A3B8] uppercase tracking-wider border-b border-[#1A263D] text-[10px]">
            <tr>
              <th className="py-2.5 px-4 font-medium">Instrument</th>
              <th className="py-2.5 px-4 text-right font-medium">Qty</th>
              <th className="py-2.5 px-4 text-right font-medium">Avg (₹)</th>
              <th className="py-2.5 px-4 text-right font-medium">LTP (₹)</th>
              <th className="py-2.5 px-4 text-right font-medium">Value (₹)</th>
              <th className="py-2.5 px-4 text-right font-medium">P&L</th>
              <th className="py-2.5 px-4 text-right font-medium">Weight</th>
              <th className="py-2.5 px-4 text-center font-medium">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1A263D]/60">
            {holdings.map((pos) => {
              const isProfit = pos.unrealized_pnl >= 0;
              return (
                <tr key={pos.symbol} className="hover:bg-[#121B2F]/50 transition-colors">
                  <td className="py-2.5 px-4 font-semibold text-[#F8FAFC] flex items-center gap-2">
                    <span>{pos.symbol.replace('.NS', '')}</span>
                    <span className="text-[9px] px-1 py-0.2 rounded bg-[#121B2F] text-[#94A3B8] border border-[#1A263D]">NSE</span>
                  </td>
                  <td className="py-2.5 px-4 text-right tabular-nums text-[#E2E8F0]">
                    {pos.shares}
                  </td>
                  <td className="py-2.5 px-4 text-right tabular-nums text-[#94A3B8]">
                    ₹{pos.avg_price?.toLocaleString('en-IN', { maximumFractionDigits: 1 })}
                  </td>
                  <td className="py-2.5 px-4 text-right tabular-nums font-semibold text-[#F8FAFC]">
                    ₹{pos.current_price?.toLocaleString('en-IN', { maximumFractionDigits: 1 })}
                  </td>
                  <td className="py-2.5 px-4 text-right tabular-nums text-[#F8FAFC]">
                    ₹{pos.market_value?.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                  </td>
                  <td className="py-2.5 px-4 text-right tabular-nums">
                    <span
                      className={`inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[11px] font-semibold border ${
                        isProfit 
                          ? 'text-[#10B981] bg-[#10B981]/10 border-[#10B981]/25' 
                          : 'text-[#F43F5E] bg-[#F43F5E]/10 border-[#F43F5E]/25'
                      }`}
                    >
                      {isProfit ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                      ₹{Math.abs(pos.unrealized_pnl).toLocaleString('en-IN', { maximumFractionDigits: 0 })} ({pos.unrealized_pnl_pct}%)
                    </span>
                  </td>
                  <td className="py-2.5 px-4 text-right tabular-nums text-[#94A3B8]">
                    {(pos.weight * 100).toFixed(1)}%
                  </td>
                  <td className="py-2.5 px-4 text-center">
                    <button
                      onClick={() => onTradeClick && onTradeClick(pos.symbol)}
                      className="px-2.5 py-1 rounded bg-[#121B2F] hover:bg-[#3B82F6] text-[#94A3B8] hover:text-white border border-[#1A263D] hover:border-[#3B82F6]/50 transition-all text-[11px]"
                    >
                      Trade
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

