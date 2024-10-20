from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_lines_per_file_per_author_from_last_coi import Data_Provider_Lines_Per_File_Per_Author_From_Last_COI

#NADEV
#The number of active developers who, given the considered commit, changed the same specific files along with the given file up
#to the considered commit starting from the previous refactoring commit (consider the commit with the introduction of the file
#as the previous commit when dealing with the first refactoring commit).
class Metric_NADEV(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.contributors_per_files_neighbours_waypoints = {}
        self.data_provider = Data_Provider_Lines_Per_File_Per_Author_From_Last_COI(repository)

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Returns name of the metric as str
    def get_metric_name(self):
        return "NADEV"
    
    #Returns at what level was the metric collected at
    def get_collection_level(self):
        return "file"

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if is_commit_of_interest or not calc_only_commits_of_interest:
            metric_data = self.data_provider.get_data()
            if metric_data:
                #Make a waypoint for this commit. Number of contributors per file neighbours
                self.contributors_per_files_neighbours_waypoints[commit.hash] = helper_make_waypoint_per_file_neigbours(
                    metric_data,
                    helper_list_commit_files(commit),
                    lambda data: len(data.keys())
                )

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.contributors_per_files_neighbours_waypoints.get(commit_hash, 0)