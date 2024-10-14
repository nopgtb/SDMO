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

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        self.lines_added[pr_commit.hash] = self.lines_added.get(pr_commit.hash, 0) + file.added_lines

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        return self.lines_added.get(pr_commit.hash, 0)