#!/usr/bin/env python3
"""Assert the linter passes the good fixture and fails each bad one for the RIGHT rule.

A linter that fails is easy; a linter that fails for the wrong reason is a silent
hole. Each failure fixture names the rule it must trip (--expect), so a refactor
that breaks a specific check is caught here.

Usage: python tools/test_lint.py   (exit 0 iff all assertions hold)
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LINT = os.path.join(HERE, "lint.py")

PASS_FIXTURE = os.path.join(REPO, "fixtures", "pass", "synthetic-all-claims.yaml")
FAIL_CASES = [
    ("fixtures/fail/no-receipt.yaml", "EDGE_NO_RECEIPT"),
    ("fixtures/fail/inferred-no-derivation.yaml", "INFERRED_NO_DERIVATION"),
    ("fixtures/fail/eo-as-documented.yaml", "DOCUMENTED_NEEDS_WITNESS"),
]


def run(*args):
    return subprocess.run([sys.executable, LINT, *args], capture_output=True, text=True)


def main():
    failures = []

    # 1. Passing fixture must lint clean (exit 0).
    r = run("--root", PASS_FIXTURE)
    if r.returncode != 0:
        failures.append(f"PASS fixture did not lint clean:\n{r.stdout}\n{r.stderr}")
    else:
        print("ok   pass fixture lints clean")

    # 2. Each failure fixture must fail for its specific rule.
    for rel, rule in FAIL_CASES:
        path = os.path.join(REPO, rel)
        r = run("--root", path, "--expect", rule)
        if r.returncode != 0:
            failures.append(f"{rel} did not raise {rule}:\n{r.stdout}\n{r.stderr}")
        else:
            print(f"ok   {rel} fails with {rule}")

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(" -", f)
        return 1
    print("\nall linter assertions passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
