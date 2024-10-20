from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_total_lines_authored_in_project import Data_Provider_Total_Lines_Authored_In_Project

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
        #author => lines contributed
        self.lines_per_author = {}
        self.data_provider_tla_in_project = Data_Provider_Total_Lines_Authored_In_Project(repository)

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider_tla_in_project]

    #Returns name of the metric as str
    def get_metric_name(self):
        return "EXP"
    
    #Returns at what level was the metric collected at
    def get_collection_level(self):
        return "author"

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        author = helper_commit_author(commit)
        self.lines_per_author[author] = self.lines_per_author.get(author, 0) + file.added_lines + file.deleted_lines

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        tla_in_project = self.data_provider_tla_in_project.get_data()
        if tla_in_project:
            #Calculate percentages of contribution per author
            author_contrib_in_percentage = {}
            for author in self.lines_per_author:
                author_contrib_in_percentage[author] = (self.lines_per_author[author] / tla_in_project)
            #Calculate inner product
            inner_product = 1
            for author in author_contrib_in_percentage:
                inner_product = inner_product * (1+ author_contrib_in_percentage[author])
            #Calculate exponent 1/num of authors
            exponent = 1/len(author_contrib_in_percentage)
            #Raise the inner product to the exponent and subtract 1
            self.geometric_mean_of_exp[commit.hash] = (inner_product ** exponent) - 1

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        #EXP waypoint set for current_commit
        return self.geometric_mean_of_exp.get(commit_hash, 0)