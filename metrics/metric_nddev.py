from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import Data_Calculator_Util
from metrics.data_provider.data_provider_lines_per_file_per_author import Data_Provider_Lines_Per_File_Per_Author

#NDDEV
#The number of distinct developers who, given the considered commit, changed the same specific files up to the considered commit
#starting from the point in which the file was introduced
class Metric_NDDEV(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        self.contributors_per_files_neighbours_waypoints = {}
        self.data_provider = Data_Provider_Lines_Per_File_Per_Author()

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]
    
    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "NDDEV"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "file"

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if is_commit_of_interest or not calc_only_commits_of_interest:
            metric_data = self.data_provider.get_data()
            if metric_data:
                #Make a waypoint for this commit. Number of "Distinct" contributors per files neighbours
                self.contributors_per_files_neighbours_waypoints[commit.hash] = Data_Calculator_Util.waypoint_per_file_neigbours(
                    metric_data,
                    Data_Calculator_Util.list_commit_files(commit),
                    lambda data: len(list(set(data.keys())))
                )

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.contributors_per_files_neighbours_waypoints.get(commit_hash, 0)