from metrics.metric import Metric
from metrics.metric_helper_functions import *
from pydriller import ModificationType

#DEL
#The normalized (by the total number of deleted lines in that file since it was created) number of lines removed from a given file in the considered commit.
class Metric_DEL(Metric):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.lines_removed = {}

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.lines_removed[file.new_path] = self.lines_removed.setdefault(file.old_path, [])
        self.lines_removed.setdefault(file.new_path, []).append(file.deleted_lines)

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        #Sum all removed lines per refactored lines
        total_lines_removed = helper_sum_metric_per_rfm_file(cur_rfm_commit["rfm_data"]["refactored_files"], self.lines_removed)
        #Get lines removed in our specific commit
        commit_lines_removed = [{"file":rfm_file["new_path"], "metric":len(rfm_file["diff_parsed"]["deleted"])} for rfm_file in cur_rfm_commit["diff"]]
        #calculate normals per file
        metric_del = helper_normalized_metric_per_rfm_file(commit_lines_removed, total_lines_removed)
        #Sum to commit level, normalize using normal count
        if metric_del:
            return helper_summ_to_commit_level(metric_del) / len(metric_del)
        return 0