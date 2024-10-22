from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_commits_per_file_per_author import Data_Provider_Commits_Per_File_Per_Author

#NUC
#The number of times the file has been modified up to the refactoring commit being analyzed.
class Metric_NUC(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        #Commit hash => number of times fiels in the commiit have been modified
        self.commit_files_modified_count = {}
        self.modification_times_in_commit = []
        self.data_provider = Data_Provider_Commits_Per_File_Per_Author()

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Returns name of the metric as str
    def get_metric_name(self):
        return "NUC"
    
    #Returns at what level was the metric collected at
    def get_collection_level(self):
        return "commit"

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        self.modification_times_in_commit = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        metric_data = self.data_provider.get_data()
        #commit and we have data
        if (is_commit_of_interest or not calc_only_commits_of_interest) and metric_data and file.new_path in metric_data.keys():
            #Count the times file has been modified
            self.modification_times_in_commit.append(sum([metric_data[file.new_path][author] for author in metric_data[file.new_path]]))

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if is_commit_of_interest or not calc_only_commits_of_interest:            
            self.commit_files_modified_count[commit.hash] = sum(self.modification_times_in_commit)

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.commit_files_modified_count.get(commit_hash, 0)