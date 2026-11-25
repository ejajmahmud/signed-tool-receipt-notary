"""Core hash-chained and HMAC-signed audit receipt notary for agent tool executions."""
import hashlib
import hmac
import json
import time
from typing import Any, Dict, List


class ToolReceiptNotary:
    """Maintains a tamper-evident hash chain of signed tool execution receipts."""

    def __init__(self, secret: str):
        self._secret = secret.encode("utf-8")
        self.chain: List[Dict[str, Any]] = []

    def _compute_sig(self, entry_without_sig: Dict[str, Any]) -> str:
        raw = json.dumps(entry_without_sig, sort_keys=True).encode("utf-8")
        return hmac.new(self._secret, raw, hashlib.sha256).hexdigest()

    def notarize(self, tool_name: str, args: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        prev_sig = self.chain[-1]["signature"] if self.chain else "GENESIS"
        body = {
            "seq": len(self.chain) + 1,
            "timestamp": round(time.time(), 4),
            "tool": tool_name,
            "args_hash": hashlib.sha256(json.dumps(args, sort_keys=True).encode("utf-8")).hexdigest(),
            "result_hash": hashlib.sha256(json.dumps(result, sort_keys=True).encode("utf-8")).hexdigest(),
            "prev_sig": prev_sig,
        }
        sig = self._compute_sig(body)
        receipt = {**body, "signature": sig}
        self.chain.append(receipt)
        return receipt

    def verify_chain(self) -> Dict[str, Any]:
        expected_prev = "GENESIS"
        for idx, receipt in enumerate(self.chain):
            if receipt.get("prev_sig") != expected_prev:
                return {"valid": False, "broken_at_seq": idx + 1, "reason": "broken_prev_link"}
            body = {k: v for k, v in receipt.items() if k != "signature"}
            if not hmac.compare_digest(receipt.get("signature", ""), self._compute_sig(body)):
                return {"valid": False, "broken_at_seq": idx + 1, "reason": "invalid_hmac_signature"}
            expected_prev = receipt["signature"]
        return {"valid": True, "length": len(self.chain)}
