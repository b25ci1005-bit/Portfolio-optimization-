import React, { useState, useEffect } from 'react';
import {
  Radio,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
  HelpCircle,
  KeyRound
} from 'lucide-react';
import { getUpstoxStatus, updateUpstoxConfig } from '../api';

export default function UpstoxConnect({ onStatusChange }) {
  const [status, setStatus] = useState(null);
  const [apiKey, setApiKey] = useState('27b3ae9f-da6b-4b67-a0dd-b6ea9265efca');
  const [apiSecret, setApiSecret] = useState('');
  const [redirectUri, setRedirectUri] = useState('http://localhost:8000/api/upstox/callback');
  const [manualCode, setManualCode] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  const loadStatus = async () => {
    try {
      const res = await getUpstoxStatus();
      setStatus(res);
      if (res.redirect_uri) setRedirectUri(res.redirect_uri);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleCopyUri = () => {
    navigator.clipboard.writeText(redirectUri);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSaveConfig = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setMsg(null);

    try {
      await updateUpstoxConfig({
        api_key: apiKey.trim(),
        api_secret: apiSecret.trim(),
        redirect_uri: redirectUri.trim()
      });
      setMsg('API configuration saved to .env');
      loadStatus();
      if (onStatusChange) onStatusChange();
    } catch (err) {
      setError(err.message || 'Failed to update credentials');
    } finally {
      setSaving(false);
    }
  };

  const handleExchangeManualCode = (e) => {
    e.preventDefault();
    if (!manualCode) return;
    window.location.href = `http://localhost:8000/api/upstox/callback?code=${manualCode.trim()}`;
  };

  const isLive = status?.is_live;

  return (
    <div className="max-w-4xl mx-auto space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-[#1A263D]">
        <div>
          <h1 className="text-base font-semibold text-[#F8FAFC] tracking-tight flex items-center gap-2.5">
            Upstox Gateway & Execution
            <span
              className={`text-[11px] px-2 py-0.5 rounded font-mono font-medium border ${
                isLive
                  ? 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]/30'
                  : 'bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/30'
              }`}
            >
              {isLive ? 'LIVE BROKER' : 'PAPER SIMULATION'}
            </span>
          </h1>
          <p className="text-xs text-[#94A3B8] mt-0.5">
            NSE direct execution and market feed routing via Upstox API v2
          </p>
        </div>

        <a
          href="http://localhost:8000/api/upstox/authorize"
          target="_blank"
          rel="noopener noreferrer"
          className="px-4 py-2 rounded-lg bg-gradient-to-r from-[#3B82F6] to-[#10B981] hover:from-[#2563EB] hover:to-[#059669] text-white font-semibold text-xs flex items-center gap-2 transition-all shadow-md shadow-blue-500/20 hover:shadow-emerald-500/20"
        >
          <span>Connect Broker</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>

      {msg && (
        <div className="p-3 rounded-lg bg-[#10B981]/10 border border-[#10B981]/30 text-[#10B981] text-xs font-mono flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>{msg}</span>
        </div>
      )}

      {error && (
        <div className="p-3 rounded-lg bg-[#EF4444]/10 border border-[#EF4444]/30 text-[#EF4444] text-xs font-mono flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Gateway Status Summary */}
      <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-5 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06),0_4px_20px_-2px_rgba(0,0,0,0.5)]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#1A263D]">
          <div className="flex items-center gap-3">
            <div
              className={`w-10 h-10 rounded-lg flex items-center justify-center border ${
                isLive 
                  ? 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]/30' 
                  : 'bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/30'
              }`}
            >
              <Radio className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-semibold text-[#F8FAFC] flex items-center gap-2">
                <span>{isLive ? 'Active Live Session' : 'Paper Trading Fallback'}</span>
                <span className={`w-1.5 h-1.5 rounded-full ${isLive ? 'bg-[#10B981]' : 'bg-[#F59E0B]'}`} />
              </div>
              <p className="text-xs text-[#94A3B8] font-mono">
                {isLive ? `User ID: ${status?.user_id || 'Upstox Account'}` : 'Broker simulator active with Indian slippage & tax models'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={loadStatus}
              disabled={loading}
              className="px-3 py-1.5 rounded bg-[#121B2F] hover:bg-[#1A263D] text-[#94A3B8] hover:text-white text-xs border border-[#1A263D] transition-colors"
            >
              Refresh Status
            </button>
          </div>
        </div>

        {/* Status Indicators */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-4 text-xs font-mono">
          <div className="bg-[#080D18] p-3 rounded-lg border border-[#1A263D]">
            <span className="text-[#94A3B8] text-[11px] block mb-0.5">Execution Gateway</span>
            <span className="text-[#F8FAFC] font-medium">
              {isLive ? 'Direct Upstox v2' : 'NSE Paper Engine'}
            </span>
          </div>
          <div className="bg-[#080D18] p-3 rounded-lg border border-[#1A263D]">
            <span className="text-[#94A3B8] text-[11px] block mb-0.5">Market Data Feed</span>
            <span className="text-[#F8FAFC] font-medium">
              {isLive ? 'Upstox Streaming WebSocket' : 'NSE / Yahoo Cache'}
            </span>
          </div>
          <div className="bg-[#080D18] p-3 rounded-lg border border-[#1A263D]">
            <span className="text-[#94A3B8] text-[11px] block mb-0.5">Session Token</span>
            <span className={isLive ? 'text-[#10B981] font-medium' : 'text-[#F59E0B] font-medium'}>
              {isLive ? 'Valid' : 'Unauthenticated'}
            </span>
          </div>
        </div>
      </div>

      {/* Configuration Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Credentials Form */}
        <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-5 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06),0_4px_20px_-2px_rgba(0,0,0,0.5)]">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xs font-semibold text-[#F8FAFC] uppercase tracking-wider flex items-center gap-1.5">
              <KeyRound className="w-3.5 h-3.5 text-[#3B82F6]" />
              API Credentials
            </h3>
            <a
              href="https://account.upstox.com/developer/apps"
              target="_blank"
              rel="noreferrer"
              className="text-[11px] text-[#3B82F6] hover:underline inline-flex items-center gap-1 font-mono"
            >
              Developer Console <ExternalLink className="w-3 h-3" />
            </a>
          </div>

          <form onSubmit={handleSaveConfig} className="space-y-3.5 text-xs font-mono">
            <div>
              <label className="text-[#94A3B8] block mb-1">API Key (Client ID)</label>
              <input
                type="text"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Upstox API Key"
                className="w-full bg-[#080D18] border border-[#1A263D] rounded-lg px-3 py-2 text-[#F8FAFC] focus:border-[#3B82F6] outline-none text-xs"
                required
              />
            </div>

            <div>
              <label className="text-[#94A3B8] block mb-1">API Secret</label>
              <input
                type="password"
                value={apiSecret}
                onChange={(e) => setApiSecret(e.target.value)}
                placeholder="Enter secret to update"
                className="w-full bg-[#080D18] border border-[#1A263D] rounded-lg px-3 py-2 text-[#F8FAFC] focus:border-[#3B82F6] outline-none text-xs"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-[#94A3B8]">Redirect URI</label>
                <button
                  type="button"
                  onClick={handleCopyUri}
                  className="text-[11px] text-[#3B82F6] hover:underline flex items-center gap-1"
                >
                  {copied ? <Check className="w-3 h-3 text-[#10B981]" /> : <Copy className="w-3 h-3" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
              <input
                type="text"
                value={redirectUri}
                onChange={(e) => setRedirectUri(e.target.value)}
                className="w-full bg-[#080D18] border border-[#1A263D] rounded-lg px-3 py-2 text-[#F8FAFC] focus:border-[#3B82F6] outline-none text-xs"
                required
              />
              <div className="flex gap-2 mt-1.5">
                <button
                  type="button"
                  onClick={() => setRedirectUri('http://localhost:8000/api/upstox/callback')}
                  className="px-2 py-0.5 rounded bg-[#080D18] hover:bg-[#121B2F] text-[#94A3B8] text-[10px] border border-[#1A263D]"
                >
                  localhost:8000
                </button>
                <button
                  type="button"
                  onClick={() => setRedirectUri('http://127.0.0.1:8000/api/upstox/callback')}
                  className="px-2 py-0.5 rounded bg-[#080D18] hover:bg-[#121B2F] text-[#94A3B8] text-[10px] border border-[#1A263D]"
                >
                  127.0.0.1:8000
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={saving}
              className="w-full py-2 rounded-lg bg-gradient-to-r from-[#3B82F6] to-[#10B981] hover:from-[#2563EB] hover:to-[#059669] text-white font-semibold text-xs shadow-md shadow-blue-500/20 hover:shadow-emerald-500/20 transition-all disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save Configuration'}
            </button>
          </form>
        </div>

        {/* Right column: Auth code exchange + UDAPI100068 resolution */}
        <div className="space-y-4">
          <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-5 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06),0_4px_20px_-2px_rgba(0,0,0,0.5)]">
            <h3 className="text-xs font-semibold text-[#F8FAFC] uppercase tracking-wider mb-2">
              Manual Auth Code Exchange
            </h3>
            <p className="text-xs text-[#94A3B8] mb-3">
              If your callback landed with a <code className="text-[#3B82F6] font-mono">?code=...</code> parameter, paste it below:
            </p>

            <form onSubmit={handleExchangeManualCode} className="space-y-2.5 text-xs font-mono">
              <input
                type="text"
                value={manualCode}
                onChange={(e) => setManualCode(e.target.value)}
                placeholder="Paste code parameter"
                className="w-full bg-[#080D18] border border-[#1A263D] rounded-lg px-3 py-2 text-[#F8FAFC] focus:border-[#3B82F6] outline-none text-xs"
              />
              <button
                type="submit"
                disabled={!manualCode}
                className="w-full py-2 rounded-lg bg-gradient-to-r from-[#10B981] to-[#059669] hover:from-[#059669] hover:to-[#047857] text-white font-semibold text-xs shadow-md shadow-emerald-500/20 transition-all disabled:opacity-50"
              >
                Exchange Code
              </button>
            </form>
          </div>

          <div className="bg-[#0D1322] border border-[#1A263D] rounded-xl p-4 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06)]">
            <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-[#F8FAFC]">
              <HelpCircle className="w-3.5 h-3.5 text-[#F59E0B]" />
              <span>UDAPI100068 Resolution</span>
            </div>
            <p className="text-[11px] text-[#94A3B8] leading-relaxed">
              Ensure the exact Redirect URL in Upstox Developer Console matches <code className="text-[#10B981] font-mono">{redirectUri}</code>. Discrepancies between <code className="text-[#F8FAFC] font-mono">localhost</code> vs <code className="text-[#F8FAFC] font-mono">127.0.0.1</code> will trigger UDAPI100068.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
