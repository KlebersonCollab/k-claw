#!/usr/bin/env python3
"""Wrapper to run analyze_session.py and save output to query_results.txt."""
import subprocess
import sys
import os

os.chdir("/home/kleberson/Documentos/test")

result = subprocess.run(
    [sys.executable, "analyze_session.py"],
    capture_output=True,
    text=True,
    timeout=120
)

output = result.stdout + result.stderr
print(output)

with open("query_results.txt", "w") as f:
    f.write(output)

print(f"\n--- Output saved to query_results.txt ({len(output)} bytes) ---")
