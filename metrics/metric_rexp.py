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
        self.commits_made_coi_waypoints = {}

    #Data providers for the metric
    def get_data_providers(self):
        return []
    
    #Returns name of the metric as str
    def get_metric_name(self):
        return "REXP"
    
    #Returns at what level was the metric collected at
    def get_collection_level(self):
        return "file"

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.commits_made_coi_waypoints[commit.hash] = {}

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.commits_made[file.new_path] = self.commits_made.setdefault(file.old_path, {})
        current_date = commit.committer_date
        current_date_str = current_date.strftime("%Y_%m_%d")
        author = helper_commit_author(commit)
        date_authors = self.commits_made.setdefault(file.new_path, {}).setdefault(current_date_str, {}) 
        date_authors[author] = date_authors.get(author, 0) + 1
        #Make waypoint for commits
        if is_commit_of_interest or not calc_only_commits_of_interest:
            #Run a 30 day (month) rolling window on 
            time_diff = 30
            while time_diff > 0:
                date_key = (current_date - timedelta(days = time_diff)).strftime("%Y_%m_%d")
                #if file has commits on the date
                if date_key in self.commits_made[file.new_path].keys() and author in self.commits_made[file.new_path][date_key].keys():
                    #Append authors commits to the count
                    self.commits_made_coi_waypoints[commit.hash][file.new_path] = self.commits_made_coi_waypoints[commit.hash].get(file.new_path, 0) + self.commits_made[file.new_path][date_key][author]
                time_diff = time_diff -1

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.commits_made_coi_waypoints.get(commit_hash, None)