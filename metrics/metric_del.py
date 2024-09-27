from os import path
from metrics.metric import Metric
from metrics.metric_helpers import *
from pydriller import ModificationType

#DEL
#The normalized (by the total number of deleted lines in that file since it was created) number of lines removed from a given file in the considered commit.
class Metric_Del(Metric):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.lines_removed = {}

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_rfm_commit, rfm_commit):
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            self.lines_removed[file.new_path] = self.lines_removed.setdefault(file.old_path, [])
        self.lines_removed.setdefault(file.new_path, []).append(file.deleted_lines)

    #Called to fetch the metric value for current commit
    def get_metric(self, previous_commit, current_commit):
        #Sum all removed lines for refactored lines
        total_lines_removed = []
        for rfile in current_commit["rfm_data"]["refactored_files"]:
            if rfile in self.lines_removed.keys():
                total_lines_removed.append({"file": rfile, "metric": sum(self.lines_removed[rfile])}) 
        #Get lines removed in our specific commit
        commit_lines_removed = [{"file":f["new_path"], "removed":len(f["diff_parsed"]["deleted"])} for f in current_commit["diff"]]
        #Loop and calculate normals per file
        normal_del = []
        for clr in commit_lines_removed:
            for tlr in total_lines_removed:
                if clr["file"] and path.normpath(clr["file"]) == tlr["file"]:
                    #If we only had additions, avoid division by 0 crash
                    if tlr["metric"] > 0:
                        normal_del.append({"file": tlr["file"], "metric": (clr["removed"] / tlr["metric"])})
                    else:
                        normal_del.append({"file": tlr["file"], "metric": 0})
                    break
        #Sum to commit level, normalize using normal count
        if normal_del:
            return helper_summ_to_commit_level(normal_del) / len(normal_del)
        return 0