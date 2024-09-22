from datetime import datetime
from pydriller.metrics.process.commits_count import CommitsCount # for COMM
from pydriller.metrics.process.contributors_count import ContributorsCount #for ADEV, DDEV
from pydriller.metrics.process.lines_count import LinesCount #for ADD, DEL

#Summs metrics into one number
def helper_summ_to_commit_level(metric):
    return sum([m["metric"] for m in metric])

#Picks metrics for given refactored files
def helper_metric_for_rf_file(file_metrics, rf_files):
    metric = []
    #Get data for files that have been refactored
    for file in file_metrics.keys():
        #Reformat here for consistency accross tools        
        if(str(file).replace("\\", "/" ) in rf_files):
            metric.append({"file": file, "metric": file_metrics[file]})
    return metric

#COMM
#The cumulative number of commits made to a file up to the considered commit starting from the previous refactoring commit
#(consider the commit with the introduction of the file as the previous commit when dealing with the first refactoring commit)
def calculate_metric_comm(mr, previous_commit, current_commit):
    try:
        #consider the commit with the introduction of the file as the previous commit when dealing with the first refactoring commit
        if not previous_commit:
            return helper_summ_to_commit_level(
                helper_metric_for_rf_file(
                    CommitsCount(path_to_repo=mr["local_path"], since=datetime(1970,1,1), to_commit=current_commit["commit_hash"]).count(),
                    current_commit["rfm_data"]["refactored_files"]
                )
            )
        #The cumulative number of commits made to a file up to the considered commit starting from the previous refactoring commit
        return helper_summ_to_commit_level(
            helper_metric_for_rf_file(
                CommitsCount(path_to_repo=mr["local_path"], from_commit=previous_commit["commit_hash"], to_commit=current_commit["commit_hash"]).count(),
                current_commit["rfm_data"]["refactored_files"]
            )
        )
    #We might see some weird git throws
    except:
        return 0

#ADEV
#The number of developers who modified a given file up to the considered commit starting from previous refactoring commit
#(consider the commit with the introduction of the file as the previous commit when dealing with the first refactoring commit).
def calculate_metric_adev(mr, previous_commit, current_commit):
    try:
        #consider the commit with the introduction of the file as the previous commit when dealing with the first refactoring commit
        if not previous_commit:
            return helper_summ_to_commit_level(
                helper_metric_for_rf_file(
                    ContributorsCount(path_to_repo=mr["local_path"], since=datetime(1970,1,1), to_commit=current_commit["commit_hash"]).count_minor(),
                    current_commit["rfm_data"]["refactored_files"]
                )
            )
        #The number of developers who modified a given file up to the considered commit starting from previous refactoring commit
        return helper_summ_to_commit_level(
            helper_metric_for_rf_file(
                ContributorsCount(path_to_repo=mr["local_path"], from_commit=previous_commit["commit_hash"], to_commit=current_commit["commit_hash"]).count_minor(),
                current_commit["rfm_data"]["refactored_files"]
            )
        )
    #We might see some weird git throws
    except:
        return 0


#DDEV
#The cumulative number of distinct developers contributed to a given file up to the considered commit starting from the point
#the file was introduced.
def calculate_metric_ddev(mr, previous_commit, current_commit):
    try:
        #The cumulative number of distinct developers contributed to a given file up to the considered commit starting from the point the file was introduced.
        return helper_summ_to_commit_level(
            helper_metric_for_rf_file(
                ContributorsCount(path_to_repo=mr["local_path"], since=datetime(1970,1,1), to_commit=current_commit["commit_hash"]).count_minor(),
                current_commit["rfm_data"]["refactored_files"]
            )
        )
    except:
        return 0

#ADD
#The normalized (by the total number of added lines in that file since it was created) number of lines added to a given file in the
#considered commit
def calculate_metric_add(mr, previous_commit, current_commit):
    rff_data = []
    try:
        #total number of added lines in that file since it was created
        rff_data = helper_metric_for_rf_file(
            LinesCount(path_to_repo=mr["local_path"], since=datetime(1970,1,1), to_commit=current_commit["commit_hash"]).count_added(),
            current_commit["rfm_data"]["refactored_files"]
        )
    except:
        rff_data = []
    #file, lines added
    diff_data = [{"file":f["file"], "added":len(f["diff_parsed"]["added"])} for f in current_commit["diff"]]
    #Loop and calculate normals per file
    normal_add = []
    for dfd in diff_data:
        for rffd in rff_data:
            if dfd["file"] == rffd["file"]:
                normal_add.append({"file": dfd["file"], "metric": (dfd["added"] / rffd["metric"])})
                break
    return helper_summ_to_commit_level(normal_add)

#DEL
#The normalized (by the total number of deleted lines in that file since it was created) number of lines removed from a given file
#in the considered commit.
def calculate_metric_del(mr, previous_commit, current_commit):
    rff_data = []
    try:
        #total number of removed lines in that file since it was created
        rff_data = helper_metric_for_rf_file(
            LinesCount(path_to_repo=mr["local_path"], since=datetime(1970,1,1), to_commit=current_commit["commit_hash"]).count_added(),
            current_commit["rfm_data"]["refactored_files"]
        )
    except:
        rff_data = []
    #file, lines removed
    diff_data = [{"file":f["file"], "removed":len(f["diff_parsed"]["deleted"])} for f in current_commit["diff"]]
    #Loop and calculate normals per file
    normal_rem = []
    for dfd in diff_data:
        for rffd in rff_data:
            if dfd["file"] == rffd["file"]:
                normal_rem.append({"file": dfd["file"], "metric": (dfd["removed"] / rffd["metric"])})
                break
    return helper_summ_to_commit_level(normal_rem)