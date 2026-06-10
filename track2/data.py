from dataclasses import dataclass
from datetime import date, timedelta
from math import sin
from random import Random


@dataclass(frozen=True)
class MarketBar:
    day: str
    price: float
    rsi: float
    macd_histogram: float
    fear_greed: float
    volume_score: float


def fake_cmc_history(days: int = 180, seed: int = 42) -> list[MarketBar]:
    """Generate CMC-shaped daily market data for local backtesting.

    This is fake data by design. The Track 2 artifact is the strategy spec and
    backtest interface; the adapter can later swap in real CMC history.
    """
    rng = Random(seed)
    start = date(2025, 12, 12)
    price = 600.0
    bars: list[MarketBar] = []

    for i in range(days):
        regime_wave = sin(i / 17)
        drift = 0.0015 if regime_wave > 0.25 else -0.0008 if regime_wave < -0.35 else 0.0002
        shock = rng.uniform(-0.025, 0.025)
        price = max(100.0, price * (1 + drift + shock))

        momentum = max(-1.0, min(1.0, regime_wave + rng.uniform(-0.35, 0.35)))
        rsi = max(5.0, min(95.0, 50 + momentum * 28 + rng.uniform(-8, 8)))
        macd = momentum * 2.2 + rng.uniform(-0.8, 0.8)
        fear_greed = max(0.0, min(100.0, 50 + regime_wave * 35 + rng.uniform(-18, 18)))
        volume_score = max(0.0, min(100.0, 65 + abs(momentum) * 24 + rng.uniform(-18, 12)))

        bars.append(
            MarketBar(
                day=(start + timedelta(days=i)).isoformat(),
                price=round(price, 4),
                rsi=round(rsi, 2),
                macd_histogram=round(macd, 4),
                fear_greed=round(fear_greed, 2),
                volume_score=round(volume_score, 2),
            )
        )
    return bars

