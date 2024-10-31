import metrics
from util import Util
from pydriller import Repository

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
    metrics.Metric_C3,
    metrics.Metric_HSLCOM
]

#Load up the available data from the part 1 files
def load_rfm_commits(repository):
    #commit_hash, commit_message
    rfm_commits = Util.read_json(repository["commit_messages"])
    #take only hashes
    rfm_commits = [commit["commit_hash"] for commit in rfm_commits]
    print("rfm commits: ", len(rfm_commits))
    return rfm_commits

#Takes repository and returns metric data for its rfm commits
def get_metric_data(repository, branch, mine_all_commits, metrics_to_run):
    #Load mined refactored commit hashes
    rfm_commit_data = load_rfm_commits(repository)
    #Load and run metric calculators
    metric_calculators = metrics.run_metrics(metrics_to_run, repository["local_path"], branch,  rfm_commit_data, not mine_all_commits)
    #Get metric data for the rfm commits
    metrics_data = []
    print(Util.get_timestamp(), ": pre calc done")
    metric_hashes = rfm_commit_data
    if mine_all_commits:
        #If we mining all commits, get their hashes
        metric_hashes = [commit.hash for commit in Repository(repository, only_in_branch=branch).traverse_commits()]
    for commit_hash in metric_hashes:
        #print(Util.get_timestamp(), ": ", commit_hash)
        rfm_commit_metrics = {"commit_hash": commit_hash}
        #Run it trought the metric calculators
        for metric_calc in metric_calculators:
            rfm_commit_metrics["metric_" + metric_calc.get_metric_name()] = metric_calculators[metric_calc].get_metric(commit_hash)
        metrics_data.append(rfm_commit_metrics)
    return metrics_data

input_file = Util.relative_to_absolute("part_1_submission_index.json")
output_file = Util.relative_to_absolute("part_2_submission_index.json")

#All commits in all branches considered?
mine_all_branches = True
#Only rfm commits considered?
mine_all_commits = False

if Util.file_exists(input_file):
    #Get mined commits
    repositories = Util.read_json(input_file)
    #Create part 2 submission folder
    part_2_submission_folder = Util.relative_to_absolute("part_2_submission")
    if Util.make_directory(part_2_submission_folder):
        #Run trough repositories
        for repository in repositories:
            print(Util.get_timestamp(), ": processing ", repository["source_git"])
            part_2_repo_folder = part_2_submission_folder + "/" + Util.get_repo_name(repository["source_git"])
            metric_report = part_2_repo_folder + "/rmetrics.json"
            if not Util.file_exists(metric_report):
                branch = None
                #If not mining all branches mine only the main branch
                if not mine_all_branches:
                    branch = Util.get_main_branch(repository["local_path"])
                repository_rfm_metrics = get_metric_data(repository, branch, mine_all_commits, metrics_table)
                #create repo submission folder and write metrics
                if Util.make_directory(part_2_repo_folder):
                    Util.write_json(metric_report, repository_rfm_metrics)
                    repository["metric_report"] = metric_report    
            else:
                print("Found complete output for repository: ", metric_report, " skipping")
                repository["metric_report"] = metric_report
        Util.write_json(output_file, repositories)
else:
    print("Did not find input file: ", input_file)
