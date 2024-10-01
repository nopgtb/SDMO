#todo seperate ouput foor the diffrent levels

import metrics
from os import path
from common import *
from pydriller import Repository

#list for metric calculating functions
#list can be found on the last page of the assignment
#if some are missing go ahead and implement them in metrics/ based on metric.py and add it here
metrics_table = {
    "COMM": metrics.Metric_COMM,
    "NCOMM": metrics.Metric_NCOMM,
    "ADEV": metrics.Metric_ADEV,
    "DDEV": metrics.Metric_DDEV,
    "ADD":  metrics.Metric_ADD,
    "DEL":  metrics.Metric_DEL,
    "OWN":  metrics.Metric_OWN,
    "MINOR": metrics.Metric_MINOR,
    "NADEV": metrics.Metric_NADEV,
    "NDDEV": metrics.Metric_NDDEV,
    "SCTR": metrics.Metric_SCTR,
    #"NSCTR": metrics.Metric_NSCTR,
}

#Get all unique data providers from the given metrics
def get_data_providers(metrics):
    all_providers = [metrics[m].get_data_provider() for m in metrics]
    #List of all unique providers
    unique_providers = []
    for provider in all_providers:
        if provider:
            #Is in the provider list?
            if not isinstance(provider, tuple([type(up) for up in unique_providers])):
                #no, append it
                unique_providers.append(provider)
    return unique_providers

#Runs precalculations on the given metric calculators
def run_metric_precalculations(repository, rfm_commit_data, metrics_calculators):
    data_providers = get_data_providers(metrics_calculators)
    #Start external tools and run per repository calculations
    for provider in data_providers:
        provider.reset_data()
        provider.pre_calc_run_external()
        provider.pre_calc_per_repository()

    #run precalculations on the repo. Call pre_cals for each commit and file
    for commit in Repository(repository["local_path"]).traverse_commits():
        #If we are a commit with mined refactoring data get it
        is_rfm_commit = (commit.hash in rfm_commit_data)
        rfm_commit = rfm_commit_data.get(commit.hash, None)

        #Per commit pre_calc for providers
        for provider in data_providers:
            provider.pre_calc_per_commit_exlusive(commit, is_rfm_commit, rfm_commit)

        #Per commit pre_calc for metrics to set waypoints
        for metric_calc in metrics_calculators:
            metrics_calculators[metric_calc].pre_calc_per_commit_exlusive(commit, is_rfm_commit, rfm_commit)

        #Per file pre_calc for providers
        for modified_file in commit.modified_files:
            #Per file pre_calc for providers
            for provider in data_providers:
                provider.pre_calc_per_file(modified_file, commit, is_rfm_commit, rfm_commit)
            #Per file pre_cal for metrics
            for metric_calc in metrics_calculators:
                metrics_calculators[metric_calc].pre_calc_per_file(modified_file, commit, is_rfm_commit, rfm_commit)
        
        #Per commit pre_calc inclusive for metrics to set waypoints
        for metric_calc in metrics_calculators:
            metrics_calculators[metric_calc].pre_calc_per_commit_inclusive(commit, is_rfm_commit, rfm_commit)

        #Per commit pre_calc for providers
        for provider in data_providers:
            provider.pre_calc_per_commit_inclusive(commit, is_rfm_commit, rfm_commit)
        
        #Append the pydriller commit
        if is_rfm_commit:
            rfm_commit_data[commit.hash]["pr_commit"] = commit
            
    #Wait for external tools to finish
    for provider in data_providers:
        provider.pre_calc_wait_for_external()

#Load up the available data from the part 1 files
def load_commit_data(repository):
    #commit_hash, commit_message
    rfm_commits = read_json(repository["commit_messages"])
    #lookup table for easy addition
    rfm_commits = {commit["commit_hash"]:commit for commit in rfm_commits}
    rfm_hashes = rfm_commits.keys()
    #read rf miner report. We need to get the files that had refactoring done on
    rfm_data = read_json(repository["mining_report"])
    #add rfm data
    for rfm_commit in rfm_data["commits"]:
        if rfm_commit["sha1"] in rfm_hashes:
            rfm_commits[rfm_commit["sha1"]]["rfm_data"] = {"refactored_files":list(set([path.normpath(file["filePath"]) for rf in rfm_commit["refactorings"] for file in rf["rightSideLocations"]]))}
    #add diff data
    #commit_hash, previous_commit_hash, diff:[...]
    diffs = read_json(repository["commit_diffs"])
    for diff in diffs:
        rfm_commits[diff["commit_hash"]]["previous_commit_hash"] = diff["previous_commit_hash"]
        rfm_commits[diff["commit_hash"]]["diff"] = diff["diff"]
    return rfm_commits

#Takes repository and returns metric data for its rfm commits
def get_metric_data(metrics_to_run, repository):
    #Load mining data and other commit data available
    rfm_commit_data = load_commit_data(repository)
    #If not specified run all metrics
    if not metrics_to_run:
        metrics_to_run = metrics_table.keys()
    #Build metric calculators
    metric_calculators = {}
    #Get the metric calculator objects
    for metric_to_run in metrics_to_run:
        metric_calculators[metric_to_run] = metrics_table[metric_to_run](repository)
    #Run precalculations on the metric calculators
    run_metric_precalculations(repository, rfm_commit_data, metric_calculators)
    #Get metric data for the rfm commits
    metrics_data = []
    prev_rfm_commit = None
    for commit_hash, rfm_commit in list(rfm_commit_data.items()):
        print(get_timestamp(), ": ", commit_hash)
        rfm_commit_metrics = {"commit_hash": commit_hash}
        #Run it trought the metric calculators
        for metric_calc in metric_calculators:
            rfm_commit_metrics["metric_" + str(len(rfm_commit_metrics.keys()))] = metric_calculators[metric_calc].get_metric(prev_rfm_commit, rfm_commit, rfm_commit["pr_commit"])
        metrics_data.append(rfm_commit_metrics)
        prev_rfm_commit = rfm_commit
    return metrics_data

#Get mined commits
repositories = read_csv(relative_to_absolute("part_1_submission_index.csv"), ",", {"source_git":0, "local_path":1, "mining_report":2, "commit_messages":3, "commit_diffs":4})
#Create part 2 submission folder
part_2_submission_folder = relative_to_absolute("part_2_submission")
if makedirs_helper(part_2_submission_folder):
    #if empty all metrics are calculated
    metrics_to_calculate = []
    #Run trough repositories
    for respository in repositories:
        print(get_timestamp(), ": processing ", respository["source_git"])
        repository_rfm_metrics = get_metric_data(metrics_to_calculate, respository)
        #create repo submission folder and write metrics
        part_2_repo_folder = part_2_submission_folder + "/" + get_repo_name(respository["source_git"])
        if makedirs_helper(part_2_repo_folder):
            write_json(part_2_repo_folder + "/rmetrics.json", repository_rfm_metrics)