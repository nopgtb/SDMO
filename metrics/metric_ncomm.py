from metrics.metric import Metric
from metrics.metric_helper_functions import *
from pydriller import ModificationType

#NCOMM
#The cumulative number of commits made to a file up to the considered commit starting from the previous refactoring commit, in
#which the same set of files were changed along with the given file. (For the first refactoring commit, consider as previous commit
#the one in which the file was introduced)
class Metric_NCOMM(Metric):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.commits_per_file = {}
        self.commit_per_file_neighbours_waypoints = {}

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
            #Make a waypoint for this rfm_commit. per rfm_file, sum its neighbours commits
            self.commit_per_file_neighbours_waypoints[pr_commit.hash] = helper_make_waypoint_per_rfm_file_neigbours(
                self.commits_per_file, 
                rfm_commit["rfm_data"]["refactored_files"],
                lambda data: sum(data)
            )
            #start counting from 0
            self.commits_per_file = {}

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        #NCOMM waypoint set for current_commit
        if cur_rfm_commit["commit_hash"] in self.commit_per_file_neighbours_waypoints.keys():
            return self.commit_per_file_neighbours_waypoints[cur_rfm_commit["commit_hash"]]
        return 0