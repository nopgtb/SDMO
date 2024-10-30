from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import Data_Calculator_Util
from metrics.data_provider.data_provider_author_per_commit import Data_Provider_Author_Per_Commit
from metrics.data_provider.data_provider_files_in_commit import Data_Provider_Files_In_Commit

#NDDEV
#The number of distinct developers who, given the considered commit, changed the same specific files up to the considered commit
#starting from the point in which the file was introduced
class Metric_NDDEV(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        self.commit_author_data = Data_Provider_Author_Per_Commit()
        self.files_in_commit = Data_Provider_Files_In_Commit()
        #Hash => {file:metric}
        self.file_set_unique_devs_waypoint = {}
        #file => [commit_hash containing our file]
        self.commits_containing_file = {}
        #Keep track of the smallest possible list of commits containing commits set
        self.smallest_commit_list = None

    #Data providers for the metric
    def get_data_providers(self):
        return [self.commit_author_data, self.files_in_commit]
    
    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "NDDEV"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "file"
    
    #Called once per commit, excludes current commit data (pre pre_calc_per_file call)
    def pre_calc_per_commit_exlusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #We are calculating this file
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.file_set_unique_devs_waypoint[commit.hash] = []
            self.commits_containing_file = {}
            self.smallest_commit_list = None

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        commit_file_data = self.files_in_commit.get_data()
        #We are calculating this file and we have data
        if is_commit_of_interest or not calc_only_commits_of_interest and commit_file_data:
            #Get list of commits containing this file since files creation
            self.commits_containing_file[file.new_path] = Data_Calculator_Util.commits_containing_file(commit_file_data, file.new_path, None, True)
            #Check if we are smallest commit list
            if not self.smallest_commit_list or len(self.commits_containing_file[self.smallest_commit_list]) > len(self.commits_containing_file[file.new_path]):
                self.smallest_commit_list = file.new_path
            #Pre append the file to the list
            self.file_set_unique_devs_waypoint[commit.hash].append({"file":file.new_path, "metric":0})

    #Called once per commit, includes current commit data (post pre_calc_per_file call)
    def pre_calc_per_commit_inclusive(self, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #We are calculating this file
        if is_commit_of_interest or not calc_only_commits_of_interest:
            metric_value = 0
            author_data = self.commit_author_data.get_data()
            #We have data
            if self.smallest_commit_list and author_data:
                #Check the smallest commit list and pick all commits where all the commits files are present
                considered_commits_list = Data_Calculator_Util.files_present_in_commits(self.smallest_commit_list, self.commits_containing_file)
                #Number of unique developers who changed our file set since file creation
                metric_value = len(list(set([author_data[hash] for hash in considered_commits_list])))
            for file in self.file_set_unique_devs_waypoint[commit.hash]:
                file["metric"] = metric_value

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.file_set_unique_devs_waypoint.get(commit_hash, None)