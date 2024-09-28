from metrics.metric import Metric
from metrics.metric_helper_functions import *
from pydriller import ModificationType

#OWN
#Measures the percentage of the lines authored by the highest contributor of a file in the considered commit. 
class Metric_OWN(Metric):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.lines_authored_per_file = {}
        self.lines_authored_per_commit = {}
        self.largest_contributor_per_file = {}

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
        #is refactorings commit
        if is_rfm_commit:
            self.lines_authored_per_commit.setdefault(pr_commit.hash, {})[file.new_path] = {"author": author, "lines": lines_authored}

    #Returns the largest contributor to the given file
    def get_largest_contributor_for_file(self, file):
        largest_contributor = self.largest_contributor_per_file.setdefault(file, {})
        #We have not calculated for this file before
        if not largest_contributor:
            largest_contributor = {"author": "",  "lines": 0}
            #Find out the largest contributor
            for author in self.lines_authored_per_file[file]:
                if self.lines_authored_per_file[file][author] > largest_contributor["lines"]:
                    largest_contributor = {"author": author, "lines": self.lines_authored_per_file[file][author]}
            #Store and return
            self.largest_contributor_per_file[file] = largest_contributor
        return largest_contributor

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        metric_own = []
        for file in self.lines_authored_per_commit[cur_rfm_commit["commit_hash"]]:
            files_higest_contributor = self.get_largest_contributor_for_file(file)
            data = {"file": file, "metric":0}
            #largest contributor is the author of current rfm_commit
            if self.lines_authored_per_commit[cur_rfm_commit["commit_hash"]][file]["author"] == files_higest_contributor["author"]:
                #percentage of the lines authored by the highest contributor
                data["metric"] = (self.lines_authored_per_commit[cur_rfm_commit["commit_hash"]][file]["lines"] / files_higest_contributor["lines"])
            metric_own.append(data)
        #Sum to commit level, normalize using normal count
        if metric_own:
            return helper_summ_to_commit_level(metric_own) / len(metric_own)
        return 0