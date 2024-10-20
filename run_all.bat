@echo off
echo Fetching
python github_fetcher.py
echo Mining
python refactor_miner.py
echo Analyzing
python analyze_refactor_miner_reports.py
echo Calculating metrics
python calculate_metrics.py