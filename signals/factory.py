from agent.config import CONFIG
from signals.cmc_http import CmcHttpSignalCollector
from signals.collector import SignalCollector
from signals.fake_cmc import FakeCmcSignalCollector


def build_signal_collector() -> SignalCollector:
    if CONFIG.signal_adapter == "cmc":
        return CmcHttpSignalCollector()
    if CONFIG.signal_adapter == "fake":
        return FakeCmcSignalCollector()
    raise ValueError(f"Unknown SIGNAL_ADAPTER={CONFIG.signal_adapter}")
