from .data_provider_interface import Data_Provider_Interface
from pydriller import ModificationType

#Metrics rely on common data. Instead of each metric calculating it on its own
#data provider will provide it from single source making it available for all metrics
class Data_Provider_Total_Lines_Authored_In_Project(Data_Provider_Interface):

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        self.lines_authored_in_project = self.lines_authored_in_project + (file.added_lines + file.deleted_lines)

    #Initialize and Reset the data
    def reset_data(self):
        #Number of linesn authored in project
        self.lines_authored_in_project = 0

    #Returns the data of the data provider
    def get_data(self):
        return self.lines_authored_in_project