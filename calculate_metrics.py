import metrics
from common import *

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
    print("rfm commits: ", len(rfm_commits))
    return rfm_commits

#Takes repository and returns metric data for its rfm commits
def get_metric_data(repository, branch, mine_all_commits):
    #Load mined refactored commit hashes
    rfm_commit_data = load_rfm_commits(repository)
    #Load and run metric calculators
    metric_calculators = metrics.run_metrics(metrics_table, repository["local_path"], branch,  rfm_commit_data, mine_all_commits)
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


input_file = relative_to_absolute("part_1_submission_index.json")
output_file = relative_to_absolute("part_2_submission_index.json")

#All commits in all branches considered?
mine_all_branches = True
#Only rfm commits considered?
mine_all_commits = False

if not file_exists(output_file):
    if file_exists(input_file):
        #Get mined commits
        repositories = read_json(input_file)
        #Create part 2 submission folder
        part_2_submission_folder = relative_to_absolute("part_2_submission")
        if makedirs_helper(part_2_submission_folder):
            #Run trough repositories
            for repository in repositories:
                print(get_timestamp(), ": processing ", repository["source_git"])
                part_2_repo_folder = part_2_submission_folder + "/" + get_repo_name(repository["source_git"])
                metric_report = part_2_repo_folder + "/rmetrics.json"
                if not file_exists(metric_report):
                    branch = None
                    if not mine_all_commits:
                        branch = get_main_branch(repository["local_path"])
                    repository_rfm_metrics = get_metric_data(repository, branch, mine_all_commits)
                    #create repo submission folder and write metrics
                    if makedirs_helper(part_2_repo_folder):
                        write_json(metric_report, repository_rfm_metrics)
                        repository["metric_report"] = metric_report    
                else:
                    repository["metric_report"] = metric_report
            write_json(output_file, repositories)
    else:
        print("Did not find input file: ", input_file)
else:
    print("Found ", output_file, " skipping")