from datetime import datetime, timedelta
from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import Data_Calculator_Util
from pydriller import ModificationType

#rolling time window of 30 days in the past, starting from commiting date
#   - calculate per file
#       -author times they have commited to the file within the time window 

#REXP
#The number of commits performed on the given file by the committer in the last month.
class Metric_REXP(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        #file => date_str => author => num of commits
        self.commits_made = {}
        #commit => [{"file", "metric"}]
        self.commits_made_on_files_waypoint = {}

    #Data providers for the metric
    def get_data_providers(self):
        return []
    
    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "REXP"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "file"

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #We are calculating this commit
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.commits_made_on_files_waypoint[commit.hash] = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.commits_made[file.new_path] = self.commits_made.setdefault(file.old_path, {})
        #Note the commit made by author on this date key
        current_date = commit.committer_date
        current_date_str = current_date.strftime("%Y_%m_%d")
        author = Data_Calculator_Util.get_commit_author(commit)
        date_authors = self.commits_made.setdefault(file.new_path, {}).setdefault(current_date_str, {}) 
        date_authors[author] = date_authors.get(author, 0) + 1
        
        #We are calculating this commit
        if is_commit_of_interest or not calc_only_commits_of_interest:
            time_diff = 30
            file_commits_in_last_month = 0
            #Run a 30 day (month) rolling window on data
            while time_diff > 0:
                date_key = (current_date - timedelta(days = time_diff)).strftime("%Y_%m_%d")
                #if file has commits on the date by the author
                if date_key in self.commits_made[file.new_path].keys() and author in self.commits_made[file.new_path][date_key].keys():
                    #Append authors commits to the count
                    file_commits_in_last_month = file_commits_in_last_month + self.commits_made[file.new_path][date_key][author]
                time_diff = time_diff -1
            #Append file info to the waypoint
            self.commits_made_on_files_waypoint[commit.hash].append({
                "file": file.new_path,
                "metric": file_commits_in_last_month
            })

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.commits_made_on_files_waypoint.get(commit_hash, None)