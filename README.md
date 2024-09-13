github_search - usefull if you can use the API for the bonus of A, sent a email about this no answer yet  
option_b_decode_git_urls - Decode the git urls from the sonar_measures csv  
github_fetcher - Clones projects given a csv file (git_link at index 0 for each line)  
github_refactor_miner - runs refactorminer on the projects and generates report.json for them  
github_analyze_refactor_miner_reports.py - Fetches data required for submission of part 1  
  
Basic usage:  
get csv for sources  (first comment of github_fetcher)  
run github_fetcher  -- outputs fetch_index.csv
run github_refactor_miner -- takes in fetch_index and outputs mining_index  
run github_analyze_refactor_miner_reports -- takes in mining_index and outputs files required for submission of part 1  