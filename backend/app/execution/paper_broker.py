"""
Indian Paper Broker & Microstructure Execution Engine.
Simulates realistic trade fills with:
1. Indian Brokerage: min(0.03%, ₹20) per order
2. Securities Transaction Tax (STT): 0.1% on delivery sell
3. Exchange transaction charges (0.00345% NSE)
4. GST: 18% on (Brokerage + Exchange fees)
5. SEBI turnover fees (₹10/crore) + Stamp duty (0.015% on buy)
6. Square-Root Market Impact Slippage:
   Impact = sign(order) * gamma * sigma_daily * sqrt(OrderSize / ADV)
7. Real-time virtual ledger tracking cash, holdings, realized/unrealized P&L.
"""

import logging
import datetime
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.models.schema import Portfolio, Position, Order, DailyNAV, RebalanceLog

logger = logging.getLogger(__name__)

class PaperBroker:
    def __init__(self, db: Session, portfolio_id: int = 1):
        self.db = db
        self.portfolio_id = portfolio_id
        self._ensure_portfolio_exists()

    def _ensure_portfolio_exists(self) -> Portfolio:
        portfolio = self.db.query(Portfolio).filter(Portfolio.id == self.portfolio_id).first()
        if not portfolio:
            portfolio = Portfolio(
                id=self.portfolio_id,
                name=f"Portfolio #{self.portfolio_id}",
                initial_capital=settings.DEFAULT_INITIAL_CASH,
                current_cash=settings.DEFAULT_INITIAL_CASH
            )
            self.db.add(portfolio)
            self.db.commit()
            self.db.refresh(portfolio)
        return portfolio

    def calculate_indian_fees(self, order_type: str, turnover: float) -> Dict[str, float]:
        """
        Calculate complete Indian statutory and brokerage fees for equity delivery.
        """
        turnover = abs(turnover)
        if turnover <= 0:
            return {
                "brokerage": 0.0, "stt": 0.0, "exchange_fee": 0.0,
                "gst": 0.0, "sebi_charges": 0.0, "stamp_duty": 0.0, "total_fees": 0.0
            }

        # 1. Brokerage: 0.03% or ₹20 max
        brokerage = min(settings.BROKERAGE_RATE * turnover, settings.MAX_BROKERAGE_PER_ORDER)

        # 2. STT: 0.1% on sell delivery
        stt = settings.STT_SELL_DELIVERY * turnover if order_type.upper() == "SELL" else 0.0

        # 3. Exchange fee: 0.00345%
        exchange_fee = settings.EXCHANGE_TURNOVER_FEE * turnover

        # 4. GST: 18% on (brokerage + exchange fee)
        gst = settings.GST_RATE * (brokerage + exchange_fee)

        # 5. SEBI turnover charge: ₹10 per crore (0.0001%)
        sebi_charges = settings.SEBI_TURNOVER_CHARGES * turnover

        # 6. Stamp duty: 0.015% on buy turnover
        stamp_duty = settings.STAMP_DUTY_BUY * turnover if order_type.upper() == "BUY" else 0.0

        total_fees = brokerage + stt + exchange_fee + gst + sebi_charges + stamp_duty

        return {
            "brokerage": round(brokerage, 2),
            "stt": round(stt, 2),
            "exchange_fee": round(exchange_fee, 2),
            "gst": round(gst, 2),
            "sebi_charges": round(sebi_charges, 2),
            "stamp_duty": round(stamp_duty, 2),
            "total_fees": round(total_fees, 2)
        }

    def calculate_market_impact_slippage(
        self,
        order_type: str,
        order_shares: float,
        price: float,
        daily_vol: float = 0.018,
        adv_shares: float = 1_000_000.0
    ) -> Tuple[float, float]:
        """
        Square-Root Market Impact Model:
        slippage_pct = gamma * sigma_daily * sqrt(OrderSize / ADV)
        Returns (slippage_pct, fill_price)
        """
        order_shares = abs(order_shares)
        participation = max(order_shares / max(adv_shares, 100.0), 0.0)
        slippage_pct = settings.MARKET_IMPACT_GAMMA * daily_vol * np.sqrt(participation)
        # Cap slippage between 0.02% and 1.5%
        slippage_pct = float(np.clip(slippage_pct, 0.0002, 0.015))

        if order_type.upper() == "BUY":
            fill_price = price * (1.0 + slippage_pct)
        else:
            fill_price = price * (1.0 - slippage_pct)

        return round(slippage_pct, 6), round(fill_price, 2)

    def execute_order(
        self,
        symbol: str,
        order_type: str,
        shares: float,
        current_price: float,
        daily_vol: float = 0.018,
        adv: float = 1_000_000.0
    ) -> Dict[str, Any]:
        """
        Execute a simulated market order with Indian fees and slippage.
        Updates cash and position ledger atomically.
        """
        portfolio = self._ensure_portfolio_exists()
        order_type = order_type.upper()
        shares = round(abs(shares), 2)

        if shares <= 0 or current_price <= 0:
            return {"status": "REJECTED", "reason": "Invalid shares or price"}

        # Calculate slippage & fill price
        slippage_pct, fill_price = self.calculate_market_impact_slippage(
            order_type=order_type,
            order_shares=shares,
            price=current_price,
            daily_vol=daily_vol,
            adv_shares=adv
        )

        turnover = shares * fill_price
        fee_breakdown = self.calculate_indian_fees(order_type, turnover)
        total_fees = fee_breakdown["total_fees"]

        pos = self.db.query(Position).filter(
            Position.portfolio_id == self.portfolio_id,
            Position.ticker == symbol
        ).first()

        if order_type == "BUY":
            total_required = turnover + total_fees
            if portfolio.current_cash < total_required:
                # Adjust shares to fit available cash
                affordable_turnover = max(0.0, portfolio.current_cash - 50.0)
                shares = round(affordable_turnover / fill_price, 2)
                turnover = shares * fill_price
                fee_breakdown = self.calculate_indian_fees(order_type, turnover)
                total_fees = fee_breakdown["total_fees"]
                total_required = turnover + total_fees

            if shares <= 0:
                return {"status": "REJECTED", "reason": "Insufficient cash buffer"}

            portfolio.current_cash -= total_required

            if pos:
                new_shares = pos.shares + shares
                new_avg_price = ((pos.shares * pos.avg_price) + (shares * fill_price)) / new_shares
                pos.shares = new_shares
                pos.avg_price = round(new_avg_price, 2)
                pos.current_price = current_price
            else:
                pos = Position(
                    portfolio_id=self.portfolio_id,
                    ticker=symbol,
                    shares=shares,
                    avg_price=fill_price,
                    current_price=current_price
                )
                self.db.add(pos)

        elif order_type == "SELL":
            current_shares = pos.shares if pos else 0.0
            if current_shares < shares:
                shares = current_shares  # Sell all remaining

            if shares <= 0:
                return {"status": "REJECTED", "reason": "No existing shares to sell"}

            turnover = shares * fill_price
            fee_breakdown = self.calculate_indian_fees(order_type, turnover)
            total_fees = fee_breakdown["total_fees"]
            net_proceeds = turnover - total_fees

            portfolio.current_cash += net_proceeds
            pos.shares -= shares
            pos.current_price = current_price

            if pos.shares <= 1e-4:
                self.db.delete(pos)

        # Log order in database
        order_record = Order(
            portfolio_id=self.portfolio_id,
            ticker=symbol,
            order_type=order_type,
            shares=shares,
            price=current_price,
            fill_price=fill_price,
            slippage=slippage_pct,
            fees=total_fees,
            status="FILLED",
            executed_at=datetime.datetime.utcnow()
        )
        self.db.add(order_record)
        self.db.commit()

        return {
            "status": "FILLED",
            "symbol": symbol,
            "order_type": order_type,
            "shares": shares,
            "price": current_price,
            "fill_price": fill_price,
            "slippage_pct": round(slippage_pct * 100, 4),
            "fees": fee_breakdown,
            "turnover": round(turnover, 2),
            "current_cash": round(portfolio.current_cash, 2)
        }

    def execute_rebalance(
        self,
        target_weights: Dict[str, float],
        current_prices: Dict[str, float],
        optimizer_name: str = "Optimizer",
        covariance_name: str = "Covariance"
    ) -> Dict[str, Any]:
        """
        Execute full portfolio rebalancing according to target weights.
        Sells excess holdings first to generate liquidity, then purchases target underweights.
        """
        portfolio = self._ensure_portfolio_exists()
        positions = self.db.query(Position).filter(Position.portfolio_id == self.portfolio_id).all()
        pos_dict = {p.ticker: p.shares for p in positions}

        # Calculate current total NAV
        invested_val = sum(pos_dict.get(s, 0.0) * current_prices.get(s, 0.0) for s in pos_dict)
        current_nav = portfolio.current_cash + invested_val

        all_symbols = list(set(list(target_weights.keys()) + list(pos_dict.keys())))
        all_symbols = [s for s in all_symbols if s != "CASH"]

        orders_executed = []
        total_fees = 0.0

        # Step 1: Calculate target value and shares for each symbol
        trade_plan = []
        for sym in all_symbols:
            target_w = float(target_weights.get(sym, 0.0))
            price = float(current_prices.get(sym, 0.0))
            if price <= 0:
                continue

            target_val = current_nav * target_w
            target_shares = target_val / price
            curr_shares = pos_dict.get(sym, 0.0)
            delta_shares = target_shares - curr_shares

            trade_plan.append({
                "symbol": sym,
                "delta_shares": delta_shares,
                "price": price,
                "curr_shares": curr_shares,
                "target_shares": target_shares
            })

        # Step 2: Execute SELLS first to generate cash
        sells = [t for t in trade_plan if t["delta_shares"] < -0.01]
        for s in sells:
            shares_to_sell = abs(s["delta_shares"])
            res = self.execute_order(
                symbol=s["symbol"],
                order_type="SELL",
                shares=shares_to_sell,
                current_price=s["price"]
            )
            if res.get("status") == "FILLED":
                orders_executed.append(res)
                total_fees += res["fees"]["total_fees"]

        # Step 3: Execute BUYS with available cash
        buys = [t for t in trade_plan if t["delta_shares"] > 0.01]
        for b in buys:
            res = self.execute_order(
                symbol=b["symbol"],
                order_type="BUY",
                shares=b["delta_shares"],
                current_price=b["price"]
            )
            if res.get("status") == "FILLED":
                orders_executed.append(res)
                total_fees += res["fees"]["total_fees"]

        # Step 4: Record rebalance log
        import json
        rebalance_record = RebalanceLog(
            portfolio_id=self.portfolio_id,
            optimizer_used=optimizer_name,
            covariance_used=covariance_name,
            target_weights_json=json.dumps(target_weights),
            realized_turnover=sum(abs(t["delta_shares"] * t["price"]) for t in trade_plan) / (2.0 * max(current_nav, 1.0)),
            total_fees_paid=total_fees
        )
        self.db.add(rebalance_record)
        self.db.commit()

        # Step 5: Snapshot new NAV
        state = self.get_portfolio_state(current_prices)
        nav_record = DailyNAV(
            portfolio_id=self.portfolio_id,
            date=datetime.date.today().strftime("%Y-%m-%d"),
            nav=state["nav"],
            cash=state["cash"],
            invested_value=state["invested_value"]
        )
        self.db.add(nav_record)
        self.db.commit()

        return {
            "rebalance_status": "COMPLETED",
            "orders_count": len(orders_executed),
            "orders": orders_executed,
            "total_fees_paid": round(total_fees, 2),
            "state_after": state
        }

    def get_portfolio_state(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        """Fetch current portfolio valuation, holdings, and P&L"""
        portfolio = self._ensure_portfolio_exists()
        positions = self.db.query(Position).filter(Position.portfolio_id == self.portfolio_id).all()

        holdings = []
        invested_value = 0.0
        total_cost = 0.0

        for p in positions:
            price = current_prices.get(p.ticker, p.current_price)
            val = p.shares * price
            cost = p.shares * p.avg_price
            pnl = val - cost
            pnl_pct = (pnl / cost) * 100.0 if cost > 0 else 0.0

            invested_value += val
            total_cost += cost

            holdings.append({
                "symbol": p.ticker,
                "shares": round(p.shares, 2),
                "avg_price": round(p.avg_price, 2),
                "current_price": round(price, 2),
                "market_value": round(val, 2),
                "unrealized_pnl": round(pnl, 2),
                "unrealized_pnl_pct": round(pnl_pct, 2),
                "weight": 0.0  # Will calculate below
            })

        total_nav = portfolio.current_cash + invested_value
        for h in holdings:
            h["weight"] = round(h["market_value"] / total_nav, 4) if total_nav > 0 else 0.0

        total_pnl = total_nav - portfolio.initial_capital
        total_pnl_pct = (total_pnl / portfolio.initial_capital) * 100.0 if portfolio.initial_capital > 0 else 0.0

        return {
            "nav": round(total_nav, 2),
            "cash": round(portfolio.current_cash, 2),
            "invested_value": round(invested_value, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_pct": round(total_pnl_pct, 2),
            "initial_capital": round(portfolio.initial_capital, 2),
            "cash_pct": round((portfolio.current_cash / total_nav) * 100.0, 2) if total_nav > 0 else 100.0,
            "holdings": holdings
        }

    def reset_portfolio(self, initial_capital: float = settings.DEFAULT_INITIAL_CASH):
        """Reset portfolio ledger to clean cash state"""
        self.db.query(Position).filter(Position.portfolio_id == self.portfolio_id).delete()
        self.db.query(Order).filter(Order.portfolio_id == self.portfolio_id).delete()
        self.db.query(DailyNAV).filter(DailyNAV.portfolio_id == self.portfolio_id).delete()
        self.db.query(RebalanceLog).filter(RebalanceLog.portfolio_id == self.portfolio_id).delete()

        portfolio = self._ensure_portfolio_exists()
        portfolio.initial_capital = initial_capital
        portfolio.current_cash = initial_capital
        self.db.commit()
