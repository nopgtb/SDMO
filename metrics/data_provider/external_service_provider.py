from .data_provider_interface import Data_Provider_Interface
from metrics.data_calculator_util import Data_Calculator_Util
from metrics.external_tools.external_runner import tool_is_present, get_tool_instruction_path, get_file_path, get_tool_temp_folder, get_output_paths

#Metrics rely on common data. Instead of each metric calculating it on its own
#data provider will provide it from single source making it available for all metrics
class External_Service_Provider(Data_Provider_Interface):

    #Signal the need for a external service to be run
    def signal_service_need(self, tool_id):
        self.service_needs.append(tool_id)

    #Start a external proc for the data
    def pre_calc_run_external(self, repository, branch, commits_of_interest, analyze_only_commits_of_interest):
        if self.service_needs and tool_is_present(self.service_needs):
            #Make own copy of the git to avoid wasting time on lockouts
            new_repository = Data_Calculator_Util.copy_git(repository, get_tool_temp_folder())
            #write data for the external tool to process and start it up
            Data_Calculator_Util.write_external_instructions(get_tool_instruction_path(), new_repository, branch, commits_of_interest, analyze_only_commits_of_interest, self.tool_max_workers, self.service_needs)
            self.tool_proc = Data_Calculator_Util.start_python_process(get_file_path())
        else:
            Data_Calculator_Util.output_to_console("Warning: Some of the external tools needed were not found, cant start external service")

    #Wait for the external proc to finish
    #and make its data available to metrics
    def pre_calc_wait_for_external(self):
        #If proc was created wait for it
        if self.tool_proc:
            self.tool_proc.wait()

    #Initialize and Reset the data
    def reset_data(self):
        self.tool_max_workers = 2
        self.service_needs = []
        Data_Calculator_Util.remove_folder(get_tool_temp_folder())
        Data_Calculator_Util.remove_file(get_tool_instruction_path())
        for path in get_output_paths():
            Data_Calculator_Util.remove_file(path)
    
    #Returns the data of the data provider
    def get_data(self):
        raise Exception("Not supported")