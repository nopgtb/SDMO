from .data_provider_interface import Data_Provider_Interface
from metrics.data_calculator_util import *
from pydriller import ModificationType

#Metrics rely on common data. Instead of each metric calculating it on its own
#data provider will provide it from single source making it available for all metrics
class Data_Provider_Commits_Per_File_Per_Author(Data_Provider_Interface):

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #File name changed in this commit
        if file.change_type == ModificationType.RENAME:
            #Reference the previous path for continuity
            self.commits_per_author_per_file[file.new_path] = self.commits_per_author_per_file.setdefault(file.old_path, {})
        #Add commit to the file calc
        author = helper_commit_author(commit)
        file_authors = self.commits_per_author_per_file.setdefault(file.new_path, {})
        file_authors[author] = file_authors.get(author, 0) + 1

    #Initialize and Reset the data
    def reset_data(self):
        #File => Author => num of commits
        self.commits_per_author_per_file = {}

    #Returns the data of the data provider
    def get_data(self):
        return self.commits_per_author_per_file