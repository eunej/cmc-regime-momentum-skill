import unittest

from track2.backtest import decide, run_backtest
from track2.data import MarketBar, fake_cmc_history


class Track2BacktestTests(unittest.TestCase):
    def test_enters_when_rules_align(self):
        bar = MarketBar(
            day="2026-01-01",
            price=100.0,
            rsi=60.0,
            macd_histogram=1.2,
            fear_greed=60.0,
            volume_score=75.0,
        )
        decision = decide(bar, in_position=False)
        self.assertEqual(decision.action, "enter_long")

    def test_exits_on_negative_macd(self):
        bar = MarketBar(
            day="2026-01-02",
            price=100.0,
            rsi=55.0,
            macd_histogram=-0.1,
            fear_greed=60.0,
            volume_score=75.0,
        )
        decision = decide(bar, in_position=True)
        self.assertEqual(decision.action, "exit_long")
        self.assertIn("MACD", decision.reason)

    def test_backtest_returns_metrics_and_decisions(self):
        result = run_backtest(fake_cmc_history(days=120, seed=4))
        self.assertEqual(result.start_equity, 10_000.0)
        self.assertGreater(len(result.decisions), 0)
        self.assertIsInstance(result.total_return_pct, float)


if __name__ == "__main__":
    unittest.main()
