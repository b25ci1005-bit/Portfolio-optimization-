import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

export default function StatCard({
  title,
  value,
  subValue,
  change,
  isPositive,
  icon: Icon,
  suffix = '',
  prefix = ''
}) {
  return (
    <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-4 flex flex-col justify-between shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06),0_4px_20px_-2px_rgba(0,0,0,0.5)] hover:border-[#3B82F6]/40 hover:shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_8px_30px_-4px_rgba(59,130,246,0.15)] transition-all duration-200">
      <div className="flex items-center justify-between text-[#94A3B8] mb-2">
        <span className="text-[11px] font-medium uppercase tracking-wider">{title}</span>
        {Icon && <Icon className="w-3.5 h-3.5 text-[#64748B]" />}
      </div>

      <div className="my-0.5">
        <div className="text-2xl font-bold font-mono text-[#F8FAFC] tracking-tight tabular-nums">
          {prefix}{value}{suffix}
        </div>
      </div>

      <div className="flex items-center justify-between mt-2 pt-2 border-t border-[#1A263D] text-xs">
        {change !== undefined ? (
          <div
            className={`inline-flex items-center gap-0.5 px-2 py-0.5 rounded text-[11px] font-mono font-medium border ${
              isPositive 
                ? 'text-[#10B981] bg-[#10B981]/10 border-[#10B981]/25' 
                : 'text-[#F43F5E] bg-[#F43F5E]/10 border-[#F43F5E]/25'
            }`}
          >
            {isPositive ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
            <span>{isPositive ? '+' : ''}{change}%</span>
          </div>
        ) : (
          <span className="text-[11px] font-mono text-[#64748B]">{subValue}</span>
        )}
        {subValue && change !== undefined && (
          <span className="text-[11px] font-mono text-[#94A3B8]">{subValue}</span>
        )}
      </div>
    </div>
  );
}

