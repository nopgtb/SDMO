from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_lines_per_file_per_author_from_last_coi import Data_Provider_Lines_Per_File_Per_Author_From_Last_COI

#ADEV
#The number of developers who modified a given file up to the considered commit starting from previous refactoring commit
#(consider the commit with the introduction of the file as the previous commit when dealing with the first refactoring commit).
class Metric_ADEV(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        self.data_provider = Data_Provider_Lines_Per_File_Per_Author_From_Last_COI()
        #commit => [Number of authors who contributed to commits files since last COI]
        self.authors_per_commits_files_since_coi_waypoint = {}

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]
    
    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "ADEV"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "commit"

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #Are we calculating a waypoint for this commit?
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.authors_per_commits_files_since_coi_waypoint[commit.hash] = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        metric_data = self.data_provider.get_data()
        #We are making a waypoint and we have data for the file
        if (is_commit_of_interest or not calc_only_commits_of_interest) and metric_data and file.new_path in metric_data.keys():
            #Files contribution to the commits value is the number of devs that have commited the file since last COI
            self.authors_per_commits_files_since_coi_waypoint[commit.hash].append(len(metric_data[file.new_path]))

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        if commit_hash in self.authors_per_commits_files_since_coi_waypoint.keys():
            #Sum all the devs together that have commited this commits file since last COI
            return sum(self.authors_per_commits_files_since_coi_waypoint.get(commit_hash))
        return None