from dataclasses import dataclass


@dataclass(frozen=True)
class StrategySpec:
    name: str
    summary: str
    cmc_inputs: tuple[str, ...]
    entry_rules: tuple[str, ...]
    exit_rules: tuple[str, ...]
    risk_rules: tuple[str, ...]
    llm_skill_prompt: str


REGIME_MOMENTUM_SPEC = StrategySpec(
    name="CMC Regime Momentum Skill",
    summary=(
        "A backtestable CMC Skill that blends RSI, MACD histogram, Fear & Greed, "
        "and volume quality into deterministic long/flat rules."
    ),
    cmc_inputs=(
        "Daily price history",
        "RSI",
        "MACD histogram",
        "Fear & Greed index",
        "24h volume or volume quality score",
    ),
    entry_rules=(
        "Enter long when RSI is between 52 and 72.",
        "MACD histogram must be positive.",
        "Fear & Greed must be between 45 and 82.",
        "Volume score must be at least 60.",
        "No entry if the strategy is already long.",
    ),
    exit_rules=(
        "Exit when RSI exceeds 78, indicating overheating.",
        "Exit when RSI falls below 45, indicating failed momentum.",
        "Exit when MACD histogram turns negative.",
        "Exit when Fear & Greed falls below 35 or rises above 90.",
    ),
    risk_rules=(
        "Long-only, no leverage.",
        "Position size is 100% of strategy equity in backtest, but the live spec recommends 25% max allocation.",
        "No new entries during extreme greed or fear regimes.",
        "Backtest includes fees on every entry and exit.",
    ),
    llm_skill_prompt=(
        "You are the CMC Regime Momentum Skill. Given CMC market data containing price, RSI, "
        "MACD histogram, Fear & Greed, and volume quality, output a deterministic strategy "
        "decision: enter_long, exit_long, or hold. Explain which rule fired. Never invent data. "
        "If data is missing or stale, output hold."
    ),
)


IDEAS = [
    {
        "name": "Regime Momentum Skill",
        "why": "Most judge-legible: blends common CMC-style indicators into clear entry/exit rules and clean backtests.",
        "build": "Implemented in this prototype.",
    },
    {
        "name": "Sentiment Divergence Skill",
        "why": "Flags when Fear & Greed/social heat diverges from price momentum, useful for contrarian setups.",
        "build": "Next variant once real CMC sentiment/social inputs are wired.",
    },
    {
        "name": "Derivatives Regime Skill",
        "why": "Switches strategy based on funding/open-interest pressure. Stronger alpha story, but needs richer data.",
        "build": "Best as a sponsor-prize extension if CMC derivatives fields are available.",
    },
]

