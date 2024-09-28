from metrics.metric import Metric
from metrics.metric_helper_functions import *
from pydriller import ModificationType

#ADD
#The normalized (by the total number of added lines in that file since it was created) number of lines added to a given file in the considered commit
class Metric_ADD(Metric):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.lines_added = {}

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.lines_added[file.new_path] = self.lines_added.setdefault(file.old_path, [])
        #Add added_lines to the calculation
        self.lines_added.setdefault(file.new_path, []).append(file.added_lines)

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        #Sum all added lines for refactored lines
        total_lines_added = helper_sum_metric_per_rfm_file(cur_rfm_commit["rfm_data"]["refactored_files"], self.lines_added)
        #Get lines added in our specific commit
        commit_lines_added = [{"file":rfm_file["new_path"], "metric":len(rfm_file["diff_parsed"]["added"])} for rfm_file in cur_rfm_commit["diff"]]
        #calculate normals per file
        metric_add = helper_normalized_metric_per_rfm_file(commit_lines_added, total_lines_added)
        #Sum to commit level, normalize using normal count
        if metric_add:
            return helper_summ_to_commit_level(metric_add) / len(metric_add)
        return 0