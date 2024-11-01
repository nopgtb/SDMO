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

# Install
Developed on python 3.12.3, install libaries using      
```pip install -r requirements.txt```

# Usage
Excepts a csv containing targeted github projects placed into the project folder named "source.csv".  
First column should contain the projects .git link  
## External Tools
Describes expected external tools   
### RefactoringMiner
Excepts a build version of refactorminer to be found at ./RefactoringMiner/bin   
### ck
Excepts a build version of ck to be found at ./metrics/external_tools/ck.jar      
## Running
You can run the project two ways
### Run all
To execute all you can use the provided run_all script   
### Run individually
The project provides the following scripts   
github_fetcher - Clones projects from given source.csv file  
refactor_miner - runs refactorminer on the projects   
analyze_refactor_miner_reports.py - Fetches data required for submission of part 1  
calculate_metrics.py - Calculates metrics for the collected refactoring commits  
metric_visualizer.py - Provides visualization for the collected metrics  

# Code description
Brief descriptions for the code   
## metrics/*
Metric calculators can be found in metrics/*    
They are split into three parts:   
metric_* - Provides a interface for calculating and fetching metric values    
data_provider/* - Provides singeltons for calculating common values for metric_*     
external_tools/* - Interfaces to external tools   
## metric_graphing/*
Contains rudimentary graphing tools for the metrics
# Tools used calculating metrics
Metrics from COMM to SEXP are implemented using pydriller. All the data needed is provided by pydriller. Metrics from CBO to NOSI are implemented using pydriller and CK. Pydriller provides data on the files and ck provides convenient way to calculate the metrics. Data for metric HsLCOM and C3 was retrieved using pydriller. Metric HsLCOM was implemented in python due to lack of platform independence of the existing tools. Metric C3 was implemented in python using numpy,scikit and javalang due to existing tools working on .class files. Compiling files to .class files would be wasteful since all the required data is in the source code itself already.
Out of the list ComRead is missing due to lack of information on this metric.
# Metric output format
The tool puts out a json file containing an array. in this array each commit is represented by an dictionary. This dictionary contains keys "commit_hash" and "metric_*" where star represents the shorthand for the metric (example metric_COMM). If the metric_* value is None, it means that the value could not be calculated. The metric data comes in four different shapes.   
### Commit level metric
Commit level metric contains a direct value for the metric. This value can be in the form of integer,floating point or a boolean.
```
"metric_OWN":3
```
### File level metric
File level metric contains an array of dictionaries. This dictionary has the keys file and metric. File key contains the path of the file as given by pydriller. Key metric contains the value for the metric being calculated for this file. The value can be either integer, floating point, boolean or a value representing None. The value None means that the metric could not be calculated for the specific file. Some metrics might contain additional keys providing extra data.
```
"metric_OEXP":[
    {"file":"path/of/the/file/file.java", "metric":0.2}, 
    {"file":"path/of/the/file/file2.java", "metric":0.5}
]
```
### Author level metric
Currently the only author level metric EXP behaves output wise similarily as the commit level metrics. It provides a direct value for the metric. This value is in the form of a floating point.
```
"metric_EXP":4.2
```
### Class level metric
Class level metric contains an array of dictionaries. This dictionary has the keys class and metric. Key class contains the name of the class prefixed with the package path that it exists in. Key metric contains the value for the metric being calculated for this class. The value can be either integer, floating point, boolean or a value representing None. The value None means that the metric could not be calculated for the specific class.
```
"metric_C3":[
    {"class":"excomm.secret.class", "metric":1}, 
    {"class":"greater.instrumentation.class", "metric":3}
]
```