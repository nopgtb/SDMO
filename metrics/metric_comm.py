from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_commits_from_last_rfmc import Data_Provider_Commits_From_Last_Rfmc

#COMM
#The cumulative number of commits made to a file up to the considered commit starting from the previous refactoring commit
#(consider the commit with the introduction of the file as the previous commit when dealing with the first refactoring commit)
class Metric_COMM(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.commit_per_file_waypoints = {}
        self.data_provider = Data_Provider_Commits_From_Last_Rfmc(repository)

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, pr_commit, is_rfm_commit, rfm_commit):
        if is_rfm_commit:
            self.commit_per_file_waypoints[pr_commit.hash] = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        metric_data = self.data_provider.get_data()
        #Make waypoint for rfm commit files
        if is_rfm_commit and metric_data and file.new_path in metric_data.keys():
            self.commit_per_file_waypoints[pr_commit.hash].append(
                {
                    "file": file.new_path,
                    "metric": sum(metric_data[file.new_path])
                }
            )

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        return helper_sum_to_commit_level(self.commit_per_file_waypoints.get(pr_commit.hash, []))