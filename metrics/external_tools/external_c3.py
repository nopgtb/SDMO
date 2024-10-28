import subprocess
from pathlib import Path

if __name__ == "external_c3":
    #if run from service 
    from external_tool_interface import External_Tool_Interface
    from external_tool_util import External_Tool_Util
else:
    from .external_tool_interface import External_Tool_Interface
    from .external_tool_util import External_Tool_Util

class C3(External_Tool_Interface):

    #Returns a identifier for the tool
    @staticmethod
    def get_tool_id():
        return "c3"

    #Collect the output of the external tool
    @staticmethod
    def collect_tool_data(path):
        file_path = path + "\\c3_class.json"
        if External_Tool_Util.path_exists(file_path):
            return External_Tool_Util.read_json(file_path)
        return []

    #Returns the tools execution path
    @staticmethod
    def get_tool_path():
        return External_Tool_Util.relative_to_absolute("c3.py", __file__)

    #Is the external tool present and usable?
    @staticmethod
    def tool_present():
        return Path(External_Tool_Util.relative_to_absolute(C3.get_tool_path(), __file__)).is_file

    #Starts external proc for analysing the given path
    @staticmethod
    def start_tool_proc(path):
        #Arguments for starting python with tool
        args = ["python", C3.get_tool_path(), path] 
        return subprocess.Popen(
            args, 
            stdin = subprocess.DEVNULL, stdout = subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True
        )

    #Outputs the given data as output of the tool
    @staticmethod
    def output_tool_data(data):
        External_Tool_Util.write_json(C3.get_output_path(), data)

    #Returns the path were the tools output will be output
    @staticmethod
    def get_output_path():
        return External_Tool_Util.relative_to_absolute("c3_output.json", __file__)