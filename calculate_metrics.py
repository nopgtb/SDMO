from common import relative_to_absolute, read_csv, read_json, makedirs_helper, get_repo_name, write_json
from metric_funtions import *

#list for metric calculating functions
#list can be found on the last page of the assignment
#if some are missing go ahead and implement them in metric_functions.py and add it here
metric_table = {
    "COMM": lambda mr, previous_commit, current_commit:  calculate_metric_comm(mr, previous_commit, current_commit),
    "ADEV": lambda mr, previous_commit, current_commit:  calculate_metric_adev(mr, previous_commit, current_commit),
    "DDEV": lambda mr, previous_commit, current_commit:  calculate_metric_ddev(mr, previous_commit, current_commit),
}

#run metric mining
def get_metrics(metrics, mr, previous_commit, current_commit):
    #we want format commit_hash, metric_1, metric_2...
    #as foretold by the assignment
    metric_values = {"commit_hash":current_commit["commit_hash"] }
    #if no specific set of metrics given run all
    if not metrics:
        metrics = metric_table.keys()
    for k in metrics:
        if k in metric_table.keys():
            mval = metric_table[k](mr, previous_commit, current_commit)
            #for scenario where we dont want to add anything for the metric
            if mval:
                mk = "metric_" + str(len(metric_values.keys()))
                metric_values[mk] = mval
    return metric_values

#Returns needed data from the rfm data
def parse_rfm_data(data):
    rfm_data = {}
    #list of filepaths refactored in this commit
    rfm_data["refactored_files"] = list(set([file["filePath"] for rf in data["refactorings"] for file in rf["leftSideLocations"]]))
    return rfm_data


#Load up the available data from the part 1 files
def load_commit_data(mr):
    #commit_hash, commit_message
    commits = read_json(mr["commit_messages"])
    #lookup table for easy addition
    commits = {commit["commit_hash"]:commit for commit in commits}
    hashes = commits.keys()
    #read rf miner report. We need to get the files that had refactoring done on
    rfm_data = read_json(mr["mining_report"])
    #add rfm data
    for rf_commit in rfm_data["commits"]:
        if rf_commit["sha1"] in hashes:
            commits[rf_commit["sha1"]]["rfm_data"] = parse_rfm_data(rf_commit)
    #add diff data
    #commit_hash, previous_commit_hash, diff:[...]
    diffs = read_json(mr["commit_diffs"])
    for diff in diffs:
        commits[diff["commit_hash"]]["previous_commit_hash"] = diff["previous_commit_hash"]
        commits[diff["commit_hash"]]["diff"] = diff["diff"]
    #turns us back into a nice array
    return [commits[key] for key in commits.keys()]

#Get mined commits
mining_data = read_csv(relative_to_absolute("part_1_submission_index.csv"), ",", {"source_git":0, "local_path":1, "mining_report":2, "commit_messages":3, "commit_diffs":4})
#Create part 2 submission folder
part_2_submission_folder = relative_to_absolute("part_2_submission")
makedirs_helper(part_2_submission_folder)

for mr in mining_data:
    print("processing: ", mr["source_git"])
    #load commit data and run them trough the metric functions
    commits = load_commit_data(mr)
    metrics = []
    previous_commit = None
    for commit in commits:
        metrics.append(get_metrics(None, mr, previous_commit, commit))
        previous_commit = commit
    #create repo submission folder and write metrics
    part_2_repo_folder = part_2_submission_folder + "/" + get_repo_name(mr["source_git"])
    makedirs_helper(part_2_repo_folder)
    write_json(part_2_repo_folder + "/rmetrics.json", metrics)

