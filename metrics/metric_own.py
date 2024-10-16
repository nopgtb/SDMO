from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_contributions_per_file_per_author import Data_Provider_Contributions_Per_File_Per_Author

#OWN
#Measures the percentage of the lines authored by the highest contributor of a file in the considered commit. 
class Metric_OWN(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.lines_authored_per_commit = {}
        self.data_provider = Data_Provider_Contributions_Per_File_Per_Author(repository)

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        #is refactorings commit
        if is_rfm_commit:
            author = helper_commit_author(pr_commit)
            #For rfm commits note the author and his/hers contribution to the file
            self.lines_authored_per_commit.setdefault(pr_commit.hash, {})[file.new_path] = {"author": author, "lines": (file.added_lines + file.deleted_lines)}

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        metric_data = self.data_provider.get_data()
        if metric_data:
            metric_own = []
            for file in self.lines_authored_per_commit[cur_rfm_commit["commit_hash"]]:
                files_higest_contributor = helper_get_largest_contributor_for_file(metric_data, file)
                data = {"file": file, "metric":0}
                #largest contributor is the author of current rfm_commit
                if self.lines_authored_per_commit[cur_rfm_commit["commit_hash"]][file]["author"] == files_higest_contributor["author"]:
                    #percentage of the lines authored by the highest contributor
                    data["metric"] = (self.lines_authored_per_commit[cur_rfm_commit["commit_hash"]][file]["lines"] / files_higest_contributor["lines"])
                metric_own.append(data)
            #Sum to commit level, normalize using normal count
            if metric_own:
                return helper_sum_to_commit_level(metric_own) / len(metric_own)
        return 0