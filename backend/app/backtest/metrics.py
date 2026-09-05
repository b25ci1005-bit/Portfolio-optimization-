"""
Quantitative Portfolio Performance Metrics Suite.
Calculates:
- CAGR (Compound Annual Growth Rate)
- Annualized Volatility
- Sharpe Ratio (Indian Rf = 6.5%)
- Downside Volatility & Sortino Ratio
- Maximum Drawdown & Calmar Ratio
- Win Rate, Daily Returns distribution, and Monthly Returns table.
"""

from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd

from backend.app.config import settings

def calculate_portfolio_metrics(
    nav_series: pd.Series,
    rf: float = settings.DEFAULT_RISK_FREE_RATE,
    turnover: float = 0.0
) -> Dict[str, Any]:
    """
    Compute comprehensive quantitative risk-adjusted performance metrics.
    """
    if len(nav_series) < 2:
        return {
            "cagr": 0.0, "annual_volatility": 0.0, "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0, "calmar_ratio": 0.0, "max_drawdown": 0.0,
            "cumulative_return": 0.0, "win_rate": 0.0, "turnover": turnover
        }

    daily_returns = nav_series.pct_change().dropna()
    num_days = len(daily_returns)

    # 1. Cumulative Return & CAGR
    start_nav = float(nav_series.iloc[0])
    end_nav = float(nav_series.iloc[-1])
    cum_return = (end_nav / start_nav) - 1.0 if start_nav > 0 else 0.0

    years = max(num_days / 252.0, 0.05)
    cagr = (end_nav / start_nav) ** (1.0 / years) - 1.0 if (start_nav > 0 and end_nav > 0) else 0.0

    # 2. Annualized Volatility
    daily_vol = float(daily_returns.std())
    annual_vol = daily_vol * np.sqrt(252.0)

    # 3. Sharpe Ratio
    sharpe = (cagr - rf) / annual_vol if annual_vol > 1e-6 else 0.0

    # 4. Downside Deviation & Sortino Ratio
    negative_returns = daily_returns[daily_returns < 0.0]
    downside_vol = float(negative_returns.std()) * np.sqrt(252.0) if len(negative_returns) > 1 else annual_vol
    sortino = (cagr - rf) / downside_vol if downside_vol > 1e-6 else 0.0

    # 5. Maximum Drawdown & Calmar Ratio
    peaks = nav_series.cummax()
    drawdowns = (nav_series - peaks) / peaks
    max_dd = float(abs(drawdowns.min())) if len(drawdowns) > 0 else 0.0
    calmar = cagr / max_dd if max_dd > 1e-6 else 0.0

    # 6. Win Rate
    positive_days = int(np.sum(daily_returns > 0))
    win_rate = positive_days / num_days if num_days > 0 else 0.0

    return {
        "cagr": round(cagr * 100, 2),
        "annual_volatility": round(annual_vol * 100, 2),
        "sharpe_ratio": round(sharpe, 2),
        "sortino_ratio": round(sortino, 2),
        "calmar_ratio": round(calmar, 2),
        "max_drawdown": round(max_dd * 100, 2),
        "cumulative_return": round(cum_return * 100, 2),
        "win_rate": round(win_rate * 100, 2),
        "turnover": round(turnover * 100, 2)
    }

def compute_drawdown_series(nav_series: pd.Series) -> pd.Series:
    """Returns underwater drawdown percentage series"""
    peaks = nav_series.cummax()
    dd = (nav_series - peaks) / peaks
    return dd * 100.0

def compute_monthly_returns(nav_series: pd.Series) -> List[Dict[str, Any]]:
    """Generates Month-by-Year returns matrix for heatmap visualization"""
    if len(nav_series) < 2:
        return []

    df = nav_series.to_frame(name="nav")
    df.index = pd.to_datetime(df.index)
    monthly_nav = df["nav"].resample("ME").last()
    monthly_ret = monthly_nav.pct_change().dropna()

    results = []
    for date, ret in monthly_ret.items():
        results.append({
            "year": int(date.year),
            "month": int(date.month),
            "return_pct": round(float(ret) * 100.0, 2)
        })

    return results
