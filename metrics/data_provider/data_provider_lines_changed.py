from .data_provider_interface import Data_Provider_Interface
from pydriller import ModificationType

#Metrics rely on common data. Instead of each metric calculating it on its own
#data provider will provide it from single source making it available for all metrics
class Data_Provider_Lines_Changed(Data_Provider_Interface):

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.lines_Changed["added"][file.new_path] = self.lines_Changed.setdefault(file.old_path, [])
            self.lines_Changed["deleted"][file.new_path] = self.lines_Changed.setdefault(file.old_path, [])
        #Add deleted and added lines
        self.lines_Changed["added"].setdefault(file.new_path, []).append(file.added_lines)
        self.lines_Changed["deleted"].setdefault(file.new_path, []).append(file.deleted_lines)

    #Initialize and Reset the data
    def reset_data(self):
        #added => File => [Num of lines added]
        #deleted => File => [Num of lines added]
        self.lines_Changed = {"added":{}, "deleted":{}}

    #Returns the data of the data provider
    def get_data(self):
        return self.lines_Changed