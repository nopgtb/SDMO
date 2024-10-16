from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_contributions_per_file_per_author import Data_Provider_Contributions_Per_File_Per_Author

#DDEV
#The cumulative number of distinct developers contributed to a given file up to the considered commit starting from the point the file was introduced.
class Metric_DDEV(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.contributors_per_file_waypoints = {}
        self.data_provider = Data_Provider_Contributions_Per_File_Per_Author(repository)

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, pr_commit, is_rfm_commit, rfm_commit):
        if is_rfm_commit:
            self.contributors_per_file_waypoints[pr_commit.hash] = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        metric_data = self.data_provider.get_data()
        #Make waypoint for rfm commit files
        if is_rfm_commit and metric_data and file.new_path in metric_data.keys():
            self.contributors_per_file_waypoints[pr_commit.hash].append(
                {
                    "file": file.new_path,
                    "metric": len(list(set(metric_data[file.new_path])))
                }
            )

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        return helper_sum_to_commit_level(self.contributors_per_file_waypoints.get(pr_commit.hash, []))