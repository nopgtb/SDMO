#Abstract class for implementing metric calculations
class Metric:
    #Store the repo
    def __init__(self, repository):
        self.repository = repository

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        pass

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, pr_commit, is_rfm_commit, rfm_commit):
        pass

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, pr_commit, is_rfm_commit, rfm_commit):
        pass
    
    #Called once per repository
    def pre_calc_per_repository(self):
        pass

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        pass
    
    #Data provider for the metric
    def get_data_provider(self):
        return None