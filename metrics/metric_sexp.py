from datetime import datetime, timedelta
from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import Data_Calculator_Util
from pydriller import ModificationType

#SEXP
#The number of commits a given developer performs in the considered package containing the given file.
class Metric_SEXP(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        #package => author => number of commits
        self.package_commits_made = {}
        #Hash => [{file:metric}]
        self.commits_made_in_package_waypoint = {}
        self.packages_in_this_commit = []

    #Data providers for the metric
    def get_data_providers(self):
        return []
    
    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "SEXP"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "file"

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        self.packages_in_this_commit = []
        #We are calculating this commit
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.commits_made_in_package_waypoint[commit.hash] = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #Fetch file package
        packages = Data_Calculator_Util.extract_modified_packages(file)
        if packages:
            author = Data_Calculator_Util.get_commit_author(commit)
            #Have we seen this package already in this commit?
            if not packages[0] in self.packages_in_this_commit:
                #If not make note that the author commited on this package
                self.packages_in_this_commit.append(packages[0])
                self.package_commits_made.setdefault(packages[0], {}).setdefault(author, 0)
                self.package_commits_made[packages[0]][author] = self.package_commits_made[packages[0]][author] + 1

            #We are calculating this file
            if is_commit_of_interest or not calc_only_commits_of_interest:
                #Number of commits made to the package by the author
                self.commits_made_in_package_waypoint[commit.hash].append({"file": file.new_path, "metric": self.package_commits_made[packages[0]][author]})

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.commits_made_in_package_waypoint.get(commit_hash, None)