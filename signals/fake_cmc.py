from datetime import datetime, timezone
from random import Random

from signals.models import SignalSnapshot


class FakeCmcSignalCollector:
    def __init__(self, seed: int = 7):
        self.random = Random(seed)
        self.base_prices = {"WBNB": 620.0, "BTCB": 68000.0, "ETH": 3600.0}

    def collect(self, asset: str, cycle: int) -> SignalSnapshot:
        base = self.base_prices[asset]
        drift = 1 + (self.random.uniform(-0.4, 0.8) / 100)
        price = round(base * drift, 4)
        trend = min(100, max(0, 62 + cycle * 4 + self.random.uniform(-8, 10)))
        momentum = min(100, max(0, 64 + cycle * 3 + self.random.uniform(-10, 10)))
        sentiment = min(100, max(0, 58 + cycle * 2 + self.random.uniform(-12, 12)))
        liquidity = min(100, max(0, 76 + self.random.uniform(-6, 8)))
        volatility = max(1.0, 4.0 + self.random.uniform(-1.5, 3.0))
        flags: list[str] = []
        if volatility > 7.0:
            flags.append("high_volatility")
        if liquidity < 70:
            flags.append("thin_liquidity")
        return SignalSnapshot(
            timestamp=datetime.now(timezone.utc).isoformat(),
            asset=asset,
            price=price,
            volume_24h=round(self.random.uniform(5_000_000, 50_000_000), 2),
            volatility_pct=round(volatility, 2),
            trend_score=round(trend, 2),
            momentum_score=round(momentum, 2),
            sentiment_score=round(sentiment, 2),
            liquidity_score=round(liquidity, 2),
            freshness_seconds=self.random.randint(1, 30),
            risk_flags=tuple(flags),
        )
