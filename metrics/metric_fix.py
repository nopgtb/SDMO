import re
from metrics.metric_interface import Metric_Interface
from metrics.data_calculator_util import *

#FIX
#Whether or not the change is a defect fix.
class Metric_FIX(Metric_Interface):

    #Store the repo
    def __init__(self, repository):
        super().__init__(repository)
        #commit => bool
        self.jira_tasked = {}

    #Data providers for the metric
    def get_data_providers(self):
        return []

    #Called once per file in a commit
    def pre_calc_per_file(self, file, pr_commit, is_rfm_commit, rfm_commit):
        self.jira_tasked[pr_commit.hash] = False
        if pr_commit.msg:
            #Extract jira ticket in form of CAPITALLETTERPROJECTID-123123
            packages_modified = re.findall(r'\b([A-Z][A-Z0-9]+-\d+)\b', pr_commit.msg)
            if packages_modified:
                self.jira_tasked[pr_commit.hash] = True

    #Called to fetch the metric value for current commit
    def get_metric(self, prev_rfm_commit, cur_rfm_commit, pr_commit):
        return self.jira_tasked.get(pr_commit.hash, False)