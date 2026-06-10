from typing import Protocol

from signals.models import SignalSnapshot


class SignalCollector(Protocol):
    def collect(self, asset: str, cycle: int) -> SignalSnapshot:
        ...

