#Abstract class for implementing metric calculations
class Metric:
    #Store the repo
    def __init__(self, repository):
        self.repository = repository

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_rfm_commit, rfm_commit):
        pass

    #Called once per commit, includes current commit
    def pre_calc_per_commit(self, commit, is_rfm_commit, rfm_commit):
        pass
    
    #Called once per repository
    def pre_calc_per_repository(self):
        pass

    #Called to fetch the metric value for current commit
    def get_metric(self, previous_commit, current_commit):
        pass