import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from agent.config import CONFIG, STATE_DIR, STATE_PATH


@dataclass
class Position:
    asset: str
    size_usd: float
    entry_price: float
    tx_hash: str


@dataclass
class AgentState:
    equity_usd: float = CONFIG.account_equity_usd
    realized_pnl_usd: float = 0.0
    daily_pnl_usd: float = 0.0
    peak_equity_usd: float = CONFIG.account_equity_usd
    kill_switch: bool = False
    last_trade_at: dict[str, str] = field(default_factory=dict)
    last_loss_at: Optional[str] = None
    positions: dict[str, Position] = field(default_factory=dict)

    @property
    def drawdown_pct(self) -> float:
        if self.peak_equity_usd <= 0:
            return 0.0
        return max(0.0, (self.peak_equity_usd - self.equity_usd) / self.peak_equity_usd * 100)

    @property
    def daily_loss_pct(self) -> float:
        if self.peak_equity_usd <= 0 or self.daily_pnl_usd >= 0:
            return 0.0
        return abs(self.daily_pnl_usd) / self.peak_equity_usd * 100

    @property
    def exposure_pct(self) -> float:
        if self.equity_usd <= 0:
            return 0.0
        exposure = sum(position.size_usd for position in self.positions.values())
        return exposure / self.equity_usd * 100

    def to_json(self) -> dict[str, Any]:
        data = asdict(self)
        data["positions"] = {asset: asdict(position) for asset, position in self.positions.items()}
        data["drawdown_pct"] = self.drawdown_pct
        data["daily_loss_pct"] = self.daily_loss_pct
        data["exposure_pct"] = self.exposure_pct
        return data


def load_state(path: Path = STATE_PATH) -> AgentState:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        return AgentState()
    data = json.loads(path.read_text(encoding="utf-8"))
    positions = {
        asset: Position(**position)
        for asset, position in data.get("positions", {}).items()
    }
    return AgentState(
        equity_usd=data.get("equity_usd", CONFIG.account_equity_usd),
        realized_pnl_usd=data.get("realized_pnl_usd", 0.0),
        daily_pnl_usd=data.get("daily_pnl_usd", 0.0),
        peak_equity_usd=data.get("peak_equity_usd", CONFIG.account_equity_usd),
        kill_switch=data.get("kill_switch", False),
        last_trade_at=data.get("last_trade_at", {}),
        last_loss_at=data.get("last_loss_at"),
        positions=positions,
    )


def save_state(state: AgentState, path: Path = STATE_PATH) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state.to_json(), indent=2, sort_keys=True), encoding="utf-8")
