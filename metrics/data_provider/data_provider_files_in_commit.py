from .data_provider_interface import Data_Provider_Interface
from metrics.data_calculator_util import Data_Calculator_Util
from pydriller import ModificationType

#Metrics rely on common data. Instead of each metric calculating it on its own
#data provider will provide it from single source making it available for all metrics
class Data_Provider_Files_In_Commit(Data_Provider_Interface):

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.files_in_commits[file.new_path] = self.files_in_commits.setdefault(file.old_path, [])
        self.files_in_commits.setdefault(file.new_path, []).append(commit.hash)

    #Initialize and Reset the data
    def reset_data(self):
        #File => [hash]
        self.files_in_commits = {}

    #Returns the data of the data provider
    def get_data(self):
        return self.files_in_commits