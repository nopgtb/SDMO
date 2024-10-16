from .data_provider_interface import Data_Provider_Interface
from metrics.data_calculator_util import *
from pydriller import ModificationType

#Metrics rely on common data. Instead of each metric calculating it on its own
#data provider will provide it from single source making it available for all metrics
class Data_Provider_File_Modification_Date(Data_Provider_Interface):

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.file_modification_age[file.new_path] = self.file_modification_age.setdefault(file.old_path, [])
        self.file_modification_age.setdefault(file.new_path, []).append(pr_commit.committer_date)

    #Initialize and Reset the data
    def reset_data(self):
        #file => [datetime of commit]
        self.file_modification_age = {}

    #Returns the data of the data provider
    def get_data(self):
        return self.file_modification_age