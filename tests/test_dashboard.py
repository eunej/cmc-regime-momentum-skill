import json
import unittest

from dashboard.server import INDEX, strategy_json_export, strategy_markdown_export, track2_payload


class DashboardTests(unittest.TestCase):
    def test_index_explains_track2_backtest(self):
        self.assertIn("CMC Strategy Skill Builder", INDEX)
        self.assertIn("Run backtest", INDEX)
        self.assertIn("Export JSON", INDEX)
        self.assertIn("Export Markdown", INDEX)
        self.assertIn("Track 2 Pivot", INDEX)
        self.assertIn("backtestStatus", INDEX)
        self.assertIn("Max Drawdown", INDEX)
        self.assertIn("backtest.max_drawdown_pct.toFixed(2)", INDEX)

    def test_track2_payload_is_json_serializable(self):
        body = json.dumps(track2_payload(days=30, seed=1))
        self.assertIn("Track 2. Strategy Skills", body)
        self.assertIn("Regime Momentum Skill", body)

    def test_json_export_contains_spec_and_backtest(self):
        data = json.loads(strategy_json_export(seed=1))
        self.assertEqual(data["spec"]["name"], "CMC Regime Momentum Skill")
        self.assertIn("backtest", data)
        self.assertIn("trades", data["backtest"])

    def test_markdown_export_contains_submission_sections(self):
        markdown = strategy_markdown_export(seed=1)
        self.assertIn("# CMC Regime Momentum Skill", markdown)
        self.assertIn("## LLM Skill Prompt", markdown)
        self.assertIn("## Backtest Summary", markdown)
        self.assertIn("Edge vs buy/hold", markdown)


if __name__ == "__main__":
    unittest.main()
