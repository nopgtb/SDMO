from .data_provider_interface import Data_Provider_Interface
from pydriller import ModificationType

#Metrics rely on common data. Instead of each metric calculating it on its own
#data provider will provide it from single source making it available for all metrics
class Data_Provider_Commits_From_Last_Rfmc(Data_Provider_Interface):

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.commits_per_file[file.new_path] = self.commits_per_file.setdefault(file.old_path, [])
        #Add commit to the file calc
        self.commits_per_file.setdefault(file.new_path, []).append(1)

    #If the calculator needs to reset calculations
    #at somepoint this is where to do it
    #its called last after pre_calc_per_* functions
    def pre_calc_check_for_reset(self, pr_commit, is_rfm_commit, rfm_commit):
        #Reset the data if rfm commit
        if is_rfm_commit:
            self.reset_data()
    
    #Initialize and Reset the data
    def reset_data(self):
        #File => [1 per commit file appeared in]
        self.commits_per_file = {}

    #Returns the data of the data provider
    def get_data(self):
        return self.commits_per_file