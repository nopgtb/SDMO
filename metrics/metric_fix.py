import re
from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *

#FIX
#Whether or not the change is a defect fix.
class Metric_FIX(Metric_Interface):

    #Store the repo
    def __init__(self):
        super().__init__()
        #commit => bool
        self.jira_tasked_waypoint = {}

    #Data providers for the metric
    def get_data_providers(self):
        return []

    #Returns name of the metric as str
    @staticmethod
    def get_metric_name():
        return "FIX"
    
    #Returns at what level was the metric collected at
    @staticmethod
    def get_collection_level():
        return "commit"

    #Called once per file in a commit
    def pre_calc_per_file(self, file, commit, is_commit_of_interest, calc_only_commits_of_interest):
        #We are calculating this file
        if is_commit_of_interest or not calc_only_commits_of_interest:
            self.jira_tasked_waypoint[commit.hash] = False
            if commit.msg:
                #Extract jira ticket in form of CAPITALLETTERPROJECTID-123123
                packages_modified = re.findall(r'\b([A-Z][A-Z0-9]+-\d+)\b', commit.msg)
                if packages_modified:
                    self.jira_tasked_waypoint[commit.hash] = True

    #Called to fetch the metric value for current commit
    def get_metric(self, commit_hash):
        return self.jira_tasked_waypoint.get(commit_hash, None)