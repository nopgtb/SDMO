from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_contributions_per_file_per_author import Data_Provider_Contributions_Per_File_Per_Author

#NDEV
#The number of developers that changed the modified files. 
class Metric_NDEV(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.data_provider = Data_Provider_Contributions_Per_File_Per_Author(repository)
        #commit hash => number of authors
        self.authors_per_commit = {}

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, pr_commit, is_rfm_commit, rfm_commit):
        if is_rfm_commit:
            #Prep the data structure for waypoint
            self.authors_per_commit[pr_commit.hash] = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        metric_data = self.data_provider.get_data()
        #Rfm commit and we have data
        if is_rfm_commit and metric_data and file.new_path in metric_data.keys():
            self.authors_per_commit[pr_commit.hash].append(
                {
                    "file": file.new_path,
                    "metric": len(metric_data[file.new_path])
                }
            )

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        metric_data = self.data_provider.get_data()
        if metric_data and pr_commit.hash in self.authors_per_commit.keys():
            return helper_sum_to_commit_level(self.authors_per_commit[pr_commit.hash])
        return 0