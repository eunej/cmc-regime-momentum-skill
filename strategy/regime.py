from signals.models import SignalSnapshot


def classify_regime(snapshot: SignalSnapshot, drawdown_pct: float = 0.0) -> str:
    if snapshot.freshness_seconds > 120:
        return "risk_off"
    if drawdown_pct >= 4.0:
        return "risk_off"
    if "high_volatility" in snapshot.risk_flags or "thin_liquidity" in snapshot.risk_flags:
        return "risk_off"
    if (
        snapshot.trend_score >= 70
        and snapshot.momentum_score >= 70
        and snapshot.sentiment_score >= 60
        and snapshot.liquidity_score >= 70
        and snapshot.volatility_pct <= 8
    ):
        return "risk_on"
    if snapshot.liquidity_score >= 70 and snapshot.volatility_pct <= 8:
        return "range_bound"
    return "risk_off"
