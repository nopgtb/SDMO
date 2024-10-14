from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_contributions_per_file_per_author import Data_Provider_Contributions_Per_File_Per_Author
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
        self.data_provider_contributions = Data_Provider_Contributions_Per_File_Per_Author(repository)
        self.data_provider_tla_in_project = Data_Provider_Total_Lines_Authored_In_Project(repository)

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider_contributions, self.data_provider_commits, self.data_provider_tla_in_project]

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, pr_commit, is_rfm_commit, rfm_commit):
        commit_data = self.data_provider_commits.get_data()
        contribution_data = self.data_provider_contributions.get_data()
        tla_in_project = self.data_provider_tla_in_project.get_data()
        #is refactorings commit
        if is_rfm_commit and commit_data and contribution_data and tla_in_project:
            for file in rfm_commit["rfm_data"]["refactored_files"]:
                #Ownership is defined by the number of commits made to the given file
                highest_commiter_of_file = helper_get_highest_commiter_of_file(commit_data, file)
                lines_contributed_by_hc = contribution_data[file][highest_commiter_of_file["author"]]
                self.exprience_of_files_highest_commiter.setdefault(pr_commit.hash, {})[file] = {
                    "author": highest_commiter_of_file["author"],
                    "metric": (lines_contributed_by_hc / tla_in_project)
                }

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        #OEXP waypoint set for current_commit
        if cur_rfm_commit["commit_hash"] in self.exprience_of_files_highest_commiter.keys():
            return self.exprience_of_files_highest_commiter[cur_rfm_commit["commit_hash"]]
        return 0
    
    #Returns at what level was the metric collected at
    def get_collection_level():
        return "file"