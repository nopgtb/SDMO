#Abstract class providing interface
class Data_Calculator_Interface(object):

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        pass

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        pass

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        pass
    
    #Called once per repository
    def pre_calc_per_repository(self):
        pass

    #Start a external proc for the data
    def pre_calc_run_external(self, repository, branch, commits_of_interest, analyze_only_commits_of_interest):
        pass

    #Wait for the external proc to finish
    #and make its data available to metrics
    def pre_calc_wait_for_external(self):
        pass

    #If the calculator needs to reset calculations
    #at somepoint this is where to do it
    #its called last after pre_calc_per_* functions
    def pre_calc_check_for_reset(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        pass

    #Reset calculator data
    def reset_data(self):
        pass