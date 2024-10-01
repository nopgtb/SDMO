from metrics.metric import Metric
from metrics.metric_helper_functions import *
from metrics.data_provider.data_provider_contributions import Data_Provider_Contributions

#MINOR
#The number of contributors who contributed less than 5% of a given file up to the considered commit. 
class Metric_MINOR(Metric):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.minor_authors_in_file_waypoint = {}
        self.minor_author_treshold = 0.05
        self.data_provider = Data_Provider_Contributions(repository)

    #Data provider for the metric
    def get_data_provider(self):
        return self.data_provider

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        if is_rfm_commit:
            metric_data = self.get_data_provider().get_data()
            if metric_data:
                #Function for getting minor author count
                def get_minor_author_count(data):
                    #Sum of total lines contributed to the file between all the developers
                    total_lines = sum([data[author] for author in data])
                    #Count the number of developers that have contributed less or equal amount of lines
                    #than the threshold set in self.minor_author_treshold
                    return len([author for author in data if (data[author] / total_lines) >= self.minor_author_treshold])
                #Make a waypoint for this rfm_commit. Number of unique minor authors per rfm_file
                self.minor_authors_in_file_waypoint[pr_commit.hash] = helper_make_waypoint_per_rfm_file(
                    metric_data, 
                    rfm_commit["rfm_data"]["refactored_files"],
                    get_minor_author_count
                )

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        #MINOR waypoint set for current_commit
        if cur_rfm_commit["commit_hash"] in self.minor_authors_in_file_waypoint.keys():
            return helper_summ_to_commit_level(self.minor_authors_in_file_waypoint[cur_rfm_commit["commit_hash"]])
        return 0