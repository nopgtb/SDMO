from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from pydriller import ModificationType

#ADD
#The normalized (by the total number of added lines in that file since it was created) number of lines added to a given file in the considered commit
class Metric_ADD(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        #hash => file => [norms of the files]
        self.lines_added_waypoint = {}
        #File => Lines added
        self.lines_added = {}

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
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.lines_added_waypoint[commit.hash] = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #Keep track of additions to the files for the total
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.lines_added[file.new_path] = self.lines_added.setdefault(file.old_path, [])
        #Add deleted and added lines
        self.lines_added.setdefault(file.new_path, []).append(file.added_lines)

        #Calculate the normal for this file
        if (is_commit_of_interest or not calc_only_commits_of_interest) and file.new_path in self.lines_added.keys():
            #sum total number of lines added to the given file
            total_lines_added_to_file = sum(self.lines_added[file.new_path])
            if total_lines_added_to_file > 0:
                #Normalize using the commits added lines
                self.lines_added_waypoint[commit.hash].append((file.added_lines / total_lines_added_to_file))

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        #Normals per file 
        lines_added = self.lines_added_waypoint.get(commit_hash, [])
        if lines_added:
            #Average of the ADDS across the files of the commits
            return sum(lines_added) / len(lines_added)
        return 0