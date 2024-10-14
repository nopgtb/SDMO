from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_contributions_per_file_per_author import Data_Provider_Contributions_Per_File_Per_Author

#MINOR
#The number of contributors who contributed less than 5% of a given file up to the considered commit. 
class Metric_MINOR(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.minor_authors_in_file_waypoint = {}
        self.minor_author_treshold = 0.05
        self.data_provider = Data_Provider_Contributions_Per_File_Per_Author(repository)

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, pr_commit, is_rfm_commit, rfm_commit):
        if is_rfm_commit:
            self.minor_authors_in_file_waypoint[pr_commit.hash] = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        metric_data = self.data_provider.get_data()
        #Make waypoint for rfm commit files
        if is_rfm_commit and metric_data and file.new_path in metric_data.keys():
            #Sum of total lines contributed to the file between all the developers
            total_lines = sum([metric_data[file.new_path][author] for author in metric_data[file.new_path]])
            if total_lines > 0:
                self.minor_authors_in_file_waypoint[pr_commit.hash].append(
                    {
                        "file": file.new_path,
                        #Count the number of developers that have contributed less or equal amount of lines
                        #than the threshold set in self.minor_author_treshold
                        "metric": len([author for author in metric_data[file.new_path] if (metric_data[file.new_path][author] / total_lines) >= self.minor_author_treshold])
                    }
                )

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        return helper_sum_to_commit_level(self.minor_authors_in_file_waypoint.get(pr_commit.hash, []))