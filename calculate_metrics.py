import metrics
from common import *
#https://github.com/mauricioaniche/ck/tree/master
#Data provider => 
    #Start process => External python script
    # => Given commit hashes and 
    #   => Extracts the files one by one at the commit
    #       => Runs the tool on them
    # => Writes json file with the given hashes
# waits => loads json file reads variables for hashes
# Metric.get_metric => gets the data provider and just uses it

#name function for metrics
#implement the run all bool
#rename rfm to something like commits of interest

#list for metric calculating functions
metrics_table = [
    metrics.Metric_COMM,
    metrics.Metric_NCOMM,
    metrics.Metric_ADEV,
    metrics.Metric_DDEV,
    metrics.Metric_ADD,
    metrics.Metric_DEL,
    metrics.Metric_OWN,
    metrics.Metric_MINOR,
    metrics.Metric_NADEV,
    metrics.Metric_NDDEV,
    metrics.Metric_OEXP,
    metrics.Metric_EXP,
    metrics.Metric_ND,
    metrics.Metric_NF,
    metrics.Metric_NS,
    metrics.Metric_ENTROPY,
    metrics.Metric_LA,
    metrics.Metric_LD,
    metrics.Metric_LT,
    metrics.Metric_FIX,
    metrics.Metric_NDEV,
    metrics.Metric_AGE,
    metrics.Metric_NUC,
    metrics.Metric_CEXP,
    metrics.Metric_REXP,
    metrics.Metric_SEXP,
    metrics.Metric_CBO,
    metrics.Metric_WMC,
    metrics.Metric_RFC,
    metrics.Metric_ELOC,
    metrics.Metric_NOM,
    metrics.Metric_NOPM,
    metrics.Metric_DIT,
    metrics.Metric_NOC,
    metrics.Metric_NOF,
    metrics.Metric_NOSF,
    metrics.Metric_NOPF,
    metrics.Metric_NOSM,
    metrics.Metric_NOSI,
]

#Load up the available data from the part 1 files
def load_rfm_commits(repository):
    #commit_hash, commit_message
    rfm_commits = read_json(repository["commit_messages"])
    #take only hashes
    rfm_commits = [commit["commit_hash"] for commit in rfm_commits]
    return rfm_commits

#Takes repository and returns metric data for its rfm commits
def get_metric_data(repository):
    #Load mined refactored commit hashes
    rfm_commit_data = load_rfm_commits(repository)
    #Load and run metric calculators
    metric_calculators = metrics.run_metrics(metrics_table, repository["local_path"], get_main_branch(repository["local_path"]),  rfm_commit_data, True)
    #Get metric data for the rfm commits
    metrics_data = []
    print(get_timestamp(), ": pre calc done")
    for commit_hash in rfm_commit_data:
        #print(get_timestamp(), ": ", commit_hash)
        rfm_commit_metrics = {"commit_hash": commit_hash}
        #Run it trought the metric calculators
        for metric_calc in metric_calculators:
            rfm_commit_metrics["metric_" + metric_calculators[metric_calc].get_metric_name()] = metric_calculators[metric_calc].get_metric(commit_hash)
        metrics_data.append(rfm_commit_metrics)
    return metrics_data

#Get mined commits
repositories = read_csv(relative_to_absolute("part_1_submission_index.csv"), ",", {"source_git":0, "local_path":1, "mining_report":2, "commit_messages":3, "commit_diffs":4})
#Create part 2 submission folder
part_2_submission_folder = relative_to_absolute("part_2_submission")
if makedirs_helper(part_2_submission_folder):
    #Run trough repositories
    for respository in repositories:
        print(get_timestamp(), ": processing ", respository["source_git"])
        repository_rfm_metrics = get_metric_data(respository)
        #create repo submission folder and write metrics
        part_2_repo_folder = part_2_submission_folder + "/" + get_repo_name(respository["source_git"])
        if makedirs_helper(part_2_repo_folder):
            write_json(part_2_repo_folder + "/rmetrics.json", repository_rfm_metrics)