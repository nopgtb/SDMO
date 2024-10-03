from .data_calculator_interface import Data_Calculator_Interface
#Abstract class for implementing metric calculations
class Metric_Interface(Data_Calculator_Interface):
    #Store the repo
    def __init__(self, repository):
        self.repository = repository

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        pass
    
    #Returns at what level was the metric collected at
    def get_collection_level():
        return "commit"

    #Data providers for the metric
    def get_data_providers(self):
        return []