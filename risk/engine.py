from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from agent.config import CONFIG, RiskConfig
from agent.state import AgentState
from signals.models import SignalSnapshot
from strategy.router import TradeIntent


@dataclass(frozen=True)
class RiskCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class RiskDecision:
    allowed: bool
    reason: str
    checks: tuple[RiskCheck, ...]


def _minutes_since(iso_timestamp: Optional[str]) -> float:
    if not iso_timestamp:
        return 10**9
    then = datetime.fromisoformat(iso_timestamp)
    now = datetime.now(timezone.utc)
    return (now - then).total_seconds() / 60


def evaluate_risk(
    state: AgentState,
    snapshot: SignalSnapshot,
    intent: TradeIntent,
    cfg: RiskConfig = CONFIG.risk,
) -> RiskDecision:
    checks = [
        RiskCheck("kill_switch", not state.kill_switch, "global kill switch must be off"),
        RiskCheck("actionable_intent", intent.action in {"buy", "sell"}, "hold intents are not executable"),
        RiskCheck("drawdown", state.drawdown_pct < cfg.max_account_drawdown_pct, f"{state.drawdown_pct:.2f}% drawdown"),
        RiskCheck("daily_loss", state.daily_loss_pct < cfg.max_daily_loss_pct, f"{state.daily_loss_pct:.2f}% daily loss"),
        RiskCheck("open_positions", len(state.positions) < cfg.max_open_positions, f"{len(state.positions)} open positions"),
        RiskCheck("single_trade_size", intent.size_usd <= state.equity_usd * cfg.max_single_trade_pct / 100, f"${intent.size_usd:.2f} trade size"),
        RiskCheck("total_exposure", state.exposure_pct + (intent.size_usd / state.equity_usd * 100) <= cfg.max_position_pct, f"{state.exposure_pct:.2f}% current exposure"),
        RiskCheck("liquidity", snapshot.liquidity_score >= cfg.min_liquidity_score, f"{snapshot.liquidity_score:.2f} liquidity score"),
        RiskCheck("volatility", snapshot.volatility_pct <= cfg.max_volatility_pct, f"{snapshot.volatility_pct:.2f}% volatility"),
        RiskCheck("confidence", intent.confidence >= cfg.min_signal_confidence, f"{intent.confidence:.2f} confidence"),
        RiskCheck("freshness", snapshot.freshness_seconds <= cfg.stale_data_seconds, f"{snapshot.freshness_seconds}s freshness"),
        RiskCheck("trade_cooldown", _minutes_since(state.last_trade_at.get(snapshot.asset)) >= cfg.trade_cooldown_minutes, "asset cooldown elapsed"),
        RiskCheck("loss_cooldown", _minutes_since(state.last_loss_at) >= cfg.loss_cooldown_minutes, "loss cooldown elapsed"),
    ]
    failed = [check for check in checks if not check.passed]
    if failed:
        return RiskDecision(False, failed[0].name, tuple(checks))
    return RiskDecision(True, "approved", tuple(checks))
