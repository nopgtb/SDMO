from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_packages_modified import Data_Provider_Packages_Modified

# - Java file can only be part of one package
# - Package that the file belongs to shown by keyword package *;
# - Run through all modified rfm_files
#   - Regex the code for keyword package and extract package name
#   - Count number of packages found

#NSCTR
#The number of different packages touched by the developer in commits where the file has been modified. 
class Metric_NSCTR(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.total_neighbour_packages_modified = {}
        self.data_provider = Data_Provider_Packages_Modified(repository)

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, pr_commit, is_rfm_commit, rfm_commit):
        metric_data = self.data_provider.get_data()
        #Check we have data and that the hash has data
        #If empty commit it might not have any
        if metric_data and pr_commit.hash in metric_data.keys():
            #Run trough all files in commit and calculate their affect on the total of packages modified
            packages_modified_in_commit = []
            file_effect_on_total = {}
            for file in metric_data[pr_commit.hash]:
                new_packages_modified_in_commit = packages_modified_in_commit + metric_data[pr_commit.hash][file]
                file_effect_on_total[file] = len(list(set(new_packages_modified_in_commit))) - len(packages_modified_in_commit)
                packages_modified_in_commit = new_packages_modified_in_commit
            total_packages_modified = len(packages_modified_in_commit)
            #Run trough files in this commit and calculate neighbour packages touched
            for file in metric_data[pr_commit.hash]:
                self.total_neighbour_packages_modified[file] = self.total_neighbour_packages_modified.get(file, []) + [(total_packages_modified - file_effect_on_total[file])]

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        #NSCTR Metric per rfm files in the rfm commit
        return helper_sum_metric_per_file(cur_rfm_commit["rfm_data"]["refactored_files"], self.total_neighbour_packages_modified)
    
    #Returns at what level was the metric collected at
    def get_collection_level():
        return "file"