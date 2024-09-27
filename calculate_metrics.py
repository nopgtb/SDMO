import metrics
from os import path
from common import *
from datetime import datetime
from pydriller import Repository
import metrics.metric_del #pip install pydriller

#list for metric calculating functions
#list can be found on the last page of the assignment
#if some are missing go ahead and implement them in metric_functions.py and add it here
metrics_table = {
    "COMM": metrics.Metric_COMM,
    "ADEV": metrics.Metric_ADEV,
    "DDEV": metrics.Metric_DDEV,
    "ADD":  metrics.Metric_Add,
    "DEL":  metrics.Metric_Del,
}

#Runs precalculations on the given metric calculators
def run_metric_precalculations(repository, rf_commit_data, metrics_calculators):
    #Per repository per_calc
    for metric_calc in metrics_calculators:
        metrics_calculators[metric_calc].pre_calc_per_repository()
    hashes = []
    #run precalculations on the repo. Call pre_cal for each commit
    for commit in Repository(repository["local_path"]).traverse_commits():
        hashes.append(commit.hash)
        #If we are a commit with mined refactoring data get it
        is_rfm_commit = (commit.hash in rf_commit_data)
        rfm_commit = rf_commit_data.get(commit.hash, None)
        #Per file pre_calc
        for modified_file in commit.modified_files:
            for metric_calc in metrics_calculators:
                metrics_calculators[metric_calc].pre_calc_per_file(modified_file, commit, is_rfm_commit, rfm_commit)
        #Per commit pre_calc
        for metric_calc in metrics_calculators:
            metrics_calculators[metric_calc].pre_calc_per_commit(commit, is_rfm_commit, rfm_commit)

#Load up the available data from the part 1 files
def load_commit_data(repository):
    #commit_hash, commit_message
    commits = read_json(repository["commit_messages"])
    #lookup table for easy addition
    commits = {commit["commit_hash"]:commit for commit in commits}
    hashes = commits.keys()
    #read rf miner report. We need to get the files that had refactoring done on
    rfm_data = read_json(repository["mining_report"])
    #add rfm data
    for rf_commit in rfm_data["commits"]:
        if rf_commit["sha1"] in hashes:
            commits[rf_commit["sha1"]]["rfm_data"] = {"refactored_files":list(set([path.normpath(file["filePath"]) for rf in rf_commit["refactorings"] for file in rf["rightSideLocations"]]))}
    #add diff data
    #commit_hash, previous_commit_hash, diff:[...]
    diffs = read_json(repository["commit_diffs"])
    for diff in diffs:
        commits[diff["commit_hash"]]["previous_commit_hash"] = diff["previous_commit_hash"]
        commits[diff["commit_hash"]]["diff"] = diff["diff"]
    return commits

#Takes repository and returns metric data for its rfm commits
def get_metric_data(metrics_to_run, repository):
    #Load mining data and other commit data available
    rfm_commit_data = load_commit_data(repository)
    #If not specified run all metrics
    if not metrics_to_run:
        metrics_to_run = metrics_table.keys()
    #Build metric calculators
    metric_calculators = {}
    #Get the metric calculator object and give it repo data
    for metric_to_run in metrics_to_run:
        metric_calculators[metric_to_run] = metrics_table[metric_to_run](repository)
    #Run precalculations on the metric calculators
    run_metric_precalculations(repository, rfm_commit_data, metric_calculators)
    #Get metric data for the rfm commits
    metrics_data = []
    previous_rfm_commit = None
    for commit_hash, rfm_commit in list(rfm_commit_data.items()):
        print(get_timestamp(), ": ", commit_hash)
        rfm_commit_metrics = {"commit_hash": commit_hash}
        #Run it trought the metric calculators
        for metric_calc in metric_calculators:
            rfm_commit_metrics["metric_" + str(len(rfm_commit_metrics.keys()))] = metric_calculators[metric_calc].get_metric(previous_rfm_commit, rfm_commit)
        metrics_data.append(rfm_commit_metrics)
        previous_rfm_commit = rfm_commit
    return metrics_data

#Get mined commits
mined_repositories = read_csv(relative_to_absolute("part_1_submission_index.csv"), ",", {"source_git":0, "local_path":1, "mining_report":2, "commit_messages":3, "commit_diffs":4})
#Create part 2 submission folder
part_2_submission_folder = relative_to_absolute("part_2_submission")
if makedirs_helper(part_2_submission_folder):
    #if empty all metrics are calculated
    metrics_to_calculate = []
    for respository in mined_repositories:
        print("processing: ", respository["source_git"])
        repository_rfm_metrics = get_metric_data(metrics_to_calculate, respository)
        #create repo submission folder and write metrics
        part_2_repo_folder = part_2_submission_folder + "/" + get_repo_name(respository["source_git"])
        makedirs_helper(part_2_repo_folder)
        write_json(part_2_repo_folder + "/rmetrics.json", repository_rfm_metrics)