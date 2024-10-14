from .data_provider_interface import Data_Provider_Interface
from metrics.data_calculator_util import *
from pydriller import ModificationType

#Metrics rely on common data. Instead of each metric calculating it on its own
#data provider will provide it from single source making it available for all metrics
class Data_Provider_Contributions_Per_File_Per_Author(Data_Provider_Interface):

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.contributors_per_file[file.new_path] = self.contributors_per_file.setdefault(file.old_path, {})
        #Per path have dict of authors with number of lines contributed
        author = helper_commit_author(pr_commit)
        contribs_path_for_path = self.contributors_per_file.setdefault(file.new_path, {})
        contribs_path_for_path[author] = contribs_path_for_path.get(author, 0) + file.added_lines + file.deleted_lines

    #Initialize and Reset the data
    def reset_data(self):
        #File => Author => Num of contributed lines
        self.contributors_per_file = {}

    #Returns the data of the data provider
    def get_data(self):
        return self.contributors_per_file