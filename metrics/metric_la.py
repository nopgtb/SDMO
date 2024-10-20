from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *

#LA
#The lines added to the given file in the refactoring commit being analyzed (absolute number of the ADD metric).
class Metric_LA(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        #commit => lines_added
        self.lines_added = {}

    #Data providers for the metric
    def get_data_providers(self):
        return []

    #Returns name of the metric as str
    def get_metric_name(self):
        return "LA"
    
    #Returns at what level was the metric collected at
    def get_collection_level(self):
        return "commit"

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.lines_added[commit.hash] = self.lines_added.get(commit.hash, 0) + file.added_lines

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.lines_added.get(commit_hash, 0)