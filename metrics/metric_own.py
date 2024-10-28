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
        #commit => % of contributed lines by largest contributor
        self.lines_authored_per_commit = {}
        #[% per file]
        self.own_percentages = []
        self.lines_per_author = Data_Provider_Lines_Per_File_Per_Author()
        self.commits_per_author = Data_Provider_Commits_Per_File_Per_Author()

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
        self.own_percentages = []

    def get_total_lines_contributed_to_file(self, data, file):
        total_lines_in_file = 0
        #File => Author => Num of contributed lines
        if file.new_path in data.keys():
            for author in data[file.new_path]:
                total_lines_in_file = total_lines_in_file + data[file.new_path][author]
        return total_lines_in_file

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        lpa_data = self.lines_per_author.get_data()
        cpa_data = self.commits_per_author.get_data()
        #is coi commit
        if (is_commit_of_interest or not calc_only_commits_of_interest) and lpa_data and cpa_data:
            author = Data_Calculator_Util.get_commit_author(commit)
            hc_author, hc_commit_count  = Data_Calculator_Util.get_highest_commiter_of_file(cpa_data, file.new_path)
            #Current author is the largest contributor
            if hc_author and author == hc_author:
                lines_contributed_in_commit = file.added_lines + file.deleted_lines
                total_lines_for_file = self.get_total_lines_contributed_to_file(lpa_data, file)
                if total_lines_for_file > 0:
                    #ownermod/totalmod * 100
                    self.own_percentages.append((lines_contributed_in_commit / total_lines_for_file) * 100)
                
    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if is_commit_of_interest or not calc_only_commits_of_interest:
            if len(self.own_percentages) > 0:
                #Average the % to commit level
                self.lines_authored_per_commit[commit.hash] = sum(self.own_percentages) / len(self.own_percentages)
            else:
                self.lines_authored_per_commit[commit.hash] = 0

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.lines_authored_per_commit.get(commit_hash, None)