#https://pydriller.readthedocs.io/en/latest/commit.html
#diff[] struct
# -file, diff_parsed
#diff_parsed[] struct
# -added[(INT_line_num, STR_line_change)], deleted[(INT_line_num, STR_line_change)]
#mr (mined repo) struct (git url, local_paths)
# -source_git, local_path, mining_report, commit_messages, commit_diffs

from datetime import datetime
from pydriller.metrics.process.commits_count import CommitsCount # for COMM

#COMM
#The cumulative number of commits in a given file up to the considered commit. 
def calculate_metric_comm(mr, commit):
    metric = []
    files = CommitsCount(path_to_repo=mr["local_path"], to=datetime(1900, 1,1), to_commit=commit["commit_hash"]).count()
    print(files)
    for diff in commit["diff"]:
        for file in files:        
            if(file == diff["file"]):
                metric.append({"file": diff["file"], "commits": None})
    return files