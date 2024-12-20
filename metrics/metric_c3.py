from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_external_c3_hslcom import Data_Provider_External_C3_HSLCOM

#RFC
#Response For a Class: the number of methods in a class plus the number of remote methods that are called recursively. 
class Metric_C3(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        self.data_provider = Data_Provider_External_C3_HSLCOM()

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]
    
    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "C3"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "class"

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        metric_data = self.data_provider.get_data()
        #If we have data for commit
        if metric_data and commit_hash in metric_data.keys():
            return [{"class":c["class"], "metric":c["metric_c3"]} for c in metric_data[commit_hash]]
        return None
