from metrics.metric import Metric
from metrics.metric_helper_functions import *
from metrics.data_provider.data_provider_contributions_from_last_rfmc import Data_Provider_Contributions_From_Last_Rfmc

#ADEV
#The number of developers who modified a given file up to the considered commit starting from previous refactoring commit
#(consider the commit with the introduction of the file as the previous commit when dealing with the first refactoring commit).
class Metric_ADEV(Metric):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.contributors_per_file_waypoints = {}
        self.data_provider = Data_Provider_Contributions_From_Last_Rfmc(repository)

    #Data provider for the metric
    def get_data_provider(self):
        return self.data_provider

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, pr_commit, is_rfm_commit, rfm_commit):
        if is_rfm_commit:
            metric_data = self.get_data_provider().get_data()
            if metric_data:
                #Make a waypoint for this rfm_commit. Number of contributors per rfm_file
                self.contributors_per_file_waypoints[pr_commit.hash] = helper_make_waypoint_per_rfm_file(
                    metric_data, 
                    rfm_commit["rfm_data"]["refactored_files"],
                    lambda data: len(data.keys())
                )

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        #ADEV waypoint set for current_commit
        if cur_rfm_commit["commit_hash"] in self.contributors_per_file_waypoints.keys():
            return helper_summ_to_commit_level(self.contributors_per_file_waypoints[cur_rfm_commit["commit_hash"]])
        return 0