from metrics.metric import Metric
from metrics.metric_helper_functions import *
from pydriller import ModificationType

#MINOR
#The number of contributors who contributed less than 5% of a given file up to the considered commit. 
class Metric_MINOR(Metric):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.lines_authored_per_file = {}
        self.minor_authors_in_file_waypoint = {}
        self.minor_author_treshold = 0.05

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.lines_authored_per_file[file.new_path] = self.lines_authored_per_file.setdefault(file.old_path, {})
        #Per path have dict of authors with number of lines contributed
        author = pr_commit.author.email.strip()
        lines_authored = file.added_lines + file.deleted_lines
        contribs_path_for_path = self.lines_authored_per_file.setdefault(file.new_path, {})
        contribs_path_for_path[author] = contribs_path_for_path.get(author, 0) + lines_authored
        #is refactorings commit, time to set waypoint
        if is_rfm_commit:
            #Function for getting minor author count
            def get_minor_author_count(data):
                total_lines = sum([data[author] for author in data])
                return len([author for author in data if (data[author] / total_lines) >= self.minor_author_treshold])
            #Make a waypoint for this rfm_commit. Number of unique minor authors per rfm_file
            self.minor_authors_in_file_waypoint[pr_commit.hash] = helper_make_waypoint_per_rfm_file(
                self.lines_authored_per_file, 
                rfm_commit["rfm_data"]["refactored_files"],
                get_minor_author_count
            )

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        #MINOR waypoint set for current_commit
        if cur_rfm_commit["commit_hash"] in self.minor_authors_in_file_waypoint.keys():
            return helper_summ_to_commit_level(self.minor_authors_in_file_waypoint[cur_rfm_commit["commit_hash"]])
        return 0