import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Optimizer from './pages/Optimizer';
import Backtest from './pages/Backtest';
import Analytics from './pages/Analytics';
import UpstoxConnect from './pages/UpstoxConnect';
import { getUpstoxStatus, getPortfolioState } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [upstoxStatus, setUpstoxStatus] = useState(null);
  const [portfolioNav, setPortfolioNav] = useState(1000000);

  const refreshGlobalState = async () => {
    try {
      const [uStatus, pState] = await Promise.all([
        getUpstoxStatus().catch(() => null),
        getPortfolioState().catch(() => null),
      ]);
      if (uStatus) setUpstoxStatus(uStatus);
      if (pState?.portfolio?.nav) setPortfolioNav(pState.portfolio.nav);
    } catch (err) {
      console.error('Failed to sync global state:', err);
    }
  };

  useEffect(() => {
    refreshGlobalState();
    const interval = setInterval(refreshGlobalState, 20000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-transparent text-[#F8FAFC] flex flex-col font-sans selection:bg-[#3B82F6]/30">
      {/* Top Institutional Header */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        upstoxStatus={upstoxStatus}
        portfolioNav={portfolioNav}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6">
        {activeTab === 'dashboard' && (
          <Dashboard
            setActiveTab={setActiveTab}
            upstoxStatus={upstoxStatus}
          />
        )}
        {activeTab === 'optimizer' && (
          <Optimizer
            setActiveTab={setActiveTab}
            onRebalanceDone={refreshGlobalState}
          />
        )}
        {activeTab === 'backtest' && (
          <Backtest />
        )}
        {activeTab === 'analytics' && (
          <Analytics />
        )}
        {activeTab === 'upstox' && (
          <UpstoxConnect
            onStatusChange={refreshGlobalState}
          />
        )}
      </main>

      {/* Institutional Footer */}
      <footer className="border-t border-[#1A263D] bg-[#080C14]/90 backdrop-blur-md py-3 px-6 text-xs text-[#94A3B8] font-mono">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <span className="w-2 h-2 rounded-full bg-[#10B981] shadow-sm shadow-emerald-500/50" />
            <span className="text-[#E2E8F0] font-medium">QuantDesk Institutional Terminal v1.0.0</span>
            <span className="text-[#1A263D]">|</span>
            <span className="text-[#94A3B8]">NSE 50 Universe</span>
          </div>
          <div className="flex items-center gap-4 text-[11px] text-[#64748B]">
            <span>Rf: <strong className="text-[#94A3B8]">6.50%</strong></span>
            <span>Microstructure Slippage: <strong className="text-[#10B981]">Active</strong></span>
            <span className="text-[#94A3B8] font-medium">FastAPI + React 18</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
