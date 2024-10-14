from datetime import datetime, timedelta
from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from pydriller import ModificationType

#rolling time window of 30 days in the past, starting from commiting date
#   - calculate per file
#       -author times they have commited to the file within the time window 

#REXP
#The number of commits performed on the given file by the committer in the last month.
class Metric_REXP(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        #file => date_str => author => num of commits
        self.commits_made = {}
        self.commits_made_rfm_waypoints = {}

    #Data providers for the metric
    def get_data_providers(self):
        return []
    
    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, pr_commit, is_rfm_commit, rfm_commit):
        if is_rfm_commit:
            self.commits_made_rfm_waypoints[pr_commit.hash] = {}

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.commits_made[file.new_path] = self.commits_made.setdefault(file.old_path, {})
        current_date = pr_commit.committer_date
        current_date_str = current_date.strftime("%Y_%m_%d")
        author = helper_commit_author(pr_commit)
        date_authors = self.commits_made.setdefault(file.new_path, {}).setdefault(current_date_str, {}) 
        date_authors[author] = date_authors.get(author, 0) + 1
        #Make waypoint for rfm commits
        if is_rfm_commit:
            #Run a 30 day (month) rolling window on 
            time_diff = 30
            while time_diff > 0:
                date_key = (current_date - timedelta(days = time_diff)).strftime("%Y_%m_%d")
                #if file has commits on the date
                if date_key in self.commits_made[file.new_path].keys() and author in self.commits_made[file.new_path][date_key].keys():
                    #Append authors commits to the count
                    self.commits_made_rfm_waypoints[pr_commit.hash][file.new_path] = self.commits_made_rfm_waypoints[pr_commit.hash].get(file.new_path, 0) + self.commits_made[file.new_path][date_key][author]
                time_diff = time_diff -1

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        return self.commits_made_rfm_waypoints.get(pr_commit.hash, None)