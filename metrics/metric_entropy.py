from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
import math

#ENTROPY
#The distribution of the modified code across each given file in the refactoring commit being analyzed. 
class Metric_ENTROPY(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        #commit => {tlc, entropy, files=>{file => lines_changed}}
        self.commit_entropy_levels = {}

    #Data providers for the metric
    def get_data_providers(self):
        return []

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, pr_commit, is_rfm_commit, rfm_commit):
        self.commit_entropy_levels[pr_commit.hash] = {"commit_total_lines":0, "entropy": 0, "files":{}}

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        lines_changed = file.added_lines + file.deleted_lines
        self.commit_entropy_levels[pr_commit.hash]["files"][file.new_path] = lines_changed
        self.commit_entropy_levels[pr_commit.hash]["commit_total_lines"] = self.commit_entropy_levels[pr_commit.hash]["commit_total_lines"] + lines_changed

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, pr_commit, is_rfm_commit, rfm_commit):
        if self.commit_entropy_levels[pr_commit.hash]["commit_total_lines"] > 0:
            #https://en.wikipedia.org/wiki/Entropy_(information_theory)
            #Calculate per commit -sum([(x*log2(x))]) where x is portion of total contributed lines in the commit 
            terms = []
            for file in self.commit_entropy_levels[pr_commit.hash]["files"]:
                portion = self.commit_entropy_levels[pr_commit.hash]["files"][file] / self.commit_entropy_levels[pr_commit.hash]["commit_total_lines"]
                if portion > 0:
                    terms.append(portion * math.log2(portion))
            self.commit_entropy_levels[pr_commit.hash]["entropy"] = -1 * sum(terms)
        else:
            self.commit_entropy_levels[pr_commit.hash]["entropy"] = 0

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        if pr_commit.hash in self.commit_entropy_levels.keys():
            return self.commit_entropy_levels[pr_commit.hash]["entropy"]
        return 0