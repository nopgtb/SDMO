from .data_provider_interface import Data_Provider_Interface
from metrics.data_calculator_util import Data_Calculator_Util

#Metrics rely on common data. Instead of each metric calculating it on its own
#data provider will provide it from single source making it available for all metrics
class Data_Provider_Author_Per_Commit(Data_Provider_Interface):

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        self.commit_author[commit.hash] = Data_Calculator_Util.get_commit_author(commit)

    #Initialize and Reset the data
    def reset_data(self):
        #hash => author
        self.commit_author = {}

    #Returns the data of the data provider
    def get_data(self):
        return self.commit_author