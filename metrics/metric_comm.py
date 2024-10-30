from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_commits_per_file_from_last_coi import Data_Provider_Commits_Per_File_From_Last_COI

#COMM
#The cumulative number of commits made to a file up to the considered commit starting from the previous refactoring commit
#(consider the commit with the introduction of the file as the previous commit when dealing with the first refactoring commit)
class Metric_COMM(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        self.data_provider = Data_Provider_Commits_Per_File_From_Last_COI()
        #commit => [Per commits file, commits made to them since last COI]
        self.commit_per_file_waypoints = {}

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]
    
    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "COMM"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "commit"

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #Are we calculating a waypoint for this commit?
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.commit_per_file_waypoints[commit.hash] = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        metric_data = self.data_provider.get_data()
        #We are calcuting this commit and we have data for it
        if (is_commit_of_interest or not calc_only_commits_of_interest) and metric_data and file.new_path in metric_data.keys():
            #File contribution to the value is sum of the commits made to it since last COI
            self.commit_per_file_waypoints[commit.hash].append(sum(metric_data[file.new_path]))

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        if commit_hash in self.commit_per_file_waypoints.keys():
            #Sum all the commits made to the COI commits files since last COI
            return sum(self.commit_per_file_waypoints.get(commit_hash))
        return None