from datetime import datetime, timedelta
from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from pydriller import ModificationType

#SEXP
#The number of commits a given developer performs in the considered package containing the given file.
class Metric_SEXP(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        #package => author => number of commits
        self.package_commits_made = {}
        self.package_commits_made_rfm_waypoints = {}
        self.packages_in_this_commit = []

    #Data providers for the metric
    def get_data_providers(self):
        return []
    
    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, pr_commit, is_rfm_commit, rfm_commit):
        self.packages_in_this_commit = []
        if is_rfm_commit:
            self.package_commits_made_rfm_waypoints[pr_commit.hash] = {}

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        #Fetch file package
        packages = helper_extract_modified_packages(file)
        if packages:
            author = helper_commit_author(pr_commit)
            #Keep running count for commits made to the package
            if not packages[0] in self.packages_in_this_commit:
                self.packages_in_this_commit.append(packages[0])
                self.package_commits_made.setdefault(packages[0], {}).setdefault(author, 0)
                self.package_commits_made[packages[0]][author] = self.package_commits_made[packages[0]][author] + 1
            #if is rfm commit make waypoint data
            if is_rfm_commit:
                self.package_commits_made_rfm_waypoints[pr_commit.hash][file.new_path] = self.package_commits_made[packages[0]][author]

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        return self.package_commits_made_rfm_waypoints.get(pr_commit.hash, None)