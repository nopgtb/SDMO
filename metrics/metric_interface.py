from .data_calculator_interface import Data_Calculator_Interface
#Abstract class for implementing metric calculations
class Metric_Interface(Data_Calculator_Interface):
    #Store the repo
    def __init__(self):
        pass
    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        pass
    
    #Returns at what level was the metric collected at
    def get_collection_level(self):
        pass
    
    #Returns name of the metric as str
    def get_metric_name(self):
        pass

    #Data providers for the metric
    def get_data_providers(self):
        return []