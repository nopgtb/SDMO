from metrics.metric_interface import Metric_Interface
from metrics.metric_helper_functions import *
from metrics.data_provider.data_provider_commits_from_last_rfmc import Data_Provider_Commits_From_Last_Rfmc

#NCOMM
#The cumulative number of commits made to a file up to the considered commit starting from the previous refactoring commit, in
#which the same set of files were changed along with the given file. (For the first refactoring commit, consider as previous commit
#the one in which the file was introduced)
class Metric_NCOMM(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.data_provider = Data_Provider_Commits_From_Last_Rfmc(repository)
        self.commit_per_file_neighbours_waypoints = {}

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, pr_commit, is_rfm_commit, rfm_commit):
        if is_rfm_commit:
            metric_data = self.data_provider.get_data()
            if metric_data:
                #Make a waypoint for this rfm_commit. per rfm_file, sum its neighbours commits
                self.commit_per_file_neighbours_waypoints[pr_commit.hash] = helper_make_waypoint_per_rfm_file_neigbours(
                    metric_data, 
                    rfm_commit["rfm_data"]["refactored_files"],
                    lambda data: sum(data)
                )

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        #NCOMM waypoint set for current_commit
        if cur_rfm_commit["commit_hash"] in self.commit_per_file_neighbours_waypoints.keys():
            return self.commit_per_file_neighbours_waypoints[cur_rfm_commit["commit_hash"]]
        return 0
    
    #Returns at what level was the metric collected at
    def get_collection_level():
        return "file"