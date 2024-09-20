#https://pydriller.readthedocs.io/en/latest/commit.html
#diff[] struct
# -file, diff_parsed
#diff_parsed[] struct
# -added[(INT_line_num, STR_line_change)], deleted[(INT_line_num, STR_line_change)]
#mr (mined repo) struct (git url, local_paths)
# -source_git, local_path, mining_report, commit_messages, commit_diffs

from datetime import datetime
from common import get_commit_by_hash
from pydriller.metrics.process.commits_count import CommitsCount # for COMM

#COMM
#The cumulative number of commits made to a file up to the considered commit starting from the previous refactoring commit
#(consider the commit with the introduction of the file as the previous commit when dealing with the first refactoring commit)
def calculate_metric_comm(mr, previous_commit, current_commit):
    metric = []
    files = []
    #consider the commit with the introduction of the file as the previous commit when dealing with the first refactoring commit
    if not previous_commit:
        files = CommitsCount(path_to_repo=mr["local_path"], since=datetime(1970,1,1), to_commit=current_commit["commit_hash"]).count()
    #The cumulative number of commits made to a file up to the considered commit starting from the previous refactoring commit
    else:
        files = CommitsCount(path_to_repo=mr["local_path"], from_commit=previous_commit["commit_hash"], to_commit=current_commit["commit_hash"]).count()
    #Get only data for files that have been refactored in current_commit
    for file in files.keys():        
        if(file in current_commit["rfm_data"]["refactored_files"]):
            metric.append({"file": file, "commits": files[file]})
    return files