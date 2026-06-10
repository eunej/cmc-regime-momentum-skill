import unittest

from agent.state import AgentState
from risk.engine import evaluate_risk
from signals.models import SignalSnapshot
from strategy.router import TradeIntent


def snapshot(**overrides):
    data = {
        "timestamp": "2026-06-09T00:00:00+00:00",
        "asset": "WBNB",
        "price": 600.0,
        "volume_24h": 10_000_000.0,
        "volatility_pct": 4.0,
        "trend_score": 85.0,
        "momentum_score": 80.0,
        "sentiment_score": 75.0,
        "liquidity_score": 90.0,
        "freshness_seconds": 10,
        "risk_flags": (),
    }
    data.update(overrides)
    return SignalSnapshot(**data)


def intent(**overrides):
    data = {
        "action": "buy",
        "asset": "WBNB",
        "size_usd": 50.0,
        "confidence": 82.0,
        "reason": "test",
    }
    data.update(overrides)
    return TradeIntent(**data)


class RiskEngineTests(unittest.TestCase):
    def test_approves_clean_small_trade(self):
        decision = evaluate_risk(AgentState(), snapshot(), intent())
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reason, "approved")

    def test_rejects_kill_switch(self):
        state = AgentState(kill_switch=True)
        decision = evaluate_risk(state, snapshot(), intent())
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "kill_switch")

    def test_rejects_drawdown_limit(self):
        state = AgentState(equity_usd=940.0, peak_equity_usd=1000.0)
        decision = evaluate_risk(state, snapshot(), intent())
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "drawdown")

    def test_rejects_stale_data(self):
        decision = evaluate_risk(AgentState(), snapshot(freshness_seconds=500), intent())
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "freshness")

    def test_rejects_hold_intent(self):
        decision = evaluate_risk(AgentState(), snapshot(), intent(action="hold", size_usd=0.0))
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "actionable_intent")


if __name__ == "__main__":
    unittest.main()
