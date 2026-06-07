#!/bin/bash
# Wrapper script to run analyze_session.py and capture output
# Should be run from project root: bash scripts/run_analysis.sh <session_id>

PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)
SESSION_ID=$1

if [ -z "$SESSION_ID" ]; then
    echo "Usage: bash scripts/run_analysis.sh <session_id>"
    python3 "$PROJECT_ROOT/scripts/analyze_session.py"
    exit 1
fi

cd "$PROJECT_ROOT" && python3 scripts/analyze_session.py "$SESSION_ID" 2>&1 | tee query_results.txt
