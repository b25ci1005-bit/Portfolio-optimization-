"""
Unit tests for the Walk-Forward Backtest Engine and Indian Execution Costs.
"""

import pytest
import numpy as np
import pandas as pd
from backend.app.data.market_data import MarketDataProvider
from backend.app.backtest.engine import WalkForwardEngine
from backend.app.models.database import SessionLocal, init_db
from backend.app.execution.paper_broker import PaperBroker

@pytest.fixture
def clean_db():
    init_db()
    db = SessionLocal()
    yield db
    db.close()

def test_walk_forward_engine():
    provider = MarketDataProvider()
    symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ITC.NS"]
    
    # Generate 500 days of synthetic test data
    prices = provider._generate_synthetic_prices(symbols, "2022-01-01", "2024-01-01")
    
    engine = WalkForwardEngine(
        prices=prices,
        lookback_days=150,
        rebalance_days=21,
        include_costs=True
    )
    
    results = engine.run_backtest()
    
    assert "metrics" in results
    assert "equity_curves" in results
    assert "drawdowns" in results
    assert "Minimum Variance" in results["metrics"]
    assert "Maximum Sharpe" in results["metrics"]
    assert "Risk Parity" in results["metrics"]
    assert "Hierarchical Risk Parity" in results["metrics"]
    assert "Black-Litterman" in results["metrics"]
    assert "Equal Weight" in results["metrics"]
    assert "Nifty 50 Benchmark" in results["metrics"]

    # Verify metrics structure
    mv_metrics = results["metrics"]["Minimum Variance"]
    assert "cagr" in mv_metrics
    assert "sharpe_ratio" in mv_metrics
    assert "max_drawdown" in mv_metrics
    assert "turnover" in mv_metrics

def test_paper_broker_indian_fees(clean_db):
    broker = PaperBroker(clean_db, portfolio_id=99)
    broker.reset_portfolio(1_000_000.0)

    # 1. Buy Order: ₹1,00,000 turnover
    buy_fees = broker.calculate_indian_fees("BUY", 100_000.0)
    assert buy_fees["brokerage"] == 20.0  # Max ₹20 cap (since 0.03% of 100k = 30 > 20)
    assert buy_fees["stt"] == 0.0         # No STT on buy delivery
    assert buy_fees["stamp_duty"] > 0     # Stamp duty on buy

    # 2. Sell Order: ₹1,00,000 turnover
    sell_fees = broker.calculate_indian_fees("SELL", 100_000.0)
    assert sell_fees["brokerage"] == 20.0
    assert sell_fees["stt"] == 100.0      # 0.1% STT on sell delivery

    # 3. Market impact slippage
    slippage_pct, fill_price = broker.calculate_market_impact_slippage("BUY", 500, 2500.0)
    assert fill_price > 2500.0
    assert 0.0002 <= slippage_pct <= 0.015

    # 4. Execution of BUY order
    res = broker.execute_order("RELIANCE.NS", "BUY", 10, 2500.0)
    assert res["status"] == "FILLED"
    assert res["shares"] == 10
    assert res["fill_price"] > 0
    assert res["current_cash"] < 1_000_000.0

    # 5. Execution of SELL order
    res_sell = broker.execute_order("RELIANCE.NS", "SELL", 5, 2600.0)
    assert res_sell["status"] == "FILLED"
    assert res_sell["shares"] == 5
