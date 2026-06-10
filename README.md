# CMC Track 2 Strategy Skill MVP

CMC Regime Momentum Skill is a Track 2 CMC Strategy Skill. It turns market
signals into a transparent, backtestable crypto strategy spec. The deliverable
is not a live-trading bot. It is a skill that defines what data it needs, how it
interprets that data, when it enters and exits, and how its decisions perform in
a replayable backtest.

## What It Does

The skill reads market inputs that are natural to CoinMarketCap-style strategy
work:

- Price history
- RSI
- MACD histogram
- Fear & Greed
- Volume quality

It converts those inputs into one of three deterministic decisions:

- `enter_long`
- `exit_long`
- `hold`

Every decision includes the rule that fired. That matters because the strategy
is not a black box. A judge or trader can inspect each backtest decision and see
why the skill acted or refused to act.

## Strategy Thesis

The implemented strategy is a conservative regime momentum system. It only
enters when momentum is constructive but not overheated:

- RSI must be positive, but not extreme.
- MACD histogram must confirm upward momentum.
- Fear & Greed must avoid panic and euphoria zones.
- Volume quality must be strong enough to trust the move.

The skill exits when momentum fails or the market gets too crowded. This makes
the strategy intentionally simple, auditable, and easy to test across assets.

This version uses:

- A deterministic strategy spec: RSI + MACD + Fear & Greed + volume.
- A simple backtest engine with fees, trades, decisions, return, and drawdown.
- A small stdlib dashboard for judge-facing explanation.

## Dashboard

The dashboard is the judge-facing demo. It shows:

- The Track 2 deliverable framing
- Candidate strategy skill ideas
- The implemented skill prompt
- CMC inputs
- Entry, exit, and risk rules
- Backtest return, buy/hold comparison, max drawdown, and trades
- Recent decisions with rule explanations
- JSON and Markdown exports for submission artifacts

## Exports

Use the dashboard buttons to download:

- `cmc-regime-momentum-skill.json` for machine-readable evaluation.
- `cmc-regime-momentum-skill.md` for a human-readable submission document.

Both exports are generated from the same strategy/backtest payload that powers
the dashboard, so the downloaded deliverable matches what appears on screen.

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
