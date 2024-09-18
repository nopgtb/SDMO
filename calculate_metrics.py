from common import relative_to_absolute, read_csv, write_csv, read_json, makedirs_helper, get_repo_name, write_json, file_exists
from metric_funtions import *

metric_table = {
    "COMM": lambda: print("") 
}

#run metric mining
def get_metrics(metrics, commit):
    #if no specific set of metrics given run all
    if not metrics:
        metrics = metric_table.keys()
    for k in metrics:
        if k in metric_table.keys():
            commit[k] = metric_table[k](commit)
    return commit

#Get mined commits
mining_data = read_csv(relative_to_absolute("part_1_submission_index.csv"), ",", {"source_git":0, "local_path":1, "mining_report":2, "commit_messages":3, "commit_diffs":4})
