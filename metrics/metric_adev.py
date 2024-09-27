from datetime import datetime
from metrics.metric import Metric
from metrics.metric_helpers import *
from pydriller import ModificationType

#ADEV
#The number of developers who modified a given file up to the considered commit starting from previous refactoring commit
#(consider the commit with the introduction of the file as the previous commit when dealing with the first refactoring commit).
class Metric_ADEV(Metric):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.contributors_per_file = {}
        self.contributors_per_rcfrc = {}

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_rfm_commit, rfm_commit):
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            self.contributors_per_file[file.new_path] = self.contributors_per_file.setdefault(file.old_path, {})
        #Per path have dict of authors with number of lines contributed
        author = commit.author.email.strip()
        contribs_path_for_path = self.contributors_per_file.setdefault(file.new_path, {})
        contribs_path_for_path[author] = contribs_path_for_path.get(author, 0) + file.added_lines + file.deleted_lines

    #Makes a waypoint from given data
    def make_waypoint(self, contributors, commit, rfm_commit):
        #Set ADEV waypoint for each file in the commit
        waypoint = []
        for rfm_file in rfm_commit["rfm_data"]["refactored_files"]:
            #File has contributors
            if rfm_file in contributors.keys():
                #Append object: file => unique count of devs
                waypoint.append(
                    {
                        "file": rfm_file,
                        "metric": len(list(set(contributors[rfm_file].keys())))
                    }
                )
        return waypoint

    #Called once per commit, includes current commit
    def pre_calc_per_commit(self, commit, is_rfm_commit, rfm_commit):
        if is_rfm_commit:
            #Make waypoint
            self.contributors_per_rcfrc[commit.hash] = self.make_waypoint(self.contributors_per_file, commit, rfm_commit)
            #Start from counting from 0
            self.contributors_per_file = {}

    #Called to fetch the metric value for current commit
    def get_metric(self, previous_commit, current_commit):
        #ADEV waypoint set for current_commit
        if current_commit["commit_hash"] in self.contributors_per_rcfrc.keys():
            return helper_summ_to_commit_level(self.contributors_per_rcfrc[current_commit["commit_hash"]])
        return 0