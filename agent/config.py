from dataclasses import dataclass
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / "runtime"
AUDIT_LOG_PATH = STATE_DIR / "audit.jsonl"
STATE_PATH = STATE_DIR / "state.json"


@dataclass(frozen=True)
class RiskConfig:
    max_account_drawdown_pct: float = 5.0
    max_daily_loss_pct: float = 2.0
    max_position_pct: float = 10.0
    max_single_trade_pct: float = 5.0
    max_open_positions: int = 2
    min_liquidity_score: float = 70.0
    max_slippage_bps: int = 50
    max_volatility_pct: float = 8.0
    min_signal_confidence: float = 75.0
    trade_cooldown_minutes: int = 15
    loss_cooldown_minutes: int = 60
    stale_data_seconds: int = 120


@dataclass(frozen=True)
class AgentConfig:
    account_equity_usd: float = 1000.0
    quote_asset: str = "USDT"
    whitelist: tuple[str, ...] = ("WBNB", "BTCB", "ETH")
    signal_adapter: str = os.getenv("SIGNAL_ADAPTER", "fake")
    cmc_api_key: str = os.getenv("CMC_API_KEY", "")
    cmc_base_url: str = os.getenv("CMC_BASE_URL", "https://pro-api.coinmarketcap.com")
    risk: RiskConfig = RiskConfig()


CONFIG = AgentConfig()
