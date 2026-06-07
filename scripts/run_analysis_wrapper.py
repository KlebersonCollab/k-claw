#!/usr/bin/env python3
"""Wrapper to run analyze_session.py and save output to query_results.txt."""
import subprocess
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

target_session = sys.argv[1] if len(sys.argv) > 1 else None

if not target_session:
    print("Usage: python scripts/run_analysis_wrapper.py <session_id>")
    sys.exit(1)

result = subprocess.run(
    [sys.executable, "scripts/analyze_session.py", target_session],
    capture_output=True,
    text=True,
    timeout=120
)

output = result.stdout + result.stderr
print(output)

with open("query_results.txt", "w") as f:
    f.write(output)

print(f"\n--- Output saved to query_results.txt ({len(output)} bytes) ---")
