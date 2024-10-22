from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_lines_per_file_per_author import Data_Provider_Lines_Per_File_Per_Author

#OWN
#Measures the percentage of the lines authored by the highest contributor of a file in the considered commit. 
class Metric_OWN(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        #commit => % of contributed lines by largest contributor
        self.lines_authored_per_commit = {}
        self.total_lines_in_commit = 0
        self.lines_authored_by_lg = 0
        self.data_provider = Data_Provider_Lines_Per_File_Per_Author()

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Returns name of the metric as str
    def get_metric_name(self):
        return "OWN"
    
    #Returns at what level was the metric collected at
    def get_collection_level(self):
        return "commit"

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        self.total_lines_in_commit = 0
        self.lines_authored_by_lg = 0

    #Returns the largest contributor to the given file
    def get_largest_contributor_for_file(self, data, file):
        largest_contributor = ""
        lines_by_lg = 0
        #Find out the largest contributor to the given file
        for author in data[file]:
            if data[file][author] > lines_by_lg:
                lines_by_lg = data[file][author]
                largest_contributor = author
        return largest_contributor

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        metric_data = self.data_provider.get_data()
        #is refactorings commit
        if (is_commit_of_interest or not calc_only_commits_of_interest) and metric_data:
            author = helper_commit_author(commit)
            largest_contributor = self.get_largest_contributor_for_file(metric_data, file.new_path)
            lines_contributed = file.added_lines + file.deleted_lines
            #Current author is the largest contributor
            if author == largest_contributor:
                self.lines_authored_by_lg = self.lines_authored_by_lg + lines_contributed
            self.total_lines_in_commit = self.total_lines_in_commit + lines_contributed

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if is_commit_of_interest or not calc_only_commits_of_interest:
            if self.total_lines_in_commit > 0:
                self.lines_authored_per_commit[commit.hash] = (self.lines_authored_by_lg / self.total_lines_in_commit)
            else:
                self.lines_authored_per_commit[commit.hash] = 0     

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.lines_authored_per_commit.get(commit_hash, 0)