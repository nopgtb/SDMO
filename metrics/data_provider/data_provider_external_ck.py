from .data_provider_interface import Data_Provider_Interface
from metrics.data_calculator_util import *
from .external_service_provider import External_Service_Provider
from metrics.external_tools.ck import ck_tool_is_present, ck_get_tool_output_path

#Metrics rely on common data. Instead of each metric calculating it on its own
#data provider will provide it from single source making it available for all metrics
class Data_Provider_External_CK(Data_Provider_Interface):

    #Start a external proc for the data
    def pre_calc_run_external(self, repository, branch, commits_of_interest, analyze_only_commits_of_interest):
        if ck_tool_is_present():
            #Signal for the external runner to run our tool on the files
            self.es_provider.signal_service_need(self.external_tool_id)
            #Make own copy of the git to avoid wasting time on lockouts
            #new_repository = helper_copy_git(repository, get_tool_temp_folder())
            #write data for the external tool to process and start it up
            #helper_write_external_instructions(get_tool_instruction_path(), new_repository, branch, commits_of_interest, analyze_only_commits_of_interest, self.tool_max_workers)
            #self.tool_proc = helper_start_external_tool_process(get_file_path())
        else:
            helper_print("Warning: Could not detect external tool ", self.external_tool_id, ". Metrics reliant on the tool will not be collected")
            helper_print("Expects packaged version of https://github.com/mauricioaniche/ck to be found in path external_tools/ck.jar")

    #Try to read the result json file
    def read_results(self):
        #Read the external output
        self.ck_data = helper_read_json(ck_get_tool_output_path())

    #Wait for the external proc to finish
    #and make its data available to metrics
    def pre_calc_wait_for_external(self):
        #Wait for the external service provider
        self.es_provider.pre_calc_wait_for_external()
        #Try to read the external tool results
        self.read_results()

    #Initialize and Reset the data
    def reset_data(self):
        self.es_provider = External_Service_Provider()
        self.external_tool_id = "ck"
        #commit => {class, ... metric_values}
        self.ck_data = {}

    #Returns the data of the data provider
    def get_data(self):
        return self.ck_data