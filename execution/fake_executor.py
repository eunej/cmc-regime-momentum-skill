from dataclasses import dataclass
from hashlib import sha256

from signals.models import SignalSnapshot
from strategy.router import TradeIntent


@dataclass(frozen=True)
class ExecutionResult:
    tx_hash: str
    status: str
    venue: str
    chain: str
    gas_usd: float
    slippage_bps: int


class FakeTwakBscExecutor:
    def execute(self, snapshot: SignalSnapshot, intent: TradeIntent) -> ExecutionResult:
        digest = sha256(f"{snapshot.timestamp}:{snapshot.asset}:{intent.size_usd}".encode("utf-8")).hexdigest()
        return ExecutionResult(
            tx_hash="0x" + digest[:64],
            status="confirmed",
            venue="pancakeswap-fake",
            chain="bsc-fake",
            gas_usd=0.08,
            slippage_bps=18,
        )
