import tempfile
import unittest
from pathlib import Path

from agent.audit import AuditLog


class AuditTests(unittest.TestCase):
    def test_writes_and_reads_recent_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            audit = AuditLog(Path(tmp) / "audit.jsonl")
            audit.write("observation", {"asset": "WBNB"})
            audit.write("trade_skipped", {"reason": "risk_off"})

            events = audit.read_recent(10)
            self.assertEqual(len(events), 2)
            self.assertEqual(events[0]["type"], "observation")
            self.assertEqual(events[1]["payload"]["reason"], "risk_off")


if __name__ == "__main__":
    unittest.main()

