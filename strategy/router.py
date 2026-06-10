from dataclasses import dataclass

from agent.config import CONFIG
from signals.models import SignalSnapshot


@dataclass(frozen=True)
class TradeIntent:
    action: str
    asset: str
    size_usd: float
    confidence: float
    reason: str


def route_strategy(snapshot: SignalSnapshot, regime: str) -> TradeIntent:
    if regime != "risk_on":
        return TradeIntent(
            action="hold",
            asset=snapshot.asset,
            size_usd=0.0,
            confidence=snapshot.confidence,
            reason=f"{regime}_regime_no_trade",
        )

    size = CONFIG.account_equity_usd * (CONFIG.risk.max_single_trade_pct / 100)
    return TradeIntent(
        action="buy",
        asset=snapshot.asset,
        size_usd=round(size, 2),
        confidence=snapshot.confidence,
        reason="risk_on_guarded_momentum",
    )
