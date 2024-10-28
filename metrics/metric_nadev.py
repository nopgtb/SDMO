from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import Data_Calculator_Util
from metrics.data_provider.data_provider_author_per_commit import Data_Provider_Author_Per_Commit
from metrics.data_provider.data_provider_files_in_commit import Data_Provider_Files_In_Commit

#NADEV
#The number of active developers who, given the considered commit, changed the same specific files along with the given file up
#to the considered commit starting from the previous refactoring commit (consider the commit with the introduction of the file
#as the previous commit when dealing with the first refactoring commit).
class Metric_NADEV(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        self.act_devs_waypoint = {}
        self.previous_coi_commit = None
        self.commit_author_data = Data_Provider_Author_Per_Commit()
        self.files_in_commit = Data_Provider_Files_In_Commit()

    #Data providers for the metric
    def get_data_providers(self):
        return [self.commit_author_data, self.files_in_commit]

    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "NADEV"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "file"

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.act_devs_waypoint[commit.hash] = []
            #Reset data
            self.commits_containing_file = {}
            self.smallest_commit_list = None

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if is_commit_of_interest or not calc_only_commits_of_interest:
            commit_file_data = self.files_in_commit.get_data()
            #Loop until start or last_coi is met, starting from most recent
            self.commits_containing_file[file.new_path] = Data_Calculator_Util.commits_containing_file(commit_file_data, file.new_path, self.previous_coi_commit, True)
            #Check if we are smallest commit list, AKA the largest possible values list
            if not self.smallest_commit_list or len(self.commits_containing_file[self.smallest_commit_list]) > len(self.commits_containing_file[file.new_path]):
                self.smallest_commit_list = file.new_path
            #Pre append the file to the list
            self.act_devs_waypoint[commit.hash].append({"file":file.new_path, "metric":0})

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.previous_coi_commit = commit.hash
            metric_value = 0
            if self.smallest_commit_list:
                author_data = self.commit_author_data.get_data()
                considered_commits_list = Data_Calculator_Util.files_present_in_commits(self.smallest_commit_list, self.commits_containing_file)
                metric_value = len(list(set([author_data[hash] for hash in considered_commits_list])))
            #Assign the metric value to the files
            for file in self.act_devs_waypoint[commit.hash]:
                file["metric"] = metric_value

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.act_devs_waypoint.get(commit_hash, None)