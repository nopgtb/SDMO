from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *

#LT
#The number of lines of code in the given file in the refactoring commit being analyzed before the change.
class Metric_LT(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        #commit => lines_before
        self.lines_before = {}

    #Data providers for the metric
    def get_data_providers(self):
        return []

    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "LT"

    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "commit"

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if file.source_code_before and (is_commit_of_interest or not calc_only_commits_of_interest):
            self.lines_before[commit.hash] = self.lines_before.get(commit.hash, 0) + len(file.source_code_before.splitlines())

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.lines_before.get(commit_hash, None)