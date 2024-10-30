from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from pydriller import ModificationType

#DEL
#The normalized (by the total number of deleted lines in that file since it was created) number of lines removed from a given file in the considered commit.
class Metric_DEL(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        #hash => file => [Normalize lines deleted values for the commits files]
        self.normal_line_deletion_waypoint = {}
        #File => [Number of lines deleted during its lifetime. Array because we can't reference a number]
        self.file_total_lines_deleted = {}

    #Data providers for the metric
    def get_data_providers(self):
        return []

    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "DEL"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "commit"

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #Are we calculating this commit?
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.normal_line_deletion_waypoint[commit.hash] = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.file_total_lines_deleted[file.new_path] = self.file_total_lines_deleted.setdefault(file.old_path, [])
        #Add deleted lines. This is an array because we need to reference it
        self.file_total_lines_deleted.setdefault(file.new_path, []).append(file.deleted_lines)
        #We are calculating this file and we have data for it
        if (is_commit_of_interest or not calc_only_commits_of_interest) and file.new_path in self.file_total_lines_deleted.keys():
            #Number of lines deleted in the file since its creation
            total_lines_deleted_from_file = sum(self.file_total_lines_deleted[file.new_path])
            if total_lines_deleted_from_file > 0:
                #This files contribution to the commits value is its lines deleted normalized by the total number of lines deleted since its creation
                self.normal_line_deletion_waypoint[commit.hash].append((file.deleted_lines / total_lines_deleted_from_file))

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        lines_deleted = self.normal_line_deletion_waypoint.get(commit_hash, [])
        if lines_deleted:
            #Calculate the average lines deleted normal
            #Metric description doesnt specify how to get to the 
            #Commit level so I picked the average
            return sum(lines_deleted) / len(lines_deleted)
        return None