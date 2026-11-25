"""Tests for Signed Tool Receipt Notary."""
import unittest
from signed_tool_receipt_notary.core import ToolReceiptNotary


class TestToolReceiptNotary(unittest.TestCase):
    def test_valid_chain_verifies(self):
        n = ToolReceiptNotary("k1")
        n.notarize("t1", {"a": 1}, {"ok": True})
        n.notarize("t2", {"b": 2}, {"ok": True})
        self.assertEqual(n.verify_chain(), {"valid": True, "length": 2})

    def test_tampering_breaks_chain_detection(self):
        n = ToolReceiptNotary("k1")
        n.notarize("t1", {"a": 1}, {"ok": True})
        n.notarize("t2", {"b": 2}, {"ok": True})
        n.chain[0]["tool"] = "evil_tool"
        res = n.verify_chain()
        self.assertFalse(res["valid"])
        self.assertEqual(res["broken_at_seq"], 1)
