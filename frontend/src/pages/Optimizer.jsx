import React, { useState, useEffect } from 'react';
import {
  Sliders,
  Play,
  CheckCircle2,
  TrendingUp,
  Percent,
  ShieldAlert,
  ArrowRight,
  Info,
  RefreshCw,
  Code,
  Sparkles,
  Layers,
  Terminal,
  FileCode2
} from 'lucide-react';
import EfficientFrontierChart from '../components/EfficientFrontierChart';
import AllocationDonut from '../components/AllocationDonut';
import {
  fetchInstruments,
  optimizePortfolio,
  getEfficientFrontier,
  rebalancePortfolio,
  fetchStrategies,
  runStrategy
} from '../api';

export default function Optimizer({ setActiveTab, onRebalanceDone }) {
  const [activeMode, setActiveMode] = useState('math'); // 'math' | 'strategy'
  const [instruments, setInstruments] = useState([]);
  const [presets, setPresets] = useState({});
  const [selectedSymbols, setSelectedSymbols] = useState([
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
    'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'LT.NS'
  ]);
  const [optimizer, setOptimizer] = useState('maximum_sharpe');
  const [covariance, setCovariance] = useState('ledoit_wolf');
  const [maxAssetWeight, setMaxAssetWeight] = useState(0.25);
  const [maxSectorWeight, setMaxSectorWeight] = useState(0.35);
  const [cashBuffer, setCashBuffer] = useState(0.02);

  // Black-Litterman views state
  const [viewSymbol, setViewSymbol] = useState('INFY.NS');
  const [viewExpectedReturn, setViewExpectedReturn] = useState(0.20);
  const [views, setViews] = useState({});

  // Custom strategies state
  const [availableStrategies, setAvailableStrategies] = useState([]);
  const [selectedStrategyId, setSelectedStrategyId] = useState('my_custom_strategy');
  const [strategyResult, setStrategyResult] = useState(null);

  const [loading, setLoading] = useState(false);
  const [rebalancing, setRebalancing] = useState(false);
  const [optResult, setOptResult] = useState(null);
  const [frontierData, setFrontierData] = useState(null);
  const [rebalanceMsg, setRebalanceMsg] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchInstruments()
      .then((res) => {
        setInstruments(res.instruments || []);
        setPresets(res.presets || {});
      })
      .catch((err) => console.error(err));

    fetchStrategies()
      .then((res) => {
        setAvailableStrategies(res.strategies || []);
      })
      .catch((err) => console.error(err));
  }, []);

  const handleSelectPreset = (presetKey) => {
    if (presets[presetKey]) {
      setSelectedSymbols(presets[presetKey]);
    }
  };

  const toggleSymbol = (sym) => {
    if (selectedSymbols.includes(sym)) {
      if (selectedSymbols.length > 2) {
        setSelectedSymbols(selectedSymbols.filter((s) => s !== sym));
      }
    } else {
      setSelectedSymbols([...selectedSymbols, sym]);
    }
  };

  const handleAddView = () => {
    if (viewSymbol) {
      setViews({ ...views, [viewSymbol]: Number(viewExpectedReturn) });
    }
  };

  const handleRemoveView = (sym) => {
    const newViews = { ...views };
    delete newViews[sym];
    setViews(newViews);
  };

  const handleRunOptimization = async () => {
    setLoading(true);
    setError(null);
    setRebalanceMsg(null);

    try {
      // 1. Run optimization
      const res = await optimizePortfolio({
        symbols: selectedSymbols,
        optimizer,
        covariance,
        max_asset_weight: Number(maxAssetWeight),
        max_sector_weight: Number(maxSectorWeight),
        cash_buffer: Number(cashBuffer),
        views: Object.keys(views).length > 0 ? views : undefined
      });
      setOptResult(res);

      // 2. Fetch Efficient Frontier
      const frontierRes = await getEfficientFrontier(selectedSymbols, covariance);
      setFrontierData(frontierRes);
    } catch (err) {
      setError(err.message || 'Optimization failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRunStrategy = async () => {
    setLoading(true);
    setError(null);
    setRebalanceMsg(null);

    try {
      const res = await runStrategy({
        strategy_id: selectedStrategyId,
        symbols: selectedSymbols,
        cash_buffer: Number(cashBuffer)
      });
      setStrategyResult(res);
    } catch (err) {
      setError(err.message || 'Strategy execution failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDeployToPortfolio = async (weightsToDeploy, optName, covName) => {
    if (!weightsToDeploy) return;
    setRebalancing(true);
    try {
      const res = await rebalancePortfolio({
        target_weights: weightsToDeploy,
        optimizer_name: optName,
        covariance_name: covName
      });
      setRebalanceMsg(`Rebalanced successfully! Executed ${res.orders_count} orders.`);
      if (onRebalanceDone) onRebalanceDone();
      setTimeout(() => {
        setActiveTab('dashboard');
      }, 1500);
    } catch (err) {
      setError(err.message || 'Rebalance failed');
    } finally {
      setRebalancing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Mode Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-[#1A263D]">
        <div className="flex items-center gap-2.5">
          <h1 className="text-base font-semibold text-[#F8FAFC] tracking-tight">Optimizer Studio</h1>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#121B2F] text-[#94A3B8] border border-[#1A263D]">
            {activeMode === 'math' ? 'CVXPY & SLSQP' : 'Alpha Models'}
          </span>
        </div>

        {/* Linear-style Segmented Pills */}
        <div className="flex items-center bg-[#0D1322] p-1 rounded-lg border border-[#1A263D] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.04)]">
          <button
            onClick={() => setActiveMode('math')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeMode === 'math'
                ? 'bg-[#1A263D] text-white shadow-sm ring-1 ring-white/10 border border-white/5'
                : 'text-[#94A3B8] hover:text-white'
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>Mathematical Solvers</span>
          </button>
          <button
            onClick={() => setActiveMode('strategy')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeMode === 'strategy'
                ? 'bg-[#1A263D] text-white shadow-sm ring-1 ring-white/10 border border-white/5'
                : 'text-[#94A3B8] hover:text-white'
            }`}
          >
            <Code className="w-3.5 h-3.5" />
            <span>Quant Strategies</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-[#EF4444]/10 border border-[#EF4444]/30 text-[#EF4444] text-xs font-mono">
          {error}
        </div>
      )}

      {rebalanceMsg && (
        <div className="p-3 rounded-lg bg-[#10B981]/10 border border-[#10B981]/30 text-[#10B981] text-xs font-mono flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" />
          <span>{rebalanceMsg}</span>
        </div>
      )}

      {/* Mode 1: Mathematical Convex Solvers */}
      {activeMode === 'math' ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Configuration Controls (4 cols) */}
          <div className="lg:col-span-4 bg-[#0D1322] border border-[#1A263D] rounded-xl p-4 space-y-4 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06),0_4px_20px_-2px_rgba(0,0,0,0.5)]">
            {/* Presets */}
            <div>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-[#94A3B8] block mb-1.5">
                Universe Presets
              </span>
              <div className="grid grid-cols-2 gap-1.5">
                {Object.keys(presets).map((key) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => handleSelectPreset(key)}
                    className="px-2.5 py-1.5 rounded-lg bg-[#080D18] hover:bg-[#121B2F] text-[#94A3B8] hover:text-white border border-[#1A263D] text-[11px] font-mono transition-colors text-left truncate"
                  >
                    {key.replace(/_/g, ' ')}
                  </button>
                ))}
              </div>
            </div>

            {/* Model Select */}
            <div>
              <label className="text-[10px] font-semibold uppercase tracking-wider text-[#94A3B8] block mb-1.5">
                Optimization Model
              </label>
              <select
                value={optimizer}
                onChange={(e) => setOptimizer(e.target.value)}
                className="w-full bg-[#080D18] border border-[#1A263D] rounded-lg px-2.5 py-2 text-xs font-mono text-[#F8FAFC] focus:border-[#3B82F6] outline-none"
              >
                <option value="maximum_sharpe">Maximum Sharpe Ratio (Rf = 6.5%)</option>
                <option value="minimum_variance">Minimum Variance (Quadratic QP)</option>
                <option value="risk_parity">Risk Parity / ERC</option>
                <option value="hierarchical_risk_parity">Hierarchical Risk Parity (HRP)</option>
                <option value="black_litterman">Black-Litterman (Bayesian Views)</option>
                <option value="cvar">CVaR 95% Expected Shortfall</option>
              </select>
            </div>

            {/* Covariance Estimation */}
            <div>
              <label className="text-[10px] font-semibold uppercase tracking-wider text-[#94A3B8] block mb-1.5">
                Covariance Matrix
              </label>
              <select
                value={covariance}
                onChange={(e) => setCovariance(e.target.value)}
                className="w-full bg-[#080D18] border border-[#1A263D] rounded-lg px-2.5 py-2 text-xs font-mono text-[#F8FAFC] focus:border-[#3B82F6] outline-none"
              >
                <option value="ledoit_wolf">Ledoit-Wolf Analytic Shrinkage</option>
                <option value="sample">Sample Covariance (Annualized)</option>
                <option value="rmt">Random Matrix Theory (Cleaned)</option>
                <option value="three_factor">3-Factor Structured</option>
              </select>
            </div>

            {/* Constraints Sliders */}
            <div className="space-y-3 pt-2 border-t border-[#1A263D]">
              <div>
                <div className="flex justify-between text-xs font-mono mb-1">
                  <span className="text-[#94A3B8]">Max Single Asset:</span>
                  <span className="text-[#F8FAFC] font-semibold">{Math.round(maxAssetWeight * 100)}%</span>
                </div>
                <input
                  type="range"
                  min="0.05"
                  max="0.50"
                  step="0.05"
                  value={maxAssetWeight}
                  onChange={(e) => setMaxAssetWeight(e.target.value)}
                  className="w-full accent-[#3B82F6] cursor-pointer"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs font-mono mb-1">
                  <span className="text-[#94A3B8]">Max Sector Cap:</span>
                  <span className="text-[#F8FAFC] font-semibold">{Math.round(maxSectorWeight * 100)}%</span>
                </div>
                <input
                  type="range"
                  min="0.10"
                  max="0.60"
                  step="0.05"
                  value={maxSectorWeight}
                  onChange={(e) => setMaxSectorWeight(e.target.value)}
                  className="w-full accent-[#3B82F6] cursor-pointer"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs font-mono mb-1">
                  <span className="text-[#94A3B8]">Cash Buffer:</span>
                  <span className="text-[#F8FAFC] font-semibold">{Math.round(cashBuffer * 100)}%</span>
                </div>
                <input
                  type="range"
                  min="0.00"
                  max="0.10"
                  step="0.01"
                  value={cashBuffer}
                  onChange={(e) => setCashBuffer(e.target.value)}
                  className="w-full accent-[#3B82F6] cursor-pointer"
                />
              </div>
            </div>

            {/* Black-Litterman Active Views */}
            {optimizer === 'black_litterman' && (
              <div className="p-3 bg-[#080D18] rounded-lg border border-[#1A263D] space-y-2">
                <span className="text-[10px] font-semibold text-[#F59E0B] uppercase block">Investor Views</span>
                <div className="flex gap-2">
                  <select
                    value={viewSymbol}
                    onChange={(e) => setViewSymbol(e.target.value)}
                    className="bg-[#0D1322] border border-[#1A263D] rounded px-2 py-1 text-xs text-[#F8FAFC]"
                  >
                    {selectedSymbols.map((s) => (
                      <option key={s} value={s}>{s.replace('.NS', '')}</option>
                    ))}
                  </select>
                  <input
                    type="number"
                    step="0.01"
                    value={viewExpectedReturn}
                    onChange={(e) => setViewExpectedReturn(e.target.value)}
                    placeholder="Return (e.g. 0.20)"
                    className="w-20 bg-[#0D1322] border border-[#1A263D] rounded px-2 py-1 text-xs text-[#F8FAFC] font-mono"
                  />
                  <button
                    type="button"
                    onClick={handleAddView}
                    className="px-2 py-1 bg-[#3B82F6] hover:bg-blue-600 rounded text-xs text-white font-semibold"
                  >
                    Add
                  </button>
                </div>
                {Object.keys(views).length > 0 && (
                  <div className="space-y-1 mt-1">
                    {Object.entries(views).map(([s, ret]) => (
                      <div key={s} className="flex items-center justify-between text-[11px] font-mono text-[#94A3B8]">
                        <span>{s.replace('.NS', '')}: +{(ret * 100).toFixed(1)}%</span>
                        <button onClick={() => handleRemoveView(s)} className="text-[#F43F5E] hover:underline">Remove</button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Run Button with signature arrow gradient */}
            <button
              onClick={handleRunOptimization}
              disabled={loading}
              className="w-full py-2.5 rounded-lg bg-gradient-to-r from-[#3B82F6] to-[#10B981] hover:from-[#2563EB] hover:to-[#059669] text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-md shadow-blue-500/20 hover:shadow-emerald-500/20 transition-all disabled:opacity-50"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Optimizing...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Run Optimization</span>
                </>
              )}
            </button>
          </div>

          {/* Right Column: Universe & Results (8 cols) */}
          <div className="lg:col-span-8 space-y-6">
            {/* Ticker Badges Selector */}
            <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-4 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06),0_4px_20px_-2px_rgba(0,0,0,0.5)]">
              <div className="flex items-center justify-between mb-2.5">
                <span className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">
                  Universe ({selectedSymbols.length} Selected)
                </span>
                <button
                  onClick={() => setSelectedSymbols(instruments.map((i) => i.symbol))}
                  className="text-[11px] text-[#3B82F6] hover:underline font-mono"
                >
                  Select All
                </button>
              </div>

              <div className="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto pr-1">
                {instruments.map((inst) => {
                  const isSelected = selectedSymbols.includes(inst.symbol);
                  return (
                    <button
                      key={inst.symbol}
                      onClick={() => toggleSymbol(inst.symbol)}
                      className={`px-2 py-0.5 rounded text-xs font-mono transition-colors border ${
                        isSelected
                          ? 'bg-[#1A263D] text-white border-[#3B82F6] shadow-sm shadow-blue-500/20'
                          : 'bg-[#080D18] text-[#94A3B8] border-[#1A263D] hover:text-white hover:bg-[#121B2F]'
                      }`}
                    >
                      {inst.symbol.replace('.NS', '')}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Results Display */}
            {optResult && (
              <div className="space-y-6">
                {/* 3 Metric Cards */}
                <div className="grid grid-cols-3 gap-3">
                  <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-3 text-center shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06)]">
                    <span className="text-[10px] text-[#94A3B8] uppercase block mb-0.5">Exp Return</span>
                    <span className="text-lg font-bold font-mono text-[#10B981] tabular-nums">
                      +{(optResult.expected_annual_return * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-3 text-center shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06)]">
                    <span className="text-[10px] text-[#94A3B8] uppercase block mb-0.5">Annual Vol</span>
                    <span className="text-lg font-bold font-mono text-[#F8FAFC] tabular-nums">
                      {(optResult.annual_volatility * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-3 text-center shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06)]">
                    <span className="text-[10px] text-[#94A3B8] uppercase block mb-0.5">Sharpe</span>
                    <span className="text-lg font-bold font-mono text-[#3B82F6] tabular-nums">
                      {optResult.sharpe_ratio}
                    </span>
                  </div>
                </div>

                {/* Efficient Frontier Chart */}
                <EfficientFrontierChart frontierData={frontierData} />

                {/* Allocation Donut & Weights Table */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <AllocationDonut
                    weights={optResult.constrained_weights}
                    sectorAllocations={optResult.sector_allocations}
                  />

                  {/* Weights Table */}
                  <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-4 overflow-hidden shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06)]">
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8] mb-2.5">Target Weights</h3>
                    <div className="max-h-60 overflow-y-auto">
                      <table className="w-full text-left text-xs font-mono">
                        <thead className="bg-[#080D18] text-[#94A3B8] uppercase sticky top-0 text-[10px]">
                          <tr>
                            <th className="py-2 px-3">Asset</th>
                            <th className="py-2 px-3 text-right">Weight</th>
                            <th className="py-2 px-3 text-right">Risk %</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#1A263D]/60">
                          {Object.entries(optResult.constrained_weights).map(([sym, w]) => {
                            const rc = optResult.risk_contributions ? optResult.risk_contributions[sym] : 0.0;
                            return (
                              <tr key={sym} className="hover:bg-[#121B2F]/50">
                                <td className="py-1.5 px-3 font-semibold text-[#F8FAFC]">{sym.replace('.NS', '')}</td>
                                <td className="py-1.5 px-3 text-right tabular-nums text-[#F8FAFC]">
                                  {(w * 100).toFixed(1)}%
                                </td>
                                <td className="py-1.5 px-3 text-right tabular-nums text-[#3B82F6]">
                                  {rc ? `${(rc * 100).toFixed(1)}%` : '-'}
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>

                {/* Rebalance Action Banner */}
                <div className="bg-[#0D1322] border border-[#10B981]/30 rounded-xl p-4 flex items-center justify-between gap-4 shadow-[inset_0_1px_0_0_rgba(16,185,129,0.1),0_4px_20px_rgba(0,0,0,0.4)]">
                  <div>
                    <h4 className="font-semibold text-[#F8FAFC] text-xs">Deploy Target Allocation to Paper Ledger</h4>
                    <p className="text-[11px] text-[#64748B]">Executes simulated market orders with Indian statutory fees & slippage.</p>
                  </div>
                  <button
                    onClick={() => handleDeployToPortfolio(optResult.constrained_weights, optResult.optimizer, optResult.covariance)}
                    disabled={rebalancing}
                    className="px-4 py-2 rounded-lg bg-gradient-to-r from-[#10B981] to-[#059669] hover:from-[#059669] hover:to-[#047857] text-white font-semibold text-xs flex items-center gap-1.5 shadow-md shadow-emerald-500/20 transition-all disabled:opacity-50 flex-shrink-0"
                  >
                    {rebalancing ? (
                      <>
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        <span>Rebalancing...</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Rebalance Portfolio</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Mode 2: Custom Quantitative Strategies */
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Strategy Picker (4 cols) */}
          <div className="lg:col-span-4 space-y-4">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-[#94A3B8] block">
              Registered Strategies
            </span>
            <div className="space-y-2">
              {availableStrategies.map((strat) => {
                const isSelected = strat.id === selectedStrategyId;
                return (
                  <div
                    key={strat.id}
                    onClick={() => setSelectedStrategyId(strat.id)}
                    className={`p-3 rounded-xl border cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-[#1A263D] border-[#3B82F6] shadow-sm shadow-blue-500/10'
                        : 'bg-[#0D1322] border-[#1A263D] hover:border-[#2A3B5C]'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-xs text-[#F8FAFC]">{strat.name}</span>
                      <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-[#080D18] text-[#94A3B8] border border-[#1A263D]">
                        {strat.category}
                      </span>
                    </div>
                    <p className="text-[11px] text-[#94A3B8] line-clamp-2 leading-relaxed">
                      {strat.description}
                    </p>
                  </div>
                );
              })}
            </div>

            {/* Cash Buffer & Execute */}
            <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-4 space-y-3 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06),0_4px_20px_-2px_rgba(0,0,0,0.5)]">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-[#94A3B8]">Cash Buffer:</span>
                <span className="text-[#F8FAFC] font-semibold">{Math.round(cashBuffer * 100)}%</span>
              </div>
              <input
                type="range"
                min="0.00"
                max="0.10"
                step="0.01"
                value={cashBuffer}
                onChange={(e) => setCashBuffer(e.target.value)}
                className="w-full accent-[#3B82F6] cursor-pointer"
              />

              <button
                onClick={handleRunStrategy}
                disabled={loading}
                className="w-full py-2.5 rounded-lg bg-gradient-to-r from-[#3B82F6] to-[#10B981] hover:from-[#2563EB] hover:to-[#059669] text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-md shadow-blue-500/20 hover:shadow-emerald-500/20 transition-all disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Evaluating Alpha Signals...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-3.5 h-3.5 fill-current" />
                    <span>Run Strategy Signals</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Right Column: Universe & Output (8 cols) */}
          <div className="lg:col-span-8 space-y-6">
            {/* Universe Selector */}
            <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-4 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06),0_4px_20px_-2px_rgba(0,0,0,0.5)]">
              <div className="flex items-center justify-between mb-2.5">
                <span className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">
                  Universe ({selectedSymbols.length} Tickers)
                </span>
                <div className="flex gap-1.5">
                  {Object.keys(presets).slice(0, 2).map((key) => (
                    <button
                      key={key}
                      type="button"
                      onClick={() => handleSelectPreset(key)}
                      className="px-2 py-0.5 rounded bg-[#080D18] text-[#94A3B8] hover:text-white border border-[#1A263D] text-[10px] font-mono"
                    >
                      {key.replace(/_/g, ' ')}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto pr-1">
                {instruments.map((inst) => {
                  const isSelected = selectedSymbols.includes(inst.symbol);
                  return (
                    <button
                      key={inst.symbol}
                      onClick={() => toggleSymbol(inst.symbol)}
                      className={`px-2 py-0.5 rounded text-xs font-mono transition-colors border ${
                        isSelected
                          ? 'bg-[#1A263D] text-white border-[#3B82F6] shadow-sm shadow-blue-500/20'
                          : 'bg-[#080D18] text-[#94A3B8] border-[#1A263D] hover:text-white hover:bg-[#121B2F]'
                      }`}
                    >
                      {inst.symbol.replace('.NS', '')}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Strategy Output */}
            {strategyResult ? (
              <div className="space-y-6">
                {/* 3 Metric Cards */}
                <div className="grid grid-cols-3 gap-3">
                  <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-3 text-center shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06)]">
                    <span className="text-[10px] text-[#94A3B8] uppercase block mb-0.5">Exp Return</span>
                    <span className="text-lg font-bold font-mono text-[#10B981] tabular-nums">
                      +{strategyResult.expected_return}%
                    </span>
                  </div>
                  <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-3 text-center shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06)]">
                    <span className="text-[10px] text-[#94A3B8] uppercase block mb-0.5">Volatility</span>
                    <span className="text-lg font-bold font-mono text-[#F8FAFC] tabular-nums">
                      {strategyResult.volatility}%
                    </span>
                  </div>
                  <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-3 text-center shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06)]">
                    <span className="text-[10px] text-[#94A3B8] uppercase block mb-0.5">Sharpe</span>
                    <span className="text-lg font-bold font-mono text-[#3B82F6] tabular-nums">
                      {strategyResult.sharpe}
                    </span>
                  </div>
                </div>

                {/* Donut & Weights Table */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <AllocationDonut weights={strategyResult.weights} />

                  <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-4 overflow-hidden shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06)]">
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8] mb-2.5">
                      Strategy Allocation
                    </h3>
                    <div className="max-h-60 overflow-y-auto">
                      <table className="w-full text-left text-xs font-mono">
                        <thead className="bg-[#080D18] text-[#94A3B8] uppercase sticky top-0 text-[10px]">
                          <tr>
                            <th className="py-2 px-3">Asset</th>
                            <th className="py-2 px-3 text-right">Target Weight</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#1A263D]/60">
                          {Object.entries(strategyResult.weights).map(([sym, w]) => (
                            <tr key={sym} className="hover:bg-[#121B2F]/50">
                              <td className="py-1.5 px-3 font-semibold text-[#F8FAFC]">{sym.replace('.NS', '')}</td>
                              <td className="py-1.5 px-3 text-right tabular-nums text-[#F8FAFC]">
                                {(w * 100).toFixed(1)}%
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>

                {/* Rebalance Action */}
                <div className="bg-[#0D1322] border border-[#10B981]/30 rounded-xl p-4 flex items-center justify-between gap-4 shadow-[inset_0_1px_0_0_rgba(16,185,129,0.1),0_4px_20px_rgba(0,0,0,0.4)]">
                  <div>
                    <h4 className="font-semibold text-[#F8FAFC] text-xs">Deploy Strategy to Paper Ledger</h4>
                    <p className="text-[11px] text-[#64748B]">Executes rebalance per {strategyResult.strategy_name} targets.</p>
                  </div>
                  <button
                    onClick={() => handleDeployToPortfolio(strategyResult.weights, strategyResult.strategy_name, 'Strategy Signal')}
                    disabled={rebalancing}
                    className="px-4 py-2 rounded-lg bg-gradient-to-r from-[#10B981] to-[#059669] hover:from-[#059669] hover:to-[#047857] text-white font-semibold text-xs flex items-center gap-1.5 shadow-md shadow-emerald-500/20 transition-all disabled:opacity-50 flex-shrink-0"
                  >
                    {rebalancing ? (
                      <>
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        <span>Rebalancing...</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Rebalance Portfolio</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            ) : (
              <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-8 text-center text-[#64748B] space-y-2 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06)]">
                <Terminal className="w-8 h-8 text-[#3B82F6] mx-auto opacity-60" />
                <h4 className="text-xs font-medium text-[#F8FAFC]">Select a Strategy and Click "Run Strategy Signals"</h4>
                <p className="text-[11px] max-w-sm mx-auto">
                  Evaluates historical indicators and returns risk-budgeted weights for execution.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}


