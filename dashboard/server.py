import json
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from track2.backtest import run_backtest
from track2.data import fake_cmc_history
from track2.spec import IDEAS, REGIME_MOMENTUM_SPEC


def track2_payload(days: int = 180, seed: int = 42) -> dict:
    bars = fake_cmc_history(days=days, seed=seed)
    result = run_backtest(bars)
    return {
        "track": "Track 2. Strategy Skills",
        "goal": "Build a CMC Skill that turns market data into a backtestable trading strategy spec.",
        "ideas": IDEAS,
        "implemented": "Regime Momentum Skill",
        "spec": asdict(REGIME_MOMENTUM_SPEC),
        "backtest": asdict(result),
        "latest_bar": asdict(bars[-1]),
    }


def strategy_json_export(seed: int = 42) -> str:
    return json.dumps(track2_payload(seed=seed), indent=2, sort_keys=True)


def strategy_markdown_export(seed: int = 42) -> str:
    payload = track2_payload(seed=seed)
    spec = payload["spec"]
    backtest = payload["backtest"]
    lines = [
        f"# {spec['name']}",
        "",
        "## Summary",
        "",
        spec["summary"],
        "",
        "## CMC Inputs",
        "",
        *[f"- {item}" for item in spec["cmc_inputs"]],
        "",
        "## Entry Rules",
        "",
        *[f"- {item}" for item in spec["entry_rules"]],
        "",
        "## Exit Rules",
        "",
        *[f"- {item}" for item in spec["exit_rules"]],
        "",
        "## Risk Rules",
        "",
        *[f"- {item}" for item in spec["risk_rules"]],
        "",
        "## LLM Skill Prompt",
        "",
        "```text",
        spec["llm_skill_prompt"],
        "```",
        "",
        "## Backtest Summary",
        "",
        f"- Start equity: ${backtest['start_equity']:,.2f}",
        f"- End equity: ${backtest['end_equity']:,.2f}",
        f"- Strategy return: {backtest['total_return_pct']:.2f}%",
        f"- Buy/hold return: {backtest['buy_hold_return_pct']:.2f}%",
        f"- Edge vs buy/hold: {backtest['total_return_pct'] - backtest['buy_hold_return_pct']:.2f}%",
        f"- Max drawdown: {backtest['max_drawdown_pct']:.2f}%",
        f"- Trades: {len(backtest['trades'])}",
        "",
        "## Trades",
        "",
    ]
    if backtest["trades"]:
        lines.extend(
            f"- {trade['entry_day']} -> {trade['exit_day']}: {trade['return_pct']:.2f}% ({trade['reason']})"
            for trade in backtest["trades"]
        )
    else:
        lines.append("- No trades in this backtest.")
    lines.append("")
    return "\n".join(lines)


INDEX = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CMC Track 2 Strategy Skill</title>
  <style>
    body { margin: 0; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f6f5f0; color: #171717; }
    header { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 18px 24px; border-bottom: 1px solid #d6d3ca; background: #fff; }
    h1 { margin: 0; font-size: 20px; font-weight: 650; }
    button { border: 1px solid #171717; background: #171717; color: #fff; border-radius: 6px; padding: 9px 12px; font-size: 13px; cursor: pointer; }
    a.button { display: inline-block; border: 1px solid #171717; background: #fff; color: #171717; border-radius: 6px; padding: 9px 12px; font-size: 13px; text-decoration: none; }
    button:disabled { opacity: .55; cursor: wait; }
    main { display: grid; grid-template-columns: 390px 1fr; gap: 16px; padding: 16px; }
    section { background: #fff; border: 1px solid #d6d3ca; border-radius: 8px; padding: 14px; }
    h2 { margin: 0 0 10px; font-size: 14px; text-transform: uppercase; color: #555; }
    h3 { margin: 0 0 6px; font-size: 15px; }
    .stack { display: grid; gap: 12px; }
    .idea, .rule, .decision, .trade { border: 1px solid #ece9df; border-radius: 6px; padding: 10px; background: #fcfbf7; }
    .idea b, .rule b { display: block; font-size: 13px; margin-bottom: 4px; }
    .idea span, .rule span { display: block; font-size: 12px; color: #555; line-height: 1.35; }
    .metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }
    .metric { border: 1px solid #ece9df; border-radius: 6px; padding: 10px; background: #fcfbf7; }
    .metric span { display: block; color: #666; font-size: 12px; }
    .metric strong { display: block; margin-top: 5px; font-size: 20px; }
    .pill { display: inline-block; padding: 3px 7px; border-radius: 999px; background: #ebf5ee; color: #166534; font-size: 12px; }
    .status { min-height: 18px; font-size: 13px; color: #555; }
    .actions { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
    pre { white-space: pre-wrap; word-break: break-word; font-size: 12px; color: #333; background: #fcfbf7; border: 1px solid #ece9df; border-radius: 6px; padding: 10px; }
    .feed { display: grid; gap: 8px; max-height: 62vh; overflow: auto; }
    .decision { display: grid; grid-template-columns: 96px 84px 1fr; gap: 10px; align-items: start; font-size: 12px; }
    .decision strong { font-size: 12px; }
    @media (max-width: 860px) { main { grid-template-columns: 1fr; } .metrics { grid-template-columns: 1fr 1fr; } .decision { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <h1>CMC Strategy Skill Builder</h1>
    <div class="actions">
      <a class="button" href="/api/track2/export/json" download="cmc-regime-momentum-skill.json">Export JSON</a>
      <a class="button" href="/api/track2/export/markdown" download="cmc-regime-momentum-skill.md">Export Markdown</a>
      <button id="run-backtest" type="button">Run backtest</button>
    </div>
  </header>
  <main>
    <div class="stack">
      <section>
        <h2>Track 2 Pivot</h2>
        <div class="rule">
          <b>Deliverable</b>
          <span>A CMC Skill that turns market data into a backtestable trading strategy spec. No wallet, no execution layer, no live-trading requirement.</span>
        </div>
        <div class="rule">
          <b>What this skill does</b>
          <span>It reads CMC-style market inputs, applies deterministic entry/exit/risk rules, and outputs enter_long, exit_long, or hold with a human-readable reason.</span>
        </div>
        <div class="rule">
          <b>Why it is useful</b>
          <span>Judges can audit the strategy instead of trusting a black box: every trade, skipped entry, and exit links back to RSI, MACD, Fear & Greed, or volume quality.</span>
        </div>
        <div class="rule">
          <b>Submission artifacts</b>
          <span>Export JSON for machine-readable review or Markdown for a human-readable strategy document. Both exports use the same spec and backtest shown here.</span>
        </div>
        <div id="status" class="status" style="margin-top:10px">Ready to run the local CMC-style backtest.</div>
      </section>
      <section>
        <h2>Idea Shortlist</h2>
        <div id="ideas" class="stack"></div>
      </section>
      <section>
        <h2>Skill Prompt</h2>
        <pre id="prompt"></pre>
      </section>
    </div>
    <div class="stack">
      <section>
        <h2>Implemented Strategy</h2>
        <h3 id="strategy-name"></h3>
        <p id="strategy-summary" style="font-size:13px;color:#555;line-height:1.4"></p>
        <div class="metrics" id="metrics"></div>
      </section>
      <section>
        <h2>Rules</h2>
        <div class="metrics">
          <div><h3>Inputs</h3><div id="inputs" class="stack"></div></div>
          <div><h3>Entry</h3><div id="entry" class="stack"></div></div>
          <div><h3>Exit</h3><div id="exit" class="stack"></div></div>
          <div><h3>Risk</h3><div id="risk" class="stack"></div></div>
        </div>
      </section>
      <section>
        <h2>Recent Decisions</h2>
        <div id="decisions" class="feed"></div>
      </section>
      <section>
        <h2>Trades</h2>
        <div id="trades" class="feed"></div>
      </section>
    </div>
  </main>
  <script>
    const button = document.getElementById('run-backtest');
    const statusEl = document.getElementById('status');
    button.addEventListener('click', runBacktest);

    function pct(value) {
      const prefix = value > 0 ? '+' : '';
      return prefix + value.toFixed(2) + '%';
    }

    function backtestStatus(backtest) {
      const edge = backtest.total_return_pct - backtest.buy_hold_return_pct;
      const edgeText = edge >= 0 ? `${pct(edge)} vs buy/hold` : `${pct(edge)} vs buy/hold`;
      return `Backtest complete. ${backtest.trades.length} trades, ${pct(backtest.total_return_pct)} strategy return, ${edgeText}.`;
    }

    function ruleList(id, values) {
      document.getElementById(id).innerHTML = values.map(value => `<div class="rule"><span>${value}</span></div>`).join('');
    }

    function render(data) {
      const spec = data.spec;
      const backtest = data.backtest;
      document.getElementById('ideas').innerHTML = data.ideas.map(idea => `
        <div class="idea"><b>${idea.name}</b><span>${idea.why}</span><span><span class="pill">${idea.build}</span></span></div>
      `).join('');
      document.getElementById('strategy-name').textContent = spec.name;
      document.getElementById('strategy-summary').textContent = spec.summary;
      document.getElementById('prompt').textContent = spec.llm_skill_prompt;
      document.getElementById('metrics').innerHTML = [
        ['End Equity', '$' + backtest.end_equity.toLocaleString()],
        ['Strategy Return', pct(backtest.total_return_pct)],
        ['Buy/Hold', pct(backtest.buy_hold_return_pct)],
        ['Max Drawdown', backtest.max_drawdown_pct.toFixed(2) + '%']
      ].map(([label, value]) => `<div class="metric"><span>${label}</span><strong>${value}</strong></div>`).join('');
      ruleList('inputs', spec.cmc_inputs);
      ruleList('entry', spec.entry_rules);
      ruleList('exit', spec.exit_rules);
      ruleList('risk', spec.risk_rules);
      document.getElementById('decisions').innerHTML = backtest.decisions.slice().reverse().map(d => `
        <div class="decision"><strong>${d.day}</strong><span class="pill">${d.action}</span><span>${d.reason}<br>RSI ${d.rsi} · MACD ${d.macd_histogram} · F&G ${d.fear_greed} · Vol ${d.volume_score}</span></div>
      `).join('');
      document.getElementById('trades').innerHTML = backtest.trades.slice().reverse().map(t => `
        <div class="trade"><b>${t.entry_day} → ${t.exit_day}</b><br><span>${pct(t.return_pct)} · ${t.reason}</span></div>
      `).join('') || '<div class="trade">No trades in this run.</div>';
    }

    async function loadStatus() {
      const res = await fetch('/api/track2/status', { cache: 'no-store' });
      render(await res.json());
    }

    async function runBacktest() {
      button.disabled = true;
      button.textContent = 'Running...';
      statusEl.textContent = 'Generating fake CMC history and replaying the strategy rules...';
      try {
        const res = await fetch('/api/track2/backtest', { method: 'POST', cache: 'no-store' });
        const data = await res.json();
        render(data);
        statusEl.textContent = backtestStatus(data.backtest);
      } catch (error) {
        statusEl.textContent = 'Backtest failed: ' + error.message;
      } finally {
        button.disabled = false;
        button.textContent = 'Run backtest';
      }
    }

    loadStatus();
  </script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    backtest_seed = 42

    def do_GET(self) -> None:
        if self.path == "/":
            self._send(200, "text/html", INDEX)
            return
        if self.path == "/api/track2/status":
            self._send(200, "application/json", json.dumps(track2_payload(seed=Handler.backtest_seed)))
            return
        if self.path == "/api/track2/export/json":
            self._send_download(
                200,
                "application/json",
                strategy_json_export(seed=Handler.backtest_seed),
                "cmc-regime-momentum-skill.json",
            )
            return
        if self.path == "/api/track2/export/markdown":
            self._send_download(
                200,
                "text/markdown; charset=utf-8",
                strategy_markdown_export(seed=Handler.backtest_seed),
                "cmc-regime-momentum-skill.md",
            )
            return
        self._send(404, "text/plain", "not found")

    def do_POST(self) -> None:
        if self.path == "/api/track2/backtest":
            Handler.backtest_seed += 1
            self._send(200, "application/json", json.dumps(track2_payload(seed=Handler.backtest_seed)))
            return
        self._send(404, "text/plain", "not found")

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send(self, status: int, content_type: str, body: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def _send_download(self, status: int, content_type: str, body: str, filename: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(encoded)


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("Dashboard: http://127.0.0.1:8765")
    server.serve_forever()


if __name__ == "__main__":
    main()
