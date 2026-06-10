import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from time import sleep

from agent.audit import AuditLog
from agent.config import CONFIG
from agent.state import Position, load_state, save_state
from execution.fake_executor import FakeTwakBscExecutor
from risk.engine import evaluate_risk
from signals.factory import build_signal_collector
from strategy.regime import classify_regime
from strategy.router import route_strategy


def run_cycle(cycle: int, audit: AuditLog) -> None:
    state = load_state()
    collector = build_signal_collector()
    executor = FakeTwakBscExecutor()

    for asset in CONFIG.whitelist:
        snapshot = collector.collect(asset, cycle)
        audit.write("observation", asdict(snapshot))

        regime = classify_regime(snapshot, state.drawdown_pct)
        audit.write("regime_classified", {"asset": asset, "regime": regime})

        intent = route_strategy(snapshot, regime)
        audit.write("strategy_routed", asdict(intent))

        if intent.action == "hold":
            audit.write("trade_skipped", {"asset": asset, "reason": intent.reason})
            continue

        decision = evaluate_risk(state, snapshot, intent)
        audit.write("risk_evaluated", {
            "asset": asset,
            "allowed": decision.allowed,
            "reason": decision.reason,
            "checks": [asdict(check) for check in decision.checks],
        })

        if not decision.allowed:
            audit.write("risk_rejected", {"asset": asset, "reason": decision.reason})
            continue

        result = executor.execute(snapshot, intent)
        audit.write("trade_executed", {**asdict(result), "asset": asset, "size_usd": intent.size_usd})

        state.positions[asset] = Position(
            asset=asset,
            size_usd=intent.size_usd,
            entry_price=snapshot.price,
            tx_hash=result.tx_hash,
        )
        state.last_trade_at[asset] = datetime.now(timezone.utc).isoformat()
        save_state(state)
        break

    save_state(state)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local BNB Track 1 fake-market agent.")
    parser.add_argument("--cycles", type=int, default=1)
    parser.add_argument("--sleep", type=float, default=0.0)
    args = parser.parse_args()

    audit = AuditLog()
    for cycle in range(args.cycles):
        run_cycle(cycle, audit)
        if args.sleep and cycle < args.cycles - 1:
            sleep(args.sleep)


if __name__ == "__main__":
    main()
