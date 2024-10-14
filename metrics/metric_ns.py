from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_packages_modified import Data_Provider_Packages_Modified

#What is considered a subsystem?
#Packages
#Modules? - javalang targets java 8, so support for modules is questionable. so propably not


#NS
#Number of modified subsystems.
class Metric_NS(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        #hash => num of subsystems modified
        self.subsystems_modified_per_commit = {}
        self.data_provider = Data_Provider_Packages_Modified(repository)

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]
    
    #Count subsystems present in file
    def count_subsystems_modified(self, pr_commit):
        subsystems_present = []
        metric_data = self.data_provider.get_data()
        if metric_data and pr_commit.hash in metric_data.keys():
            #for commit => for file => for [packages] if package
            subsystems_present = [pn for file in metric_data[pr_commit.hash] for pn in metric_data[pr_commit.hash][file] if pn]
        #remove dubplicate entries
        return len(list(set(subsystems_present)))

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, pr_commit, is_rfm_commit, rfm_commit):
        self.subsystems_modified_per_commit[pr_commit.hash] = self.count_subsystems_modified(pr_commit)

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        if pr_commit.hash in self.subsystems_modified_per_commit.keys():
            return self.subsystems_modified_per_commit[pr_commit.hash]
        return 0