import subprocess
from pathlib import Path

if __name__ == "external_c3_hslcom":
    #if run from service 
    from external_tool_interface import External_Tool_Interface
    from external_tool_util import External_Tool_Util
else:
    from .external_tool_interface import External_Tool_Interface
    from .external_tool_util import External_Tool_Util

class C3_HSLCOM(External_Tool_Interface):

    #Returns a identifier for the tool
    @staticmethod
    def get_tool_id():
        return "c3_hslcom"
    
    #Returns wheter the tool wants to go trough each commit or can patch collect
    @staticmethod
    def get_method():
        return "patch"

    #Collect the output of the external tool
    @staticmethod
    def collect_tool_data(path):
        file_path = path + "\\c3_hslcom_class.json"
        if External_Tool_Util.path_exists(file_path):
            #[{"file"..}]
            tool_json = External_Tool_Util.read_json(file_path)
            output = {}
            for file in tool_json:
                file_path = Path(file["file"])
                commit_hash = file_path.parent.name
                output.setdefault(commit_hash, []).append({"class":file["class"], "metric_c3": file["metric_c3"], "metric_hslcom":file["metric_hslcom"]})
            return output
        return []

    #Returns the tools execution path
    @staticmethod
    def get_tool_path():
        return External_Tool_Util.relative_to_absolute("c3_hslcom.py", __file__)

    #Is the external tool present and usable?
    @staticmethod
    def tool_present():
        return Path(External_Tool_Util.relative_to_absolute(C3_HSLCOM.get_tool_path(), __file__)).is_file

    #Starts external proc for analysing the given path
    @staticmethod
    def start_tool_proc(path, file_paths = None):
        #Arguments for starting python with tool
        args = ["python", C3_HSLCOM.get_tool_path(), path] 
        return subprocess.Popen(
            args, 
            stdin = subprocess.DEVNULL, stdout = subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True
        )

    #Outputs the given data as output of the tool
    @staticmethod
    def output_tool_data(data):
        External_Tool_Util.write_json(C3_HSLCOM.get_output_path(), data)

    #Returns the path were the tools output will be output
    @staticmethod
    def get_output_path():
        return External_Tool_Util.relative_to_absolute("c3_hslcom_output.json", __file__)