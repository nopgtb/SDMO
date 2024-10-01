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





github_fetcher - Clones projects given a csv file (git_link at index 0 for each line)  
github_refactor_miner - runs refactorminer on the projects and generates report.json for them  
github_analyze_refactor_miner_reports.py - Fetches data required for submission of part 1  
  
Basic usage part 1:     
get csv for sources  (first comment of github_fetcher)    
run github_fetcher  -- outputs fetch_index.csv   
run refactor_miner -- takes in fetch_index and outputs mining_index    
run analyze_refactor_miner_reports -- takes in mining_index and outputs files required for submission of part 1    
   
Basic usage part 2:  
run calculate_metrics -- takes in part 1 submission and outputs metric data   
