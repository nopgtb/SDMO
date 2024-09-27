from datetime import datetime
from metrics.metric import Metric
from metrics.metric_helpers import *
from pydriller import ModificationType
from pydriller.metrics.process.commits_count import CommitsCount

#COMM
#The cumulative number of commits made to a file up to the considered commit starting from the previous refactoring commit
#(consider the commit with the introduction of the file as the previous commit when dealing with the first refactoring commit)
class Metric_COMM(Metric):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.commits_made = {}
        self.commit_made_waypoints = {}

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_rfm_commit, rfm_commit):
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            #Reference the new path to the old path
            self.commits_made[file.new_path] = self.commits_made.setdefault(file.old_path, [])
        #Add commit to the file calc
        self.commits_made.setdefault(file.new_path, []).append(1)
    
    #Makes a waypoint from given data
    def make_waypoint(self, commits_made, commit, rfm_commit):
        #Set COMM waypoint for each file in the commit
        waypoint = []
        for rfm_file in rfm_commit["rfm_data"]["refactored_files"]:
            #File has contributors
            if rfm_file in commits_made.keys():
                #Append object: file => count of made commits
                waypoint.append(
                    {
                        "file": rfm_file,
                        "metric": sum(commits_made[rfm_file])
                    }
                )
        return waypoint

    #Called once per commit, includes current commit
    def pre_calc_per_commit(self, commit, is_rfm_commit, rfm_commit):
        if is_rfm_commit:
            #make waypoint
            self.commit_made_waypoints[commit.hash] = self.make_waypoint(self.commits_made, commit, rfm_commit)
            #start counting from 0
            self.commits_made = {}

    #Called to fetch the metric value for current commit
    def get_metric(self, previous_commit, current_commit):
        #COMM waypoint set for current_commit
        if current_commit["commit_hash"] in self.commit_made_waypoints.keys():
            return helper_summ_to_commit_level(self.commit_made_waypoints[current_commit["commit_hash"]])
        return 0