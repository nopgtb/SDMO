from datetime import datetime
from pydriller.metrics.process.commits_count import CommitsCount # for COMM
from pydriller.metrics.process.contributors_count import ContributorsCount #for ADEV, DDEV
from pydriller.metrics.process.lines_count import LinesCount #for ADD

#Picks metrics for given refactored files
def helper_metric_for_rf_file(file_metrics, rf_files):
    metric = []
    #Get data for files that have been refactored
    for file in file_metrics.keys():        
        if(file in rf_files):
            metric.append({"file": file, "commits": file_metrics[file]})
    return metric

#COMM
#The cumulative number of commits made to a file up to the considered commit starting from the previous refactoring commit
#(consider the commit with the introduction of the file as the previous commit when dealing with the first refactoring commit)
def calculate_metric_comm(mr, previous_commit, current_commit):
    #consider the commit with the introduction of the file as the previous commit when dealing with the first refactoring commit
    if not previous_commit:
        return helper_metric_for_rf_file(
            CommitsCount(path_to_repo=mr["local_path"], since=datetime(1970,1,1), to_commit=current_commit["commit_hash"]).count(),
            current_commit["rfm_data"]["refactored_files"]
        )
    #The cumulative number of commits made to a file up to the considered commit starting from the previous refactoring commit
    return helper_metric_for_rf_file(
        CommitsCount(path_to_repo=mr["local_path"], from_commit=previous_commit["commit_hash"], to_commit=current_commit["commit_hash"]).count(),
        current_commit["rfm_data"]["refactored_files"]
    )

#ADEV
#The number of developers who modified a given file up to the considered commit starting from previous refactoring commit
#(consider the commit with the introduction of the file as the previous commit when dealing with the first refactoring commit).
def calculate_metric_adev(mr, previous_commit, current_commit):
    #consider the commit with the introduction of the file as the previous commit when dealing with the first refactoring commit
    if not previous_commit:
        return helper_metric_for_rf_file(
            ContributorsCount(path_to_repo=mr["local_path"], since=datetime(1970,1,1), to_commit=current_commit["commit_hash"]).count_minor(),
            current_commit["rfm_data"]["refactored_files"]
        )
    #The number of developers who modified a given file up to the considered commit starting from previous refactoring commit
    return helper_metric_for_rf_file(
        ContributorsCount(path_to_repo=mr["local_path"], from_commit=previous_commit["commit_hash"], to_commit=current_commit["commit_hash"]).count_minor(),
        current_commit["rfm_data"]["refactored_files"]
    )

#DDEV
#The cumulative number of distinct developers contributed to a given file up to the considered commit starting from the point
#the file was introduced.
def calculate_metric_ddev(mr, previous_commit, current_commit):
    #The cumulative number of distinct developers contributed to a given file up to the considered commit starting from the point the file was introduced.
    return helper_metric_for_rf_file(
        ContributorsCount(path_to_repo=mr["local_path"], since=datetime(1970,1,1), to_commit=current_commit["commit_hash"]).count_minor(),
        current_commit["rfm_data"]["refactored_files"]
    )

#ADD
#The normalized (by the total number of added lines in that file since it was created) number of lines added to a given file in the
#considered commit
def calculate_metric_add(mr, previous_commit, current_commit):
    #total number of added lines in that file since it was created
    rff_data = helper_metric_for_rf_file(
        LinesCount(path_to_repo=mr["local_path"], since=datetime(1970,1,1), to_commit=current_commit["commit_hash"]).count_added(),
        current_commit["rfm_data"]["refactored_files"]
    )

