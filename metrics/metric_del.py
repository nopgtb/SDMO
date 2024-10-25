from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from pydriller import ModificationType

#DEL
#The normalized (by the total number of deleted lines in that file since it was created) number of lines removed from a given file in the considered commit.
class Metric_DEL(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        #hash => file => [file norms]
        self.lines_deleted_waypoint = {}
        #File => [Num of lines added]
        self.lines_deleted = {}

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
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.lines_deleted_waypoint[commit.hash] = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.lines_deleted[file.new_path] = self.lines_deleted.setdefault(file.old_path, [])
        #Add deleted and added lines
        self.lines_deleted.setdefault(file.new_path, []).append(file.deleted_lines)

        if (is_commit_of_interest or not calc_only_commits_of_interest) and file.new_path in self.lines_deleted.keys():
            #sum total number of lines deleted from the given file
            total_lines_deleted_from_file = sum(self.lines_deleted[file.new_path])
            if total_lines_deleted_from_file > 0:
                #Normalize using the commits added lines
                self.lines_deleted_waypoint[commit.hash].append((file.deleted_lines / total_lines_deleted_from_file))

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        #normals for the commits file
        lines_deleted = self.lines_deleted_waypoint.get(commit_hash, [])
        if lines_deleted:
            #Calculate the average of them for the commit level value
            return sum(lines_deleted) / len(lines_deleted)
        return 0