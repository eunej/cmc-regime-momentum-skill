from dataclasses import asdict, dataclass

from track2.data import MarketBar
from track2.spec import REGIME_MOMENTUM_SPEC, StrategySpec


@dataclass(frozen=True)
class StrategyDecision:
    day: str
    action: str
    reason: str
    price: float
    rsi: float
    macd_histogram: float
    fear_greed: float
    volume_score: float


@dataclass(frozen=True)
class Trade:
    entry_day: str
    exit_day: str
    entry_price: float
    exit_price: float
    return_pct: float
    reason: str


@dataclass(frozen=True)
class BacktestResult:
    spec: dict
    start_equity: float
    end_equity: float
    total_return_pct: float
    buy_hold_return_pct: float
    max_drawdown_pct: float
    trades: list[dict]
    decisions: list[dict]


def decide(bar: MarketBar, in_position: bool, spec: StrategySpec = REGIME_MOMENTUM_SPEC) -> StrategyDecision:
    if in_position:
        if bar.rsi > 78:
            return _decision(bar, "exit_long", "RSI overheated above 78")
        if bar.rsi < 45:
            return _decision(bar, "exit_long", "RSI failed below 45")
        if bar.macd_histogram < 0:
            return _decision(bar, "exit_long", "MACD histogram turned negative")
        if bar.fear_greed < 35 or bar.fear_greed > 90:
            return _decision(bar, "exit_long", "Fear & Greed entered an extreme regime")
        return _decision(bar, "hold", "Position remains valid")

    if (
        52 <= bar.rsi <= 72
        and bar.macd_histogram > 0
        and 45 <= bar.fear_greed <= 82
        and bar.volume_score >= 60
    ):
        return _decision(bar, "enter_long", "RSI, MACD, Fear & Greed, and volume confirmed momentum")
    return _decision(bar, "hold", "Entry rules not aligned")


def run_backtest(bars: list[MarketBar], fee_bps: float = 10.0) -> BacktestResult:
    equity = 10_000.0
    peak = equity
    max_drawdown = 0.0
    in_position = False
    entry_day = ""
    entry_price = 0.0
    shares = 0.0
    trades: list[Trade] = []
    decisions: list[StrategyDecision] = []
    fee = fee_bps / 10_000

    for bar in bars:
        decision = decide(bar, in_position)
        decisions.append(decision)

        if decision.action == "enter_long" and not in_position:
            shares = (equity * (1 - fee)) / bar.price
            entry_price = bar.price
            entry_day = bar.day
            in_position = True
        elif decision.action == "exit_long" and in_position:
            exit_equity = shares * bar.price * (1 - fee)
            trade_return = ((bar.price * (1 - fee)) - entry_price) / entry_price * 100
            trades.append(
                Trade(
                    entry_day=entry_day,
                    exit_day=bar.day,
                    entry_price=entry_price,
                    exit_price=bar.price,
                    return_pct=round(trade_return, 2),
                    reason=decision.reason,
                )
            )
            equity = exit_equity
            shares = 0.0
            in_position = False

        mark_equity = shares * bar.price if in_position else equity
        peak = max(peak, mark_equity)
        if peak > 0:
            max_drawdown = max(max_drawdown, (peak - mark_equity) / peak * 100)

    if in_position and bars:
        final_bar = bars[-1]
        equity = shares * final_bar.price * (1 - fee)
        trades.append(
            Trade(
                entry_day=entry_day,
                exit_day=final_bar.day,
                entry_price=entry_price,
                exit_price=final_bar.price,
                return_pct=round(((final_bar.price * (1 - fee)) - entry_price) / entry_price * 100, 2),
                reason="End of backtest close",
            )
        )

    start_price = bars[0].price
    end_price = bars[-1].price
    return BacktestResult(
        spec=asdict(REGIME_MOMENTUM_SPEC),
        start_equity=10_000.0,
        end_equity=round(equity, 2),
        total_return_pct=round((equity / 10_000.0 - 1) * 100, 2),
        buy_hold_return_pct=round((end_price / start_price - 1) * 100, 2),
        max_drawdown_pct=round(max_drawdown, 2),
        trades=[asdict(trade) for trade in trades],
        decisions=[asdict(decision) for decision in decisions[-60:]],
    )


def _decision(bar: MarketBar, action: str, reason: str) -> StrategyDecision:
    return StrategyDecision(
        day=bar.day,
        action=action,
        reason=reason,
        price=bar.price,
        rsi=bar.rsi,
        macd_histogram=bar.macd_histogram,
        fear_greed=bar.fear_greed,
        volume_score=bar.volume_score,
    )

