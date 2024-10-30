from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import Data_Calculator_Util
from metrics.data_provider.data_provider_commits_per_file_per_author import Data_Provider_Commits_Per_File_Per_Author

#CEXP
#The number of commits performed on the given file by the committer up to the refactoring commit being analyzed. 
class Metric_CEXP(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        self.data_provider = Data_Provider_Commits_Per_File_Per_Author()
        #Hash => number of commits made on files by author
        self.commits_made_by_author_on_files_waypoint = {}
        self.times_author_commit_files = []

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]
    
    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "CEXP"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "commit"
    
    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        self.times_author_commit_files = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        metric_data = self.data_provider.get_data()
        author = Data_Calculator_Util.get_commit_author(commit)
        #We are calculating this file and we have data for the author
        if (is_commit_of_interest or not calc_only_commits_of_interest) and metric_data and file.new_path in metric_data.keys() and author in metric_data[file.new_path].keys():
            self.times_author_commit_files.append(metric_data[file.new_path][author])

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #We are calculating this commit
        if is_commit_of_interest or not calc_only_commits_of_interest:
            #Sum number of times author has modified commits files
            self.commits_made_by_author_on_files_waypoint[commit.hash] = sum(self.times_author_commit_files)

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.commits_made_by_author_on_files_waypoint.get(commit_hash, None)