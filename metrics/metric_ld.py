from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *

#LD
#The number of lines removed from the given file in the refactoring commit being analyzed (absolute number of the DEL metric). 
class Metric_LD(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        #commit => lines_deleted
        self.lines_deleted_waypoint = {}

    #Data providers for the metric
    def get_data_providers(self):
        return []

    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "LD"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "commit"

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #We are calculating this file
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.lines_deleted_waypoint[commit.hash] = self.lines_deleted_waypoint.get(commit.hash, 0) + file.deleted_lines

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.lines_deleted_waypoint.get(commit_hash, None)