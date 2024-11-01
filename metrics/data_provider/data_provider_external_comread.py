from .data_provider_interface import Data_Provider_Interface
from metrics.data_calculator_util import Data_Calculator_Util
from .external_service_provider import External_Service_Provider
from metrics.external_tools.external_comread import COMREAD

#Metrics rely on common data. Instead of each metric calculating it on its own
#data provider will provide it from single source making it available for all metrics
class Data_Provider_External_COMREAD(Data_Provider_Interface):

    #Start a external proc for the data
    def pre_calc_run_external(self, repository, branch, commits_of_interest, analyze_only_commits_of_interest):
        if COMREAD.tool_present():
            #Signal for the external runner to run our tool on the files
            self.es_provider.signal_service_need(self.external_tool_id)
        else:
            Data_Calculator_Util.output_to_console("Warning: Could not detect external tool ", self.external_tool_id, ". Metrics reliant on the tool will not be collected")
            Data_Calculator_Util.output_to_console("Expects comread.jar to be found at external_tools/comread.jar. Check readme for guidance")

    #Try to read the result json file
    def read_results(self):
        #Read the external output
        self.comread_data = Data_Calculator_Util.read_json(COMREAD.get_output_path())

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
        self.external_tool_id = COMREAD.get_tool_id()
        #commit => {class, ... metric_values}
        self.comread_data = {}

    #Returns the data of the data provider
    def get_data(self):
        return self.comread_data