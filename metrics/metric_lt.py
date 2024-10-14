from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *

#LT
#The number of lines of code in the given file in the refactoring commit being analyzed before the change.
class Metric_LT(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        #commit => lines_before
        self.lines_before = {}

    #Data providers for the metric
    def get_data_providers(self):
        return []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        if file.source_code_before:
            self.lines_before.get(pr_commit.hash, 0) + len(file.source_code_before.splitlines())


    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        return self.lines_before.get(pr_commit.hash, 0)