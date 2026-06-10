import unittest

from signals.models import SignalSnapshot
from strategy.regime import classify_regime


def snapshot(**overrides):
    data = {
        "timestamp": "2026-06-09T00:00:00+00:00",
        "asset": "WBNB",
        "price": 600.0,
        "volume_24h": 10_000_000.0,
        "volatility_pct": 4.0,
        "trend_score": 80.0,
        "momentum_score": 78.0,
        "sentiment_score": 65.0,
        "liquidity_score": 82.0,
        "freshness_seconds": 10,
        "risk_flags": (),
    }
    data.update(overrides)
    return SignalSnapshot(**data)


class RegimeTests(unittest.TestCase):
    def test_risk_on_when_scores_align(self):
        self.assertEqual(classify_regime(snapshot()), "risk_on")

    def test_risk_off_when_data_is_stale(self):
        self.assertEqual(classify_regime(snapshot(freshness_seconds=999)), "risk_off")

    def test_range_bound_for_mixed_but_tradeable_market(self):
        self.assertEqual(classify_regime(snapshot(trend_score=62.0, momentum_score=64.0)), "range_bound")


if __name__ == "__main__":
    unittest.main()
