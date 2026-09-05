"""
Market Data Pipeline with Dual Feeds:
1. Upstox API v2 for live quotes and historical daily candles (when authenticated).
2. yfinance fallback with local disk caching for resilient offline/air-gapped execution.
3. Synthetic Geometric Brownian Motion generator for instant testing/zero-dependency sandbox.
"""

import os
import json
import logging
import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import numpy as np
import pandas as pd

from backend.app.config import settings
from backend.app.data.instruments import get_instrument

logger = logging.getLogger(__name__)

CACHE_DIR = Path("./.cache/market_data")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

class MarketDataProvider:
    def __init__(self, upstox_token: Optional[str] = None):
        self.upstox_token = upstox_token
        self.benchmark_symbol = "^NSEI"

    def fetch_historical_prices(
        self,
        symbols: List[str],
        start_date: str = "2020-01-01",
        end_date: Optional[str] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Fetch historical close prices for given symbols.
        Returns DataFrame indexed by date with symbol columns.
        """
        if end_date is None:
            end_date = datetime.date.today().strftime("%Y-%m-%d")

        cache_key = f"prices_{'_'.join(sorted(symbols[:5]))}_{len(symbols)}_{start_date}_{end_date}.parquet"
        cache_path = CACHE_DIR / cache_key

        if use_cache and cache_path.exists():
            try:
                df = pd.read_parquet(cache_path)
                # Check if all requested symbols are present
                missing = [s for s in symbols if s not in df.columns]
                if not missing:
                    return df[symbols].dropna()
            except Exception as e:
                logger.warning(f"Failed to read parquet cache: {e}")

        # Attempt 1: Upstox API if token is provided
        df = None
        if self.upstox_token:
            df = self._fetch_upstox_historical(symbols, start_date, end_date)

        # Attempt 2: yfinance fallback
        if df is None or df.empty:
            df = self._fetch_yfinance_historical(symbols, start_date, end_date)

        # Attempt 3: Synthetic fallback if both external providers fail
        if df is None or df.empty:
            logger.warning("External market data failed. Generating realistic synthetic data.")
            df = self._generate_synthetic_prices(symbols, start_date, end_date)

        # Clean corporate actions, fill missing days, forward fill
        df = df.ffill().bfill().dropna()

        # Save to parquet cache
        try:
            df.to_parquet(cache_path)
        except Exception as e:
            logger.debug(f"Could not write cache file: {e}")

        return df

    def _fetch_upstox_historical(
        self, symbols: List[str], start_date: str, end_date: str
    ) -> Optional[pd.DataFrame]:
        """Fetch historical daily candles via Upstox API v2"""
        try:
            import requests
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.upstox_token}"
            }
            price_series = {}

            for sym in symbols:
                inst = get_instrument(sym)
                inst_key = inst.get("upstox_key", f"NSE_EQ|{sym.replace('.NS', '')}")
                # Upstox endpoint: /historical-candle/{instrument_key}/day/{to_date}/{from_date}
                url = f"{settings.UPSTOX_BASE_API}/historical-candle/{inst_key}/day/{end_date}/{start_date}"
                resp = requests.get(url, headers=headers, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    candles = data.get("data", {}).get("candles", [])
                    if candles:
                        # Upstox candle format: [timestamp, open, high, low, close, volume, oi]
                        c_df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume", "oi"])
                        c_df["timestamp"] = pd.to_datetime(c_df["timestamp"]).dt.date
                        c_df = c_df.sort_values("timestamp").set_index("timestamp")
                        price_series[sym] = c_df["close"]

            if len(price_series) == len(symbols):
                return pd.DataFrame(price_series)
        except Exception as e:
            logger.warning(f"Upstox API historical fetch error: {e}")
        return None

    def _fetch_yfinance_historical(
        self, symbols: List[str], start_date: str, end_date: str
    ) -> Optional[pd.DataFrame]:
        """Fetch historical adjusted close prices via yfinance"""
        try:
            import yfinance as yf
            # Download with auto_adjust
            data = yf.download(
                tickers=symbols,
                start=start_date,
                end=end_date,
                auto_adjust=True,
                progress=False
            )
            if data is not None and not data.empty:
                if "Close" in data:
                    close_df = data["Close"]
                else:
                    close_df = data

                if isinstance(close_df, pd.Series):
                    close_df = close_df.to_frame(name=symbols[0])

                close_df.index = pd.to_datetime(close_df.index).date
                # Filter to only requested symbols that are present
                cols = [c for c in symbols if c in close_df.columns]
                if cols:
                    return close_df[cols].ffill().dropna()
        except Exception as e:
            logger.warning(f"yfinance fetch error: {e}")
        return None

    def _generate_synthetic_prices(
        self, symbols: List[str], start_date: str, end_date: str
    ) -> pd.DataFrame:
        """
        Generate realistic synthetic Indian stock prices using Geometric Brownian Motion
        with correlated shocks based on a factor covariance matrix.
        """
        dates = pd.date_range(start=start_date, end=end_date, freq="B").date
        num_days = len(dates)
        num_assets = len(symbols)

        np.random.seed(42)

        # Baseline parameters: Annualized drift ~12%, volatility 20-35%
        annual_drift = 0.12
        daily_drift = annual_drift / 252.0
        vols = np.random.uniform(0.18, 0.32, size=num_assets)
        daily_vols = vols / np.sqrt(252.0)

        # Generate positive definite correlation matrix
        raw_corr = np.random.uniform(0.2, 0.6, size=(num_assets, num_assets))
        corr = (raw_corr + raw_corr.T) / 2.0
        np.fill_diagonal(corr, 1.0)
        # Ensure positive semi-definite
        eigenvalues, eigenvectors = np.linalg.eigh(corr)
        eigenvalues = np.maximum(eigenvalues, 1e-4)
        corr = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T
        inv_std = 1.0 / np.sqrt(np.diag(corr))
        corr = inv_std[:, None] * corr * inv_std[None, :]

        # Cholesky decomposition
        L = np.linalg.cholesky(corr)

        # Uncorrelated standard normal shocks
        uncorr_shocks = np.random.normal(0, 1, size=(num_days, num_assets))
        corr_shocks = uncorr_shocks @ L.T

        # Calculate daily log returns
        log_returns = (daily_drift - 0.5 * (daily_vols ** 2)) + daily_vols * corr_shocks

        # Initial prices around ₹1,000 - ₹3,500
        initial_prices = np.random.uniform(800.0, 3200.0, size=num_assets)
        prices = np.zeros((num_days, num_assets))
        prices[0] = initial_prices

        for t in range(1, num_days):
            prices[t] = prices[t - 1] * np.exp(log_returns[t])

        df = pd.DataFrame(prices, index=dates, columns=symbols)
        return df

    def get_live_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Get live quote (LTP, change, high, low, volume) for symbols.
        Uses Upstox API v2 if authenticated, otherwise yfinance/cache fallback.
        """
        quotes = {}

        # 1. Try Upstox API live quote
        if self.upstox_token:
            try:
                import requests
                headers = {
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.upstox_token}"
                }
                keys = [get_instrument(s).get("upstox_key", f"NSE_EQ|{s.replace('.NS', '')}") for s in symbols]
                url = f"{settings.UPSTOX_BASE_API}/market-quote/quotes?instrument_key={','.join(keys)}"
                resp = requests.get(url, headers=headers, timeout=4)
                if resp.status_code == 200:
                    data = resp.json().get("data", {})
                    for sym in symbols:
                        key = get_instrument(sym).get("upstox_key", f"NSE_EQ|{sym.replace('.NS', '')}")
                        if key in data:
                            q = data[key]
                            quotes[sym] = {
                                "ltp": float(q.get("last_price", 0.0)),
                                "open": float(q.get("ohlc", {}).get("open", 0.0)),
                                "high": float(q.get("ohlc", {}).get("high", 0.0)),
                                "low": float(q.get("ohlc", {}).get("low", 0.0)),
                                "close": float(q.get("ohlc", {}).get("close", 0.0)),
                                "volume": float(q.get("volume", 0.0)),
                                "source": "upstox_live"
                            }
                    if len(quotes) == len(symbols):
                        return quotes
            except Exception as e:
                logger.warning(f"Upstox live quote fetch failed: {e}")

        # 2. Fallback to latest historical price with realistic intra-day jitter
        hist_df = self.fetch_historical_prices(symbols, start_date="2024-01-01")
        for sym in symbols:
            if sym in hist_df.columns:
                last_price = float(hist_df[sym].iloc[-1])
                prev_price = float(hist_df[sym].iloc[-2]) if len(hist_df) > 1 else last_price
                change = last_price - prev_price
                quotes[sym] = {
                    "ltp": round(last_price, 2),
                    "change": round(change, 2),
                    "change_pct": round((change / prev_price) * 100, 2) if prev_price > 0 else 0.0,
                    "open": round(last_price * 0.998, 2),
                    "high": round(last_price * 1.012, 2),
                    "low": round(last_price * 0.991, 2),
                    "close": round(prev_price, 2),
                    "volume": 1_250_000,
                    "source": "paper_feed"
                }
            else:
                quotes[sym] = {
                    "ltp": 1500.0,
                    "change": 0.0,
                    "change_pct": 0.0,
                    "open": 1500.0,
                    "high": 1515.0,
                    "low": 1490.0,
                    "close": 1500.0,
                    "volume": 500_000,
                    "source": "paper_feed"
                }

        return quotes

    def compute_returns_and_risk(
        self, price_df: pd.DataFrame, benchmark_df: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Compute:
        - Daily log returns: r_t = ln(P_t / P_{t-1})
        - Rolling 30d & 90d volatility (annualized)
        - Correlation matrix
        - CAPM Beta against benchmark
        """
        log_returns = np.log(price_df / price_df.shift(1)).dropna()

        # Annualized rolling 30-day and 90-day volatility
        rolling_30_vol = log_returns.rolling(window=30).std() * np.sqrt(252)
        rolling_90_vol = log_returns.rolling(window=90).std() * np.sqrt(252)

        # Correlation matrix
        corr_matrix = log_returns.corr()

        # Annualized mean returns and annualized volatility
        annual_returns = log_returns.mean() * 252
        annual_volatility = log_returns.std() * np.sqrt(252)

        # CAPM Beta calculation
        betas = {}
        if benchmark_df is not None and not benchmark_df.empty:
            bm_returns = np.log(benchmark_df / benchmark_df.shift(1)).dropna()
            bm_var = float(bm_returns.var().iloc[0])
            if bm_var > 1e-8:
                aligned = pd.concat([log_returns, bm_returns], axis=1, join="inner").dropna()
                bm_col = aligned.columns[-1]
                for col in price_df.columns:
                    cov = aligned[col].cov(aligned[bm_col])
                    betas[col] = float(cov / bm_var)
        else:
            for col in price_df.columns:
                betas[col] = 1.0

        return {
            "log_returns": log_returns,
            "annual_returns": annual_returns,
            "annual_volatility": annual_volatility,
            "rolling_30_vol": rolling_30_vol,
            "rolling_90_vol": rolling_90_vol,
            "corr_matrix": corr_matrix,
            "betas": betas
        }
