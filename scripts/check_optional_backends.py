#!/usr/bin/env python3
"""Report which optional backends are importable (no install required)."""
from __future__ import annotations

def probe(name: str, fn):
    try:
        fn()
        return name, True, ""
    except Exception as e:
        return name, False, str(e)[:80]

def main():
    checks = []
    checks.append(probe("sionna", lambda: __import__("sionna")))
    checks.append(probe("tensorflow", lambda: __import__("tensorflow")))
    for n, ok, err in checks:
        print(f"{n}: {'OK' if ok else 'MISSING'} {err}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
