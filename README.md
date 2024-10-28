# SDMO Project 2024

![GitHub commit activity](https://img.shields.io/github/commit-activity/t/nopgtb/SDMO)
![GitHub last commit](https://img.shields.io/github/last-commit/nopgtb/SDMO)
![GitHub top language](https://img.shields.io/github/languages/top/nopgtb/SDMO)
![GitHub language count](https://img.shields.io/github/languages/count/nopgtb/SDMO)
![GitHub License](https://img.shields.io/github/license/nopgtb/SDMO)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/nopgtb/SDMO)
![GitHub repo size](https://img.shields.io/github/repo-size/nopgtb/SDMO)
![GitHub forks](https://img.shields.io/github/forks/nopgtb/SDMO)
![GitHub Repo stars](https://img.shields.io/github/stars/nopgtb/SDMO)



# Usage
Excepts a csv containing targeted github projects placed into the project folder named "source.csv".  
First column should contain the projects .git link  

### Run all
To execute all you can use the provided run_all script   
### Run individually
The project provides the following scripts   
github_fetcher - Clones projects from given source.csv file  
refactor_miner - runs refactorminer on the projects   
analyze_refactor_miner_reports.py - Fetches data required for submission of part 1  
calculate_metrics.py - Calculates metrics for the collected refactoring commits  
metric_visualizer.py - Provides visualization for the collected metrics  

# Metrics/* files
Metric calculators can be found in metrics/*    
They are split into three parts:   
metric_* - Provides a interface for calculating and fetching metric values    
data_provider/* - Provides singeltons for calculating common values for metric_*     
external_tools/* - Interfaces to external tools   