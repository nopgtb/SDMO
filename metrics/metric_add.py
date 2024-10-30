from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from pydriller import ModificationType

#ADD
#The normalized (by the total number of added lines in that file since it was created) number of lines added to a given file in the considered commit
class Metric_ADD(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        #hash => file => [Commits files normalized line add value]
        self.normal_line_add_waypoint = {}
        #File => [Lines added to the given file. Array because we need to reference this]
        self.files_total_lines_added = {}

    #Data providers for the metric
    def get_data_providers(self):
        return []
    
    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "ADD"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "commit"

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #Are we calculating this commit?
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.normal_line_add_waypoint[commit.hash] = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #Keep track of additions to the files for the total
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.files_total_lines_added[file.new_path] = self.files_total_lines_added.setdefault(file.old_path, [])
        #Append number of lines added in this commit. This is an array because we cant reference a number
        self.files_total_lines_added.setdefault(file.new_path, []).append(file.added_lines)

        #We are calculating this file and we have data for it
        if (is_commit_of_interest or not calc_only_commits_of_interest) and file.new_path in self.files_total_lines_added.keys():
            #Number of lines added to this file during its lifetime
            total_lines_added_to_file = sum(self.files_total_lines_added[file.new_path])
            if total_lines_added_to_file > 0:
                #This files contribution to the commits waypoint is the normalized lines added
                self.normal_line_add_waypoint[commit.hash].append((file.added_lines / total_lines_added_to_file))

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        lines_added = self.normal_line_add_waypoint.get(commit_hash, [])
        if lines_added:
            #Calculate the average for the commits value
            #The description doesn't really specify a way for us to get 
            #to the commit level so i picked average 
            return sum(lines_added) / len(lines_added)
        return None