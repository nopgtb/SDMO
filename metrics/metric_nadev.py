from metrics.metric import Metric
from metrics.metric_helper_functions import *
from pydriller import ModificationType

#- Num of devs in neirbouring files (Other files in our rfm_commit)
#    - Changed the same set of rfm_files, exluding considered file (neighbours)
#    - Repeat per rfm_file in rfm_commit
#           - Pick excluded file from rfm_commits rfm_files
#           - consider each previous commit
#               -Search them for changes to the neighbour files of the excluded file
#                   - Sum the number of devs contributing to the neigbour files of the excluded file
#                       - = NADEV for our file
#    - Starting from last rfm commit or start

#NADEV
#The number of active developers who, given the considered commit, changed the same specific files along with the given file up
#to the considered commit starting from the previous refactoring commit (consider the commit with the introduction of the file
#as the previous commit when dealing with the first refactoring commit).
class Metric_NADEV(Metric):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.contributors_per_file = {}
        self.contributors_per_files_neighbours_waypoints = {}

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.contributors_per_file[file.new_path] = self.contributors_per_file.setdefault(file.old_path, {})
        #Per path have dict of authors with number of lines contributed
        author = pr_commit.author.email.strip()
        contribs_path_for_path = self.contributors_per_file.setdefault(file.new_path, {})
        contribs_path_for_path[author] = contribs_path_for_path.get(author, 0) + file.added_lines + file.deleted_lines

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, pr_commit, is_rfm_commit, rfm_commit):
        if is_rfm_commit:
            #Make a waypoint for this rfm_commit. Number of contributors per rfm_files neighbours
            self.contributors_per_files_neighbours_waypoints[pr_commit.hash] = helper_make_waypoint_per_rfm_file_neigbours(
                self.contributors_per_file,
                rfm_commit["rfm_data"]["refactored_files"],
                lambda data: len(data.keys())
            )
            #Start from counting from 0
            self.contributors_per_file = {}

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        #NADEV waypoint set for current_commit
        if cur_rfm_commit["commit_hash"] in self.contributors_per_files_neighbours_waypoints.keys():
            return self.contributors_per_files_neighbours_waypoints[cur_rfm_commit["commit_hash"]]
        return 0