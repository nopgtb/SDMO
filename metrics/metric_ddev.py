from metrics.metric import Metric
from metrics.metric_helper_functions import *
from pydriller import ModificationType

#DDEV
#The cumulative number of distinct developers contributed to a given file up to the considered commit starting from the point the file was introduced.
class Metric_DDEV(Metric):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.contributors_per_file = {}
        self.contributors_per_file_waypoints = {}

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.contributors_per_file[file.new_path] = self.contributors_per_file.setdefault(file.old_path, {})
        #Per path have dict of authors with number of lines contributed
        author = pr_commit.author.email.strip()
        contribs_path_for_path = self.contributors_per_file.setdefault(file.new_path, {})
        contribs_path_for_path[author] = contribs_path_for_path.get(author, 0) + file.added_lines + file.deleted_lines

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, pr_commit, is_rfm_commit, rfm_commit):
        if is_rfm_commit:
            #Make a waypoint for this rfm_commit. Number of unique contributors per rfm_file
            self.contributors_per_file_waypoints[pr_commit.hash] = helper_make_waypoint_per_rfm_file(
                self.contributors_per_file, 
                rfm_commit["rfm_data"]["refactored_files"],
                lambda data: len(list(set(data.keys())))
            )

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        #DDEV waypoint set for current_commit
        if cur_rfm_commit["commit_hash"] in self.contributors_per_file_waypoints.keys():
            return helper_summ_to_commit_level(self.contributors_per_file_waypoints[cur_rfm_commit["commit_hash"]])
        return 0