from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_path_statistics import Data_Provider_Path_Statistics

#NF
#The number of directories involved in a commit.
class Metric_NF(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.data_provider = Data_Provider_Path_Statistics(repository)

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        metric_data = self.data_provider.get_data()
        if metric_data and pr_commit.hash in metric_data.keys():
            return metric_data[pr_commit.hash]["file_count"]
        return 0