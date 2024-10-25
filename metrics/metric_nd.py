from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_path_statistics import Data_Provider_Path_Statistics

#ND
#The number of directories involved in a commit.
class Metric_ND(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        self.data_provider = Data_Provider_Path_Statistics()

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "ND"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "commit"

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        metric_data = self.data_provider.get_data()
        if metric_data and commit_hash in metric_data.keys():
            return metric_data[commit_hash]["directory_count"]
        return 0