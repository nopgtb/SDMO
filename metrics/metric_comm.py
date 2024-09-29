from metrics.metric import Metric
from metrics.metric_helper_functions import *
from pydriller import ModificationType

#COMM
#The cumulative number of commits made to a file up to the considered commit starting from the previous refactoring commit
#(consider the commit with the introduction of the file as the previous commit when dealing with the first refactoring commit)
class Metric_COMM(Metric):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.commits_per_file = {}
        self.commit_per_file_waypoints = {}

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.commits_per_file[file.new_path] = self.commits_per_file.setdefault(file.old_path, [])
        #Add commit to the file calc
        self.commits_per_file.setdefault(file.new_path, []).append(1)

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, pr_commit, is_rfm_commit, rfm_commit):
        if is_rfm_commit:
            #Make a waypoint for this rfm_commit. sum of data per rfm_file
            self.commit_per_file_waypoints[pr_commit.hash] = helper_make_waypoint_per_rfm_file(
                self.commits_per_file, 
                rfm_commit["rfm_data"]["refactored_files"],
                lambda data: sum(data)
            )
            #start counting from 0
            self.commits_per_file = {}

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        #COMM waypoint set for current_commit
        if cur_rfm_commit["commit_hash"] in self.commit_per_file_waypoints.keys():
            return helper_summ_to_commit_level(self.commit_per_file_waypoints[cur_rfm_commit["commit_hash"]])
        return 0