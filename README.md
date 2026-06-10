# CMC Track 2 Strategy Skill MVP

Local MVP for a Track 2 CMC Strategy Skill. The deliverable is a backtestable
strategy spec, not a live-trading agent.

This version uses:

- A deterministic strategy spec: RSI + MACD + Fear & Greed + volume.
- A simple backtest engine with fees, trades, decisions, return, and drawdown.
- A small stdlib dashboard for judge-facing explanation.

Run:

```bash
python3 -m dashboard.server
```

Open:

```text
http://127.0.0.1:8765
```

Run tests:

```bash
python3 -m unittest discover -s tests
```
