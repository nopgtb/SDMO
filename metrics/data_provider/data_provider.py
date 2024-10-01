#Metrics rely on common data. Instead of each metric calculating it on its own
#data provider will provide it from single source making it available for all metrics
#Avoiding duplicated work
class Data_Provider(object):

    #Store the repo
    def __init__(self, repository):
        self.repository = repository

    #All providers are singeltons. We want single provider for each type of data
    def __new__(cls, repository):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Data_Provider, cls).__new__(cls)
            #initialize subclass data structure
            cls.instance.reset_data()
        return cls.instance
    
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

    #Start a external proc for the data
    def pre_calc_run_external(self):
        pass

    #Wait for the external proc to finish
    #and make its data available to metrics
    def pre_calc_wait_for_external(self):
        pass
    
    #Initialize and Reset the data
    def reset_data(self):
        pass

    #Returns the data of the data provider
    def get_data(self):
        return None