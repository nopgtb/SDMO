from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import Data_Calculator_Util
from metrics.data_provider.data_provider_files_in_commit import Data_Provider_Files_In_Commit

#NCOMM
#The cumulative number of commits made to a file up to the considered commit starting from the previous refactoring commit, in
#which the same set of files were changed along with the given file. (For the first refactoring commit, consider as previous commit
#the one in which the file was introduced)
class Metric_NCOMM(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        self.data_provider = Data_Provider_Files_In_Commit()
        #Hash => {file:metric}
        self.commits_per_file_grouping_waypoints = {}
        #Keep track of the last COI
        self.previous_coi_commit = None
        #Keep track of the smallest possible list of commits containing commits set
        self.smallest_commit_list = None
        #file => [commit_hash containing our file]
        self.commits_containing_file = {}

    #Data providers for the metric
    def get_data_providers(self):
        return [self.data_provider]

    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "NCOMM"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "file"

    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #We are calculating this commit
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.commits_per_file_grouping_waypoints[commit.hash] = []
            self.commits_containing_file = {}
            self.smallest_commit_list = None

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        commit_file_data = self.data_provider.get_data()
        #We are calculating this file and we have data
        if is_commit_of_interest or not calc_only_commits_of_interest and commit_file_data:
            #Get list of commits containing this file since last COI or files creation
            self.commits_containing_file[file.new_path] = Data_Calculator_Util.commits_containing_file(commit_file_data, file.new_path, self.previous_coi_commit, True)
            #Check if we are smallest commit list
            if not self.smallest_commit_list or len(self.commits_containing_file[self.smallest_commit_list]) > len(self.commits_containing_file[file.new_path]):
                self.smallest_commit_list = file.new_path
            #Pre append the file to the list
            self.commits_per_file_grouping_waypoints[commit.hash].append({"file":file.new_path, "metric":0})

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #We are calculating this commit
        if is_commit_of_interest or not calc_only_commits_of_interest:
            #Keep track of the last COI
            self.previous_coi_commit = commit.hash
            metric_value = 0
            if self.smallest_commit_list:
                #Number of commits containing commits set of files
                metric_value = len(Data_Calculator_Util.files_present_in_commits(self.smallest_commit_list, self.commits_containing_file))
            #Assign the metric value to the files
            for file in self.commits_per_file_grouping_waypoints[commit.hash]:
                file["metric"] = metric_value

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.commits_per_file_grouping_waypoints.get(commit_hash, None)