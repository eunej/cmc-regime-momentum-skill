import json
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from agent.config import CONFIG
from signals.models import SignalSnapshot


CMC_SYMBOLS = {
    "WBNB": "BNB",
    "BTCB": "BTC",
    "ETH": "ETH",
}


class CmcConfigError(RuntimeError):
    pass


class CmcHttpSignalCollector:
    """CMC HTTP adapter.

    This keeps the rest of the agent on the same SignalSnapshot contract as fake mode.
    The adapter intentionally computes conservative scores from quote fields first;
    richer CMC Agent Hub / MCP skills can replace this parser later.
    """

    def __init__(self, api_key: str = CONFIG.cmc_api_key, base_url: str = CONFIG.cmc_base_url):
        if not api_key:
            raise CmcConfigError("CMC_API_KEY is required when SIGNAL_ADAPTER=cmc")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def collect(self, asset: str, cycle: int) -> SignalSnapshot:
        symbol = CMC_SYMBOLS.get(asset, asset)
        params = urlencode({"symbol": symbol, "convert": "USD"})
        url = f"{self.base_url}/v2/cryptocurrency/quotes/latest?{params}"
        request = Request(url, headers={"X-CMC_PRO_API_KEY": self.api_key, "Accept": "application/json"})
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return parse_cmc_quote(asset, payload)


def parse_cmc_quote(asset: str, payload: dict[str, Any], now: Optional[datetime] = None) -> SignalSnapshot:
    symbol = CMC_SYMBOLS.get(asset, asset)
    data = payload.get("data", {}).get(symbol)
    if isinstance(data, list):
        data = data[0] if data else None
    if not data:
        raise ValueError(f"CMC response missing data for {symbol}")

    quote = data.get("quote", {}).get("USD", {})
    price = float(quote.get("price", 0.0))
    volume = float(quote.get("volume_24h", 0.0))
    pct_1h = float(quote.get("percent_change_1h", 0.0) or 0.0)
    pct_24h = float(quote.get("percent_change_24h", 0.0) or 0.0)
    pct_7d = float(quote.get("percent_change_7d", 0.0) or 0.0)
    last_updated = quote.get("last_updated") or data.get("last_updated")
    freshness_seconds = _freshness_seconds(last_updated, now or datetime.now(timezone.utc))

    trend = _score_percent_change(pct_7d, scale=8)
    momentum = _score_percent_change((pct_1h * 2 + pct_24h) / 3, scale=5)
    sentiment = _score_percent_change(pct_24h, scale=7)
    liquidity = _score_liquidity(volume)
    volatility = min(20.0, round(abs(pct_24h) + abs(pct_1h), 2))

    flags: list[str] = []
    if freshness_seconds > CONFIG.risk.stale_data_seconds:
        flags.append("stale_data")
    if liquidity < CONFIG.risk.min_liquidity_score:
        flags.append("thin_liquidity")
    if volatility > CONFIG.risk.max_volatility_pct:
        flags.append("high_volatility")

    return SignalSnapshot(
        timestamp=(now or datetime.now(timezone.utc)).isoformat(),
        asset=asset,
        price=round(price, 8),
        volume_24h=round(volume, 2),
        volatility_pct=volatility,
        trend_score=trend,
        momentum_score=momentum,
        sentiment_score=sentiment,
        liquidity_score=liquidity,
        freshness_seconds=freshness_seconds,
        risk_flags=tuple(flags),
    )


def _score_percent_change(value: float, scale: float) -> float:
    return round(max(0.0, min(100.0, 50.0 + (value / scale * 50.0))), 2)


def _score_liquidity(volume_24h: float) -> float:
    if volume_24h >= 1_000_000_000:
        return 95.0
    if volume_24h >= 100_000_000:
        return 85.0
    if volume_24h >= 25_000_000:
        return 75.0
    if volume_24h >= 5_000_000:
        return 65.0
    return 40.0


def _freshness_seconds(last_updated: Optional[str], now: datetime) -> int:
    if not last_updated:
        return 10**9
    updated = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
    return max(0, int((now - updated).total_seconds()))
