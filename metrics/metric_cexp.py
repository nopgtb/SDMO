from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *
from metrics.data_provider.data_provider_commits_per_file_per_author import Data_Provider_Commits_Per_File_Per_Author

#CEXP
#The number of commits performed on the given file by the committer up to the refactoring commit being analyzed. 
class Metric_CEXP(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.data_provider = Data_Provider_Commits_Per_File_Per_Author(repository)
        #Hash => number of commits made on files by author
        self.commits_made_by_author_on_files = {}
        self.commits_made_by_author = []

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]
    
    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, pr_commit, is_rfm_commit, rfm_commit):
        self.commits_made_by_author = []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        metric_data = self.data_provider.get_data()
        author = helper_commit_author(pr_commit)
        #rfm commit and we have data for file and author
        if is_rfm_commit and metric_data and file.new_path in metric_data.keys() and author in metric_data[file.new_path].keys():
            self.commits_made_by_author.append(sum(metric_data[file.new_path][author]))

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, pr_commit, is_rfm_commit, rfm_commit):
        if is_rfm_commit:
            self.commits_made_by_author_on_files[pr_commit.hash] = sum(self.commits_made_by_author)

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        return self.commits_made_by_author_on_files.get(pr_commit.hash, 0)