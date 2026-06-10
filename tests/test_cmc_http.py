import unittest
from datetime import datetime, timezone

from signals.cmc_http import CmcConfigError, CmcHttpSignalCollector, parse_cmc_quote


class CmcHttpTests(unittest.TestCase):
    def test_requires_api_key(self):
        with self.assertRaises(CmcConfigError):
            CmcHttpSignalCollector(api_key="")

    def test_parses_cmc_quote_into_snapshot(self):
        payload = {
            "data": {
                "BNB": [
                    {
                        "symbol": "BNB",
                        "quote": {
                            "USD": {
                                "price": 620.1234,
                                "volume_24h": 250_000_000,
                                "percent_change_1h": 0.8,
                                "percent_change_24h": 2.5,
                                "percent_change_7d": 6.0,
                                "last_updated": "2026-06-09T06:59:00.000Z",
                            }
                        },
                    }
                ]
            }
        }
        now = datetime(2026, 6, 9, 7, 0, 0, tzinfo=timezone.utc)

        snapshot = parse_cmc_quote("WBNB", payload, now=now)

        self.assertEqual(snapshot.asset, "WBNB")
        self.assertEqual(snapshot.price, 620.1234)
        self.assertEqual(snapshot.volume_24h, 250_000_000)
        self.assertEqual(snapshot.freshness_seconds, 60)
        self.assertGreaterEqual(snapshot.liquidity_score, 80)
        self.assertGreater(snapshot.confidence, 70)
        self.assertEqual(snapshot.risk_flags, ())

    def test_flags_stale_thin_high_volatility_data(self):
        payload = {
            "data": {
                "ETH": {
                    "symbol": "ETH",
                    "quote": {
                        "USD": {
                            "price": 3600,
                            "volume_24h": 1_000_000,
                            "percent_change_1h": -5.0,
                            "percent_change_24h": -12.0,
                            "percent_change_7d": -20.0,
                            "last_updated": "2026-06-09T06:00:00.000Z",
                        }
                    },
                }
            }
        }
        now = datetime(2026, 6, 9, 7, 0, 0, tzinfo=timezone.utc)

        snapshot = parse_cmc_quote("ETH", payload, now=now)

        self.assertIn("stale_data", snapshot.risk_flags)
        self.assertIn("thin_liquidity", snapshot.risk_flags)
        self.assertIn("high_volatility", snapshot.risk_flags)


if __name__ == "__main__":
    unittest.main()

