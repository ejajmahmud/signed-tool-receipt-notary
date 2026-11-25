"""CLI for Signed Tool Receipt Notary."""
import argparse
import json
from .core import ToolReceiptNotary


def main():
    parser = argparse.ArgumentParser(description="Signed Tool Receipt Notary CLI")
    parser.add_argument("--demo", action="store_true", help="Notarize and verify sample chain")
    args = parser.parse_args()

    notary = ToolReceiptNotary(secret="cli-key")
    notary.notarize("git_push", {"branch": "main"}, {"status": "ok"})
    notary.notarize("gh_release", {"tag": "v0.1.0"}, {"status": "published"})
    print(json.dumps({"chain": notary.chain, "verification": notary.verify_chain()}, indent=2))


if __name__ == "__main__":
    main()
