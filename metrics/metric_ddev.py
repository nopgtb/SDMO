from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_lines_per_file_per_author import Data_Provider_Lines_Per_File_Per_Author

#DDEV
#The cumulative number of distinct developers contributed to a given file up to the considered commit starting from the point the file was introduced.
class Metric_DDEV(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        #commit => [num of dist devs contrib to file]
        self.contributors_per_file_waypoints = {}
        self.data_provider = Data_Provider_Lines_Per_File_Per_Author(repository)

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Returns name of the metric as str
    def get_metric_name(self):
        return "DDEV"
    
    #Returns at what level was the metric collected at
    def get_collection_level(self):
        return "commit"

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.contributors_per_file_waypoints[commit.hash] = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        metric_data = self.data_provider.get_data()
        #Make waypoint for commit files
        if (is_commit_of_interest or not calc_only_commits_of_interest) and metric_data and file.new_path in metric_data.keys():
            self.contributors_per_file_waypoints[commit.hash].append(len(list(set(metric_data[file.new_path]))))

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return sum(self.contributors_per_file_waypoints.get(commit_hash, []))