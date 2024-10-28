from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_lines_per_file_per_author import Data_Provider_Lines_Per_File_Per_Author

#MINOR
#The number of contributors who contributed less than 5% of a given file up to the considered commit. 
class Metric_MINOR(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        #commit => [num of contribs who give less than 5%]
        self.minor_authors_in_file_waypoint = {}
        self.minor_author_treshold = 0.05
        self.data_provider = Data_Provider_Lines_Per_File_Per_Author()

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "MINOR"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "commit"

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.minor_authors_in_file_waypoint[commit.hash] = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        metric_data = self.data_provider.get_data()
        #Make waypoint for commit files
        if (is_commit_of_interest or not calc_only_commits_of_interest) and metric_data and file.new_path in metric_data.keys():
            #Sum of total lines contributed to the file between all the developers
            total_lines = sum([metric_data[file.new_path][author] for author in metric_data[file.new_path]])
            if total_lines > 0:
                #Count the number of developers that have contributed less or equal amount of lines
                #than the threshold set in self.minor_author_treshold
                self.minor_authors_in_file_waypoint[commit.hash].append(len([author for author in metric_data[file.new_path] if (metric_data[file.new_path][author] / total_lines) >= self.minor_author_treshold]))

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        if commit_hash in self.minor_authors_in_file_waypoint.keys():
            return sum(self.minor_authors_in_file_waypoint.get(commit_hash))
        return None