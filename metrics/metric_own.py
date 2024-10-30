from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import Data_Calculator_Util
from metrics.data_provider.data_provider_lines_per_file_per_author import Data_Provider_Lines_Per_File_Per_Author
from metrics.data_provider.data_provider_commits_per_file_per_author import Data_Provider_Commits_Per_File_Per_Author

#OWN
#Measures the percentage of the lines authored by the highest contributor of a file in the considered commit. 
class Metric_OWN(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        self.lines_per_author = Data_Provider_Lines_Per_File_Per_Author()
        self.commits_per_author = Data_Provider_Commits_Per_File_Per_Author()
        #Hash => Average percentage contributed by the commits files largest contributors
        self.percent_of_lines_contrib_lc_waypoint = {}
        #[% per largest contributor]
        self.lc_author_contrib_percentages = []

    #Data providers for the metric
    def get_data_providers(self):
        return [self.lines_per_author, self.commits_per_author]

    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "OWN"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "commit"

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #Reset the data per commit
        self.lc_author_contrib_percentages = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        lpa_data = self.lines_per_author.get_data()
        cpa_data = self.commits_per_author.get_data()
        #We are calculating this file and we have data
        if (is_commit_of_interest or not calc_only_commits_of_interest) and lpa_data and cpa_data:
            hc_author, hc_commit_count  = Data_Calculator_Util.get_highest_commiter_of_file(cpa_data, file.new_path)
            #We have a highest commiter for the file
            if hc_author:
                lines_contrib_by_hc_author = Data_Calculator_Util.get_total_lines_contributed_by_author(lpa_data, file, hc_author)
                total_lines_contrib_for_file = Data_Calculator_Util.get_total_lines_contributed_by_author(lpa_data, file, None)
                if total_lines_contrib_for_file > 0:
                    #This files contribution to the commits value is the percentage contributed of the total by its highest contributor
                    self.lc_author_contrib_percentages.append((lines_contrib_by_hc_author / total_lines_contrib_for_file) * 100)
                
    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #We are calculating this commit
        if is_commit_of_interest or not calc_only_commits_of_interest:
            #We have data from the files
            if len(self.lc_author_contrib_percentages) > 0:
                #Average the contribution percentages to the commit level to get our waypoint
                self.percent_of_lines_contrib_lc_waypoint[commit.hash] = sum(self.lc_author_contrib_percentages) / len(self.lc_author_contrib_percentages)
            else:
                self.percent_of_lines_contrib_lc_waypoint[commit.hash] = 0

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.percent_of_lines_contrib_lc_waypoint.get(commit_hash, None)