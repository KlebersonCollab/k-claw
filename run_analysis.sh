#!/bin/bash
# Wrapper script to run analyze_session.py and capture output
cd /home/kleberson/Documentos/test && python3 analyze_session.py 2>&1 | tee query_results.txt
