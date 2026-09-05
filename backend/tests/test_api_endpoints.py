"""
End-to-end integration tests for all FastAPI REST endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_root_and_health(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "ONLINE"

    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_instruments_endpoint(client):
    res = client.get("/api/instruments")
    assert res.status_code == 200
    data = res.json()
    assert "instruments" in data
    assert len(data["instruments"]) >= 25
    assert "presets" in data

def test_optimize_endpoint(client):
    payload = {
        "symbols": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ITC.NS"],
        "optimizer": "maximum_sharpe",
        "covariance": "ledoit_wolf",
        "max_asset_weight": 0.30,
        "max_sector_weight": 0.40,
        "cash_buffer": 0.02
    }
    res = client.post("/api/optimize", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "constrained_weights" in data
    assert "expected_annual_return" in data
    assert "sharpe_ratio" in data
    assert "sector_allocations" in data
    assert pytest.approx(sum(data["constrained_weights"].values()), abs=1e-2) == 1.0

def test_portfolio_state_and_rebalance(client):
    # Reset portfolio to fresh state first
    reset_res = client.post("/api/portfolio/reset")
    assert reset_res.status_code == 200

    # Check initial state
    res = client.get("/api/portfolio/state")
    assert res.status_code == 200
    data = res.json()
    assert "portfolio" in data
    assert "nav" in data["portfolio"]

    # Rebalance
    rebalance_payload = {
        "target_weights": {
            "RELIANCE.NS": 0.30,
            "TCS.NS": 0.30,
            "HDFCBANK.NS": 0.38,
            "CASH": 0.02
        },
        "optimizer_name": "Maximum Sharpe",
        "covariance_name": "Ledoit-Wolf"
    }
    res = client.post("/api/portfolio/rebalance", json=rebalance_payload)
    assert res.status_code == 200
    reb_data = res.json()
    assert reb_data["rebalance_status"] == "COMPLETED"
    assert "orders_count" in reb_data
    assert reb_data["orders_count"] > 0

    # Verify state after rebalance
    res_after = client.get("/api/portfolio/state")
    assert res_after.status_code == 200
    state_after = res_after.json()
    assert len(state_after["portfolio"]["holdings"]) > 0

def test_frontier_analytics(client):
    res = client.get("/api/analytics/frontier?symbols=RELIANCE.NS,TCS.NS,HDFCBANK.NS&covariance=ledoit_wolf")
    assert res.status_code == 200
    data = res.json()
    assert "frontier_curve" in data
    assert len(data["frontier_curve"]) > 0
    assert "capital_allocation_line" in data
    assert "tangency_portfolio" in data

def test_upstox_status(client):
    res = client.get("/api/upstox/status")
    assert res.status_code == 200
    data = res.json()
    assert "mode" in data
    assert data["mode"] in ["LIVE_UPSTOX", "PAPER_MODE"]

def test_custom_strategies(client):
    res = client.get("/api/strategies")
    assert res.status_code == 200
    data = res.json()
    assert "strategies" in data
    assert len(data["strategies"]) >= 4
    strategy_ids = [s["id"] for s in data["strategies"]]
    assert "my_custom_strategy" in strategy_ids
    assert "cross_sectional_momentum" in strategy_ids

    payload = {
        "strategy_id": "cross_sectional_momentum",
        "symbols": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ITC.NS"],
        "cash_buffer": 0.05
    }
    run_res = client.post("/api/strategies/run", json=payload)
    assert run_res.status_code == 200
    run_data = run_res.json()
    assert "weights" in run_data
    assert "expected_return" in run_data
    assert "sharpe" in run_data
    assert pytest.approx(sum(run_data["weights"].values()), abs=1e-2) == 1.0

