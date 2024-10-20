from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_lines_per_file_per_author import Data_Provider_Lines_Per_File_Per_Author
from metrics.data_provider.data_provider_commits_per_file_per_author import Data_Provider_Commits_Per_File_Per_Author
from metrics.data_provider.data_provider_total_lines_authored_in_project import Data_Provider_Total_Lines_Authored_In_Project

#per file
# - Find highest commiter of the file
#   - Calculate Total lines authored in the project
#       - Calculate Lines authored by the highest commiter of the file
#           return HCLA / PLA 

#OEXP
#Measures the experience of the highest contributor of the changed file using the percentage of lines he authored in the project
#at a given point in time. (Ownership is defined by the number of commits made to the given file)
class Metric_OEXP(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        #Commit => File =>  author, exp
        self.exprience_of_files_highest_commiter = {}
        self.data_provider_commits = Data_Provider_Commits_Per_File_Per_Author(repository)
        self.data_provider_contributions = Data_Provider_Lines_Per_File_Per_Author(repository)
        self.data_provider_tla_in_project = Data_Provider_Total_Lines_Authored_In_Project(repository)

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider_contributions, self.data_provider_commits, self.data_provider_tla_in_project]

    #Returns name of the metric as str
    def get_metric_name(self):
        return "OEXP"
    
    #Returns at what level was the metric collected at
    def get_collection_level(self):
        return "file"

    #Returns name of the author that is highest commiter of the file based on the given data
    def get_highest_commiter_of_file(self, data, file):
        highest_commiter = {"author": "", "commits":0}
        for author in data[file]:
            commits_authored = data[file][author]
            if commits_authored > highest_commiter["commits"]:
                highest_commiter = {"author":author, "commits": commits_authored}
        return highest_commiter

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        commit_data = self.data_provider_commits.get_data()
        contribution_data = self.data_provider_contributions.get_data()
        tla_in_project = self.data_provider_tla_in_project.get_data()
        #is refactorings commit
        if (is_commit_of_interest or not calc_only_commits_of_interest) and commit_data and contribution_data and tla_in_project:
            for file in helper_list_commit_files(commit):
                #Ownership is defined by the number of commits made to the given file
                highest_commiter_of_file = self.get_highest_commiter_of_file(commit_data, file)
                lines_contributed_by_hc = contribution_data[file][highest_commiter_of_file["author"]]
                self.exprience_of_files_highest_commiter.setdefault(commit.hash, {})[file] = {
                    "author": highest_commiter_of_file["author"],
                    "metric": (lines_contributed_by_hc / tla_in_project)
                }

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.exprience_of_files_highest_commiter.get(commit_hash, 0)