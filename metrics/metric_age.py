from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_file_modification_date import Data_Provider_File_Modification_Date

#AGE
#The average time interval between the current and the last time the changed files were modified. (Unit: Days) 
class Metric_AGE(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        #Commit hash => days on average since last change
        self.commit_average_mod_interval = {}
        self.mod_time_sep = []
        self.data_provider = Data_Provider_File_Modification_Date(repository)

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, pr_commit, is_rfm_commit, rfm_commit):
        self.mod_time_sep = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        if is_rfm_commit:
            metric_data = self.data_provider.get_data()
            if metric_data and file in metric_data.keys() and len(metric_data[file]) > 1:
                #Calculate the time between current mod and last mod
                self.mod_time_sep.append((metric_data[file][-1] - metric_data[file][len(metric_data[file])-2]).days)
        
    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, pr_commit, is_rfm_commit, rfm_commit):
        if is_rfm_commit:
            #Calcualte the average
            if len(self.mod_time_sep) > 0:
                self.commit_average_mod_interval[pr_commit.hash] = sum(self.mod_time_sep) / len(self.mod_time_sep)
            else:
                self.commit_average_mod_interval[pr_commit.hash] = 0

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        return self.commit_average_mod_interval.get(pr_commit.hash, 0)