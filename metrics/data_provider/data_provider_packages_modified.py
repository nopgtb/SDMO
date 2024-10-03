from .data_provider_interface import Data_Provider_Interface
from metrics.metric_helper_functions import *

#Metrics rely on common data. Instead of each metric calculating it on its own
#data provider will provide it from single source making it available for all metrics
class Data_Provider_Packages_Modified(Data_Provider_Interface):

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        #Get Modified packages and append them to commit data
        commit_data = self.packages_modified_per_commit.setdefault(pr_commit.hash, {})
        commit_data[file.new_path] = helper_extract_modified_packages(file)

    #Initialize and Reset the data
    def reset_data(self):
        #commit.hash => file => [packages_modified]
        self.packages_modified_per_commit = {}

    #Returns the data of the data provider
    def get_data(self):
        return self.packages_modified_per_commit