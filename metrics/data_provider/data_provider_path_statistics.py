from .data_provider_interface import Data_Provider_Interface
from metrics.data_calculator_util import *
from pathlib import PurePath

#Metrics rely on common data. Instead of each metric calculating it on its own
#data provider will provide it from single source making it available for all metrics
class Data_Provider_Path_Statistics(Data_Provider_Interface):

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, pr_commit, is_rfm_commit, rfm_commit):
        self.folders_involved = []
        self.path_data[pr_commit.hash] = {"directory_count":0, "file_count":0}

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        #Files modified in commit
        self.path_data[pr_commit.hash]["file_count"] = self.path_data[pr_commit.hash]["file_count"] + 1 
        #Extract folders from files path
        if file.new_path:
           for part in PurePath(file.new_path).parts:
               #Append everythign that isnt the file name
               if part != file.filename:
                    self.folders_involved.append(part)

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, pr_commit, is_rfm_commit, rfm_commit):
        #How many directories were used in this commit
        self.path_data[pr_commit.hash]["directory_count"] = len(list(set(self.folders_involved)))

    #Initialize and Reset the data
    def reset_data(self):
        #commit.hash => {"directory_count", "file_count"}
        self.path_data = {}

    #Returns the data of the data provider
    def get_data(self):
        return self.path_data