from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import Data_Calculator_Util
from metrics.data_provider.data_provider_commits_per_file_from_last_coi import Data_Provider_Commits_Per_File_From_Last_COI

#NCOMM
#The cumulative number of commits made to a file up to the considered commit starting from the previous refactoring commit, in
#which the same set of files were changed along with the given file. (For the first refactoring commit, consider as previous commit
#the one in which the file was introduced)
class Metric_NCOMM(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        self.data_provider = Data_Provider_Commits_Per_File_From_Last_COI()
        self.commit_per_file_neighbours_waypoints = {}

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "NCOMM"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "file"

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if is_commit_of_interest or not calc_only_commits_of_interest:
            metric_data = self.data_provider.get_data()
            if metric_data:
                #Make a waypoint for this commit. per file, sum its neighbours commits
                self.commit_per_file_neighbours_waypoints[commit.hash] = Data_Calculator_Util.waypoint_per_file_neigbours(
                    metric_data, 
                    Data_Calculator_Util.list_commit_files(commit),
                    lambda data: sum(data)
                )

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.commit_per_file_neighbours_waypoints.get(commit_hash, 0)