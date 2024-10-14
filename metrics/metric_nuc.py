from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_commits_per_file_per_author import Data_Provider_Commits_Per_File_Per_Author

#NUC
#The number of times the file has been modified up to the refactoring commit being analyzed.
class Metric_NUC(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        #Commit hash => number of times fiels in the commiit have been modified
        self.commit_files_modified_count = {}
        self.modification_times_in_commit = []
        self.data_provider = Data_Provider_Commits_Per_File_Per_Author(repository)


    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, pr_commit, is_rfm_commit, rfm_commit):
        if is_rfm_commit:
            self.modification_times_in_commit = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        metric_data = self.data_provider.get_data()
        #rfm commit and we have data
        if is_rfm_commit and metric_data and file.new_path in metric_data.keys():
            #Count the times file has been modified
            self.modification_times_in_commit.append(sum([sum(metric_data[file.new_path][author]) for author in metric_data[file.new_path]]))

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, pr_commit, is_rfm_commit, rfm_commit):
        if is_rfm_commit:            
            self.commit_files_modified_count[pr_commit.hash] = sum(self.modification_times_in_commit)

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        return self.commit_files_modified_count.get(pr_commit.hash, 0)