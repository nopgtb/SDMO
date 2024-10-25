from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_external_ck import Data_Provider_External_CK

#NOSF
#Number Of Static Fields declared in a class.
class Metric_NOSF(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        self.data_provider = Data_Provider_External_CK()

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]
    
    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "NOSF"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "class"

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        metric_data = self.data_provider.get_data()
        #If we have data for commit
        if metric_data and commit_hash in metric_data.keys():
            #for class in metric_data[hash] {class["class"] : class["staticFieldsQty"]}
            return [{"class":c["class"], "metric":c["staticFieldsQty"]} for c in metric_data[commit_hash]]
        return []
