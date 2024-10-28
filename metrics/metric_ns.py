from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import Data_Calculator_Util

#What is considered a subsystem?
#Packages
#Modules? - javalang targets java 8, so support for modules is questionable. so propably not


#NS
#Number of modified subsystems.
class Metric_NS(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        #hash => num of subsystems modified
        self.subsystems_modified_per_commit = {}
        #file => [packages_modified]
        self.packages_modified_per_commit = {}

    #Data providers for the metric
    def get_data_providers(self):
        return []
    
    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "NS"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "commit"

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        self.packages_modified_per_commit = {}

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #Get Modified packages and append them to commit data
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.packages_modified_per_commit[file.new_path] = Data_Calculator_Util.extract_modified_packages(file)

    #Number of packages modified in this commit
    def count_packages_modified(self, pr_commit):
        packages_present = []
        if self.packages_modified_per_commit:
            #for commit => for file => for [packages] if package
            packages_present = [pn for file in self.packages_modified_per_commit for pn in self.packages_modified_per_commit[file] if pn]
        #remove dubplicate entries
        return len(list(set(packages_present)))
    
    #Count subsystems present in file
    def count_subsystems_modified(self, pr_commit):
        #For now just count the packages modified 
        subsystems_present = self.count_packages_modified(pr_commit)
        return subsystems_present

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.subsystems_modified_per_commit[commit.hash] = self.count_subsystems_modified(commit)

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.subsystems_modified_per_commit.get(commit_hash, None)