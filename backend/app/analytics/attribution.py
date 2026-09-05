"""
Brinson-Hood-Beebower Attribution & Crisis Stress Testing Engine.
1. Brinson Attribution:
   - Allocation Effect: Return attributed to overweighting/underweighting sectors
   - Selection Effect: Return attributed to selecting outperforming stocks within sectors
   - Interaction Effect: Cross-product of allocation and stock picking
2. Stress Period Replay:
   - Historical simulated drawdown replay during major Indian market shocks:
     * COVID-19 Flash Crash (Feb-Mar 2020)
     * 2022 Inflation & Rate Hike Drawdown (Jan-Jun 2022)
     * 2024 Election Volatility Day (June 4, 2024)
"""

from typing import Dict, List, Any
import numpy as np
import pandas as pd
from backend.app.data.instruments import SECTOR_MAP

class PerformanceAttribution:
    @staticmethod
    def brinson_attribution(
        portfolio_weights: Dict[str, float],
        portfolio_returns: Dict[str, float],
        benchmark_weights: Dict[str, float],
        benchmark_returns: Dict[str, float],
        sector_mapping: Dict[str, str] = SECTOR_MAP
    ) -> Dict[str, Any]:
        """
        Decompose active excess return via Brinson-Hood-Beebower methodology.
        """
        all_symbols = list(set(list(portfolio_weights.keys()) + list(benchmark_weights.keys())))
        all_symbols = [s for s in all_symbols if s != "CASH"]

        # Aggregate weights and weighted returns by sector
        sectors = sorted(list(set(sector_mapping.get(s, "Other") for s in all_symbols)))

        port_sector_weights = {sec: 0.0 for sec in sectors}
        bm_sector_weights = {sec: 0.0 for sec in sectors}
        port_sector_weighted_ret = {sec: 0.0 for sec in sectors}
        bm_sector_weighted_ret = {sec: 0.0 for sec in sectors}

        for sym in all_symbols:
            sec = sector_mapping.get(sym, "Other")
            w_p = portfolio_weights.get(sym, 0.0)
            r_p = portfolio_returns.get(sym, 0.0)
            w_b = benchmark_weights.get(sym, 0.0)
            r_b = benchmark_returns.get(sym, 0.0)

            port_sector_weights[sec] += w_p
            bm_sector_weights[sec] += w_b
            port_sector_weighted_ret[sec] += w_p * r_p
            bm_sector_weighted_ret[sec] += w_b * r_b

        # Compute sector return R_s
        port_sector_ret = {}
        bm_sector_ret = {}
        for sec in sectors:
            w_p = port_sector_weights[sec]
            w_b = bm_sector_weights[sec]
            port_sector_ret[sec] = (port_sector_weighted_ret[sec] / w_p) if w_p > 1e-4 else 0.0
            bm_sector_ret[sec] = (bm_sector_weighted_ret[sec] / w_b) if w_b > 1e-4 else 0.0

        total_bm_return = sum(bm_sector_weighted_ret.values())
        total_port_return = sum(port_sector_weighted_ret.values())
        total_active_return = total_port_return - total_bm_return

        sector_breakdown = []
        tot_alloc = 0.0
        tot_select = 0.0
        tot_inter = 0.0

        for sec in sectors:
            w_p = port_sector_weights[sec]
            w_b = bm_sector_weights[sec]
            r_p = port_sector_ret[sec]
            r_b = bm_sector_ret[sec]

            alloc = (w_p - w_b) * (r_b - total_bm_return)
            select = w_b * (r_p - r_b)
            inter = (w_p - w_b) * (r_p - r_b)
            net_contrib = alloc + select + inter

            tot_alloc += alloc
            tot_select += select
            tot_inter += inter

            sector_breakdown.append({
                "sector": sec,
                "port_weight_pct": round(w_p * 100, 2),
                "bm_weight_pct": round(w_b * 100, 2),
                "port_return_pct": round(r_p * 100, 2),
                "bm_return_pct": round(r_b * 100, 2),
                "allocation_pct": round(alloc * 100, 3),
                "selection_pct": round(select * 100, 3),
                "interaction_pct": round(inter * 100, 3),
                "total_contribution_pct": round(net_contrib * 100, 3)
            })

        return {
            "total_portfolio_return_pct": round(total_port_return * 100, 2),
            "total_benchmark_return_pct": round(total_bm_return * 100, 2),
            "total_active_return_pct": round(total_active_return * 100, 2),
            "allocation_effect_pct": round(tot_alloc * 100, 3),
            "selection_effect_pct": round(tot_select * 100, 3),
            "interaction_effect_pct": round(tot_inter * 100, 3),
            "sector_breakdown": sector_breakdown
        }

    @staticmethod
    def run_crisis_stress_tests(weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Simulate portfolio shock during historic stress periods.
        """
        clean_weights = {k: v for k, v in weights.items() if k != "CASH"}
        tot_w = sum(clean_weights.values())
        if tot_w > 0:
            norm_w = {k: v / tot_w for k, v in clean_weights.items()}
        else:
            norm_w = {}

        # Sector stress factor multipliers based on historical drawdowns
        stress_scenarios = [
            {
                "id": "covid_2020",
                "name": "COVID-19 Flash Crash (Feb-Mar 2020)",
                "period": "2020-02-20 to 2020-03-24",
                "nifty_drawdown": -38.4,
                "sector_shocks": {
                    "Financial Services": -42.5,
                    "Automobile": -39.2,
                    "Energy & Oil": -37.0,
                    "Metals": -41.0,
                    "Construction": -36.5,
                    "Consumer Goods": -22.4,
                    "Information Technology": -26.8,
                    "Healthcare": -14.2,
                    "Power": -25.0,
                    "Telecommunication": -21.0,
                    "Other": -32.0
                }
            },
            {
                "id": "rate_hike_2022",
                "name": "Global Rate Hike & War Selloff (2022)",
                "period": "2022-01-15 to 2022-06-17",
                "nifty_drawdown": -18.1,
                "sector_shocks": {
                    "Information Technology": -32.4,
                    "Metals": -28.0,
                    "Financial Services": -16.5,
                    "Consumer Goods": -6.2,
                    "Automobile": +2.5,
                    "Energy & Oil": -12.0,
                    "Healthcare": -14.0,
                    "Power": -10.0,
                    "Construction": -15.0,
                    "Telecommunication": -11.0,
                    "Other": -16.0
                }
            },
            {
                "id": "election_2024",
                "name": "2024 Election Volatility Day (June 4, 2024)",
                "period": "2024-06-04",
                "nifty_drawdown": -5.9,
                "sector_shocks": {
                    "Power": -14.8,
                    "Construction": -11.5,
                    "Metals": -10.2,
                    "Financial Services": -7.8,
                    "Energy & Oil": -9.0,
                    "Automobile": -4.2,
                    "Consumer Goods": +3.5,
                    "Healthcare": -1.2,
                    "Information Technology": -0.5,
                    "Telecommunication": -5.0,
                    "Other": -6.0
                }
            }
        ]

        results = []
        for sc in stress_scenarios:
            port_loss = 0.0
            for sym, weight in norm_w.items():
                sec = SECTOR_MAP.get(sym, "Other")
                shock = sc["sector_shocks"].get(sec, sc["sector_shocks"]["Other"])
                port_loss += weight * shock

            results.append({
                "id": sc["id"],
                "name": sc["name"],
                "period": sc["period"],
                "nifty_drawdown_pct": sc["nifty_drawdown"],
                "portfolio_drawdown_pct": round(port_loss, 2),
                "resilience_delta_pct": round(port_loss - sc["nifty_drawdown"], 2),
                "is_outperforming": (port_loss > sc["nifty_drawdown"])
            })

        return results
