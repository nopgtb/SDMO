#Static Interface for the external runner to interact with the external tools
class External_Tool_Interface:
    
    #Returns a identifier for the tool
    @staticmethod
    def get_tool_id():
        pass

    #Returns wheter the tool wants to go trough each commit or can patch collect
    @staticmethod
    def get_method():
        pass

    #Collect the output of the external tool
    @staticmethod
    def collect_tool_data(path):
        pass

    #Returns the tools execution path
    @staticmethod
    def get_tool_path():
        pass

    #Is the external tool present and usable?
    @staticmethod
    def tool_present():
        pass

    #Starts external proc for analysing the given path
    @staticmethod
    def start_tool_proc(path, file_paths = None):
        pass

    #Outputs the given data as output of the tool
    @staticmethod
    def output_tool_data(data):
        pass

    #Returns the path were the tools output will be output
    @staticmethod
    def get_output_path():
        pass
