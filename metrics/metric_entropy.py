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

    #Returns name of the metric as str
    def get_metric_name(self):
        return "ENTROPY"
    
    #Returns at what level was the metric collected at
    def get_collection_level(self):
        return "commit"

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.commit_entropy_levels[commit.hash] = {"commit_total_lines":0, "entropy": 0, "files":{}}

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if is_commit_of_interest or not calc_only_commits_of_interest:
            lines_changed = file.added_lines + file.deleted_lines
            self.commit_entropy_levels[commit.hash]["files"][file.new_path] = lines_changed
            self.commit_entropy_levels[commit.hash]["commit_total_lines"] = self.commit_entropy_levels[commit.hash]["commit_total_lines"] + lines_changed

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if is_commit_of_interest or not calc_only_commits_of_interest:
            if self.commit_entropy_levels[commit.hash]["commit_total_lines"] > 0:
                #https://en.wikipedia.org/wiki/Entropy_(information_theory)
                #Calculate per commit -sum([(x*log2(x))]) where x is portion of total contributed lines in the commit 
                terms = []
                for file in self.commit_entropy_levels[commit.hash]["files"]:
                    portion = self.commit_entropy_levels[commit.hash]["files"][file] / self.commit_entropy_levels[commit.hash]["commit_total_lines"]
                    if portion > 0:
                        terms.append(portion * math.log2(portion))
                self.commit_entropy_levels[commit.hash]["entropy"] = -1 * sum(terms)
            else:
                self.commit_entropy_levels[commit.hash]["entropy"] = 0

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.commit_entropy_levels.get(commit_hash, {"entropy":0})["entropy"]