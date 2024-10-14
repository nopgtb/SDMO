from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_lines_changed import Data_Provider_Lines_Changed

#DEL
#The normalized (by the total number of deleted lines in that file since it was created) number of lines removed from a given file in the considered commit.
class Metric_DEL(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.data_provider = Data_Provider_Lines_Changed(repository)

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        metric_data = self.data_provider.get_data()
        if metric_data:
            metric_data = metric_data["deleted"]
            #Sum all removed lines per refactored lines
            total_lines_removed = helper_sum_metric_per_file(cur_rfm_commit["rfm_data"]["refactored_files"], metric_data)
            #Get lines removed in our specific commit
            commit_lines_removed = [{"file":rfm_file["new_path"], "metric":len(rfm_file["diff_parsed"]["deleted"])} for rfm_file in cur_rfm_commit["diff"]]
            #calculate normals per file
            metric_del = helper_normalized_metric_per_file(commit_lines_removed, total_lines_removed)
            #Sum to commit level, normalize using normal count
            if metric_del:
                return helper_sum_to_commit_level(metric_del) / len(metric_del)
        return 0