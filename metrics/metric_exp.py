from metrics.metric_interface import Metric_Interface
from metrics.metric_helper_functions import *
from metrics.data_provider.data_provider_contributions_per_author import Data_Provider_Contributions_Per_Author
from metrics.data_provider.data_provider_total_lines_authored_in_project import Data_Provider_Total_Lines_Authored_In_Project

#per rfm commit
#   - Calculate exp of all devs in project at the time
#       - percentage of authered lines in project
#   - Calculate geometric mean using the exps
#   - ([(1 + E1) *... (1+En)] ^1/n) - 1 

#EXP
#The geometric mean of the experience (in terms of code modification) of all developers across the project.
class Metric_EXP(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        #Commit => geometric_mean of exp
        self.geometric_mean_of_exp = {}
        self.data_provider_author_contributions = Data_Provider_Contributions_Per_Author(repository)
        self.data_provider_tla_in_project = Data_Provider_Total_Lines_Authored_In_Project(repository)

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider_author_contributions, self.data_provider_tla_in_project]

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, pr_commit, is_rfm_commit, rfm_commit):
        author_contrib_data = self.data_provider_author_contributions.get_data()
        tla_in_project = self.data_provider_tla_in_project.get_data()
        if author_contrib_data and tla_in_project:
            #Calculate percentages of contribution per author
            author_contrib_in_percentage = {}
            for author in author_contrib_data:
                author_contrib_in_percentage[author] = (author_contrib_data[author] / tla_in_project)
            #Calculate inner product
            inner_product = 1
            for author in author_contrib_in_percentage:
                inner_product = inner_product * (1+ author_contrib_in_percentage[author])
            #Calculate exponent 1/num of authors
            exponent = 1/len(author_contrib_in_percentage)
            #Raise the inner product to the exponent and subtract 1
            self.geometric_mean_of_exp[pr_commit.hash] = (inner_product ** exponent) - 1

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        #EXP waypoint set for current_commit
        if cur_rfm_commit["commit_hash"] in self.geometric_mean_of_exp.keys():
            return self.geometric_mean_of_exp[cur_rfm_commit["commit_hash"]]
        return 0
    
    #Returns at what level was the metric collected at
    def get_collection_level():
        return "author"