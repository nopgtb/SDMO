from .data_provider_interface import Data_Provider_Interface
from pydriller import ModificationType

#Metrics rely on common data. Instead of each metric calculating it on its own
#data provider will provide it from single source making it available for all metrics
class Data_Provider_Contributions_Per_Author(Data_Provider_Interface):

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        author = pr_commit.author.email.strip()
        self.contributors_per_author[author] = self.contributors_per_author.get(author, 0) + file.added_lines + file.deleted_lines

    #Initialize and Reset the data
    def reset_data(self):
        #Author => Num of contributed lines
        self.contributors_per_author = {}

    #Returns the data of the data provider
    def get_data(self):
        return self.contributors_per_author