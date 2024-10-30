from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_lines_per_file_per_author import Data_Provider_Lines_Per_File_Per_Author

#DDEV
#The cumulative number of distinct developers contributed to a given file up to the considered commit starting from the point the file was introduced.
class Metric_DDEV(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        self.data_provider = Data_Provider_Lines_Per_File_Per_Author()
        #commit => [Per commits file, Number of unique devs contributed to the file since its creation]
        self.authors_per_commits_files_waypoint = {}

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "DDEV"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "commit"

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #Are we calculating a waypoint for this commit?
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.authors_per_commits_files_waypoint[commit.hash] = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        metric_data = self.data_provider.get_data()
        #We are making a waypoint and we have data for the file
        if (is_commit_of_interest or not calc_only_commits_of_interest) and metric_data and file.new_path in metric_data.keys():
            #Files contribution to the commits value is list of all unique developers that have commited the file since its introduction
            self.authors_per_commits_files_waypoint[commit.hash].append(len(list(set(metric_data[file.new_path]))))

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        if commit_hash in self.authors_per_commits_files_waypoint.keys():
            #Sum all the unique devs that have contributed to the commits files since their creation.
            #Now this number only considers the "uniqueness" of the devs on the file level
            #Based on the metric discription this should not be an issue
            return sum(self.authors_per_commits_files_waypoint.get(commit_hash))
        return None