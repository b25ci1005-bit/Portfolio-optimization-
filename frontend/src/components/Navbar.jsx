import React from 'react';
import { Activity, Sliders, TrendingUp, BarChart3, Radio } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, upstoxStatus, portfolioNav }) {
  const isLive = upstoxStatus?.is_live;

  const navItems = [
    { id: 'dashboard', label: 'Portfolio', icon: Activity },
    { id: 'optimizer', label: 'Optimizer', icon: Sliders },
    { id: 'backtest', label: 'Backtest', icon: TrendingUp },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'upstox', label: 'Broker Link', icon: Radio },
  ];

  return (
    <header className="border-b border-[#1A263D] bg-[#080C14]/85 backdrop-blur-xl sticky top-0 z-50 px-6 py-2.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand - Untouched signature arrow gradient from screenshot */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#3B82F6] to-[#10B981] flex items-center justify-center shadow-sm shadow-blue-500/20 ring-1 ring-white/10">
            <TrendingUp className="w-4 h-4 text-white" />
          </div>
          <div className="flex items-center gap-2">
            <span className="font-semibold text-sm tracking-wide text-white font-sans">QUANTDESK</span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#121B2F] text-[#94A3B8] border border-[#1A263D]">
              NSE
            </span>
          </div>
        </div>

        {/* Navigation Tabs (Linear-style segmented pills) */}
        <nav className="flex items-center gap-1 bg-[#0D1322] p-1 rounded-lg border border-[#1A263D] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-[#1A263D] text-white shadow-sm ring-1 ring-white/10 border border-white/5'
                    : 'text-[#94A3B8] hover:text-white hover:bg-[#121B2F]'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-[#3B82F6]' : 'text-[#64748B]'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Status Pill & Live NAV */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab('upstox')}
            className={`flex items-center gap-2 px-2.5 py-1 rounded-md text-xs font-mono transition-all border ${
              isLive
                ? 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]/30 hover:bg-[#10B981]/20 shadow-sm shadow-emerald-500/10'
                : 'bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/30 hover:bg-[#F59E0B]/20 shadow-sm shadow-amber-500/10'
            }`}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${isLive ? 'bg-[#10B981] animate-pulse' : 'bg-[#F59E0B]'}`} />
            <span className="text-[11px] font-medium tracking-tight">{isLive ? 'UPSTOX LIVE' : 'PAPER LEDGER'}</span>
          </button>

          {portfolioNav !== undefined && (
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-md bg-[#0D1322] border border-[#1A263D] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]">
              <span className="text-[10px] text-[#64748B] font-mono uppercase">NAV</span>
              <span className="text-xs font-mono font-semibold text-[#F8FAFC] tabular-nums">
                ₹{portfolioNav.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
              </span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

