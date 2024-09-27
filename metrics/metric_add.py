from os import path
from metrics.metric import Metric
from metrics.metric_helpers import *
from pydriller import ModificationType
#ADD
#The normalized (by the total number of added lines in that file since it was created) number of lines added to a given file in the considered commit
class Metric_Add(Metric):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.lines_added = {}

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_rfm_commit, rfm_commit):
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            self.lines_added[file.new_path] = self.lines_added.setdefault(file.old_path, [])
        #Add added_lines to the calculation
        self.lines_added.setdefault(file.new_path, []).append(file.added_lines)

    #Called to fetch the metric value for current commit
    def get_metric(self, previous_commit, current_commit):
        #Sum all added lines for refactored lines
        total_lines_added = []
        for rfile in current_commit["rfm_data"]["refactored_files"]:
            if rfile in self.lines_added.keys():
                total_lines_added.append({"file": rfile, "metric": sum(self.lines_added[rfile])}) 
        #Get lines added in our specific commit
        commit_lines_added = [{"file":f["new_path"], "added":len(f["diff_parsed"]["added"])} for f in current_commit["diff"]]
        #Loop and calculate normals per file
        normal_add = []
        for cla in commit_lines_added:
            for tla in total_lines_added:
                if cla["file"] and path.normpath(cla["file"]) == tla["file"]:
                    #If we only had deletions, avoid division by 0 crash
                    if tla["metric"] > 0:
                        normal_add.append({"file": tla["file"], "metric": (cla["added"] / tla["metric"])})
                    else:
                        normal_add.append({"file": tla["file"], "metric": 0})
                    break
        #Sum to commit level, normalize using normal count
        if normal_add:
            return helper_summ_to_commit_level(normal_add) / len(normal_add)
        return 0