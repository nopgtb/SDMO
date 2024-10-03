from metrics.metric_interface import Metric_Interface
from metrics.data_provider.data_provider_packages_modified import Data_Provider_Packages_Modified

# - Java file can only be part of one package
# - Package that the file belongs to shown by keyword package *;
# - Run through all modified rfm_files
#   - Regex the code for keyword package and extract package name
#   - Count number of packages found

#SCTR
#The number of packages modified by the committer in the considered commit.
class Metric_SCTR(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        self.data_provider = Data_Provider_Packages_Modified(repository)

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        metric_data = self.data_provider.get_data()
        if metric_data:
            #SCTR count the unique packages modified in our commit
            if cur_rfm_commit["commit_hash"] in metric_data.keys():
                #for commit => for file => for [packages] if package
                return len([pn for file in metric_data[pr_commit.hash] for pn in metric_data[pr_commit.hash][file] if pn])
        return 0