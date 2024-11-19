@echo off
echo Fetching
python github_fetcher.py
echo Mining
python refactor_miner.py
echo Analyzing
python analyze_refactor_miner_reports.py
echo Calculating metrics
python calculate_metrics.py
echo Graphing metrics
python metric_visualizer.py
echo Metric Sd analysis
python metric_sd.py