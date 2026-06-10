from dataclasses import dataclass


@dataclass(frozen=True)
class SignalSnapshot:
    timestamp: str
    asset: str
    price: float
    volume_24h: float
    volatility_pct: float
    trend_score: float
    momentum_score: float
    sentiment_score: float
    liquidity_score: float
    freshness_seconds: int
    risk_flags: tuple[str, ...]

    @property
    def confidence(self) -> float:
        return round((self.trend_score + self.momentum_score + self.sentiment_score + self.liquidity_score) / 4, 2)

