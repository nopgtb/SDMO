from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from pydriller import ModificationType

#AGE
#The average time interval between the current and the last time the changed files were modified. (Unit: Days) 
class Metric_AGE(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        #Commit hash => days on average since last change
        self.commit_average_mod_interval = {}
        #file => [datetime of commit]
        self.file_modification_age = {}
        self.mod_time_sep = []

    #Data providers for the metric
    def get_data_providers(self):
        return []

    #Returns name of the metric as str
    def get_metric_name(self):
        return "AGE"
    
    #Returns at what level was the metric collected at
    def get_collection_level(self):
        return "commit"

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        self.mod_time_sep = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #Keep track of times files were changed
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.file_modification_age[file.new_path] = self.file_modification_age.setdefault(file.old_path, [])
        self.file_modification_age.setdefault(file.new_path, []).append(commit.committer_date)
        
        #Add data to the average calculation 
        if is_commit_of_interest or not calc_only_commits_of_interest:
            if self.file_modification_age and file in self.file_modification_age.keys() and len(self.file_modification_age[file]) > 1:
                #Calculate the time between current mod and last mod
                self.mod_time_sep.append((self.file_modification_age[file][-1] - self.file_modification_age[file][len(self.file_modification_age[file])-2]).days)
        
    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if is_commit_of_interest or not calc_only_commits_of_interest:
            #Calcualte the average
            if len(self.mod_time_sep) > 0:
                self.commit_average_mod_interval[commit.hash] = sum(self.mod_time_sep) / len(self.mod_time_sep)
            else:
                self.commit_average_mod_interval[commit.hash] = 0

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.commit_average_mod_interval.get(commit_hash, 0)