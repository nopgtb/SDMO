from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import Data_Calculator_Util
from metrics.data_provider.data_provider_lines_per_author import Data_Provider_Lines_Per_Author
from metrics.data_provider.data_provider_commits_per_file_per_author import Data_Provider_Commits_Per_File_Per_Author
from metrics.data_provider.data_provider_total_lines_authored_in_project import Data_Provider_Total_Lines_Authored_In_Project

#OEXP
#Measures the experience of the highest contributor of the changed file using the percentage of lines he authored in the project
#at a given point in time. (Ownership is defined by the number of commits made to the given file)
class Metric_OEXP(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        self.data_provider_lpa = Data_Provider_Lines_Per_Author() 
        self.data_provider_commits = Data_Provider_Commits_Per_File_Per_Author()
        self.data_provider_tla_in_project = Data_Provider_Total_Lines_Authored_In_Project()
        #Commit => {File , author, metric]
        self.exprience_of_files_highest_commiter_waypoint = {}

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider_lpa, self.data_provider_commits, self.data_provider_tla_in_project]

    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "OEXP"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "file"

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #We are calculating this file
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.exprience_of_files_highest_commiter_waypoint[commit.hash] = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        commit_data = self.data_provider_commits.get_data()
        tla_in_project = self.data_provider_tla_in_project.get_data()
        lpa_data = self.data_provider_lpa.get_data()
        #We are calculating this file and have data
        if is_commit_of_interest or not calc_only_commits_of_interest and commit_data and tla_in_project and lpa_data:
            #Get files owner, ownership is defined by the number of commits made to the given file
            hc_author, hc_commit_count  = Data_Calculator_Util.get_highest_commiter_of_file(commit_data, file.new_path)
            #We have owner and they have data
            if hc_author and hc_author in lpa_data.keys():
                #Calculate authors experience = lines authored by the them / total lines in project
                self.exprience_of_files_highest_commiter_waypoint[commit.hash].append({
                    "file": file.new_path,
                    "author": hc_author,
                    "metric": (lpa_data.get(hc_author) / tla_in_project) * 100
                })

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.exprience_of_files_highest_commiter_waypoint.get(commit_hash, None)