import re
import os
import subprocess
from pathlib import Path

if __name__ == "external_comread":
    #if run from service 
    from external_tool_interface import External_Tool_Interface
    from external_tool_util import External_Tool_Util
else:
    from .external_tool_interface import External_Tool_Interface
    from .external_tool_util import External_Tool_Util

class COMREAD(External_Tool_Interface):

    #Returns a identifier for the tool
    @staticmethod
    def get_tool_id():
        return "comread"

    #Returns wheter the tool wants to go trough each commit or can patch collect
    @staticmethod
    def get_method():
        return "patch"

    #Parses comread output file
    @staticmethod
    def parse_comread_output(txt):
        #Split lines and ignore header
        lines = txt.splitlines()[1:]
        output = {}
        for line in lines:
            #Tool outputs a \t between the file and metric
            parts = line.split("\t")
            if parts and len(parts) == 2 and not parts[1] == "NaN":
                try:
                    file_path = Path(parts[0])
                    commit_hash = file_path.parent.name
                    #Try to interp the metric as float
                    output.setdefault(commit_hash, []).append({"class":file_path.name, "metric":float(parts[1])})
                except:
                    pass
        return output

    #Collect the output of the external tool
    @staticmethod
    def collect_tool_data(path):
        file_path = path + "\\comread.txt"
        if External_Tool_Util.path_exists(file_path):
            #{File => Metric}
            return COMREAD.parse_comread_output(Path(file_path).read_text())
        return []

    #Returns the tools execution path
    @staticmethod
    def get_tool_path():
        return External_Tool_Util.relative_to_absolute("comread.jar", __file__)
    
    #Returns readability.classifier path
    @staticmethod
    def get_classifier_path():
        return External_Tool_Util.relative_to_absolute("readability.classifier", __file__)

    #Is the external tool present and usable?
    @staticmethod
    def tool_present():
        return Path(External_Tool_Util.relative_to_absolute(COMREAD.get_tool_path(), __file__)).is_file and Path(External_Tool_Util.relative_to_absolute(COMREAD.get_classifier_path(), __file__)).is_file

    #Starts external proc for analysing the given path
    @staticmethod
    def start_tool_proc(path, file_paths = None):
        #Arguments for starting python with tool
        if file_paths:
            External_Tool_Util.write_array(path+"\\comread_input.txt" ,file_paths)
            args = [
                    "java",
                    "-jar",
                    COMREAD.get_tool_path(),
                    #(path + "/*.java"),
                    "--outputFile="+ path+"\\comread.txt",
                    "--inputFile=" + path+"\\comread_input.txt",
                    "--classifier=" + COMREAD.get_classifier_path()
            ] 
            return subprocess.Popen(
                args, 
                stdin = subprocess.DEVNULL, stdout = subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True
            )
        return None

    #Outputs the given data as output of the tool
    @staticmethod
    def output_tool_data(data):
        External_Tool_Util.write_json(COMREAD.get_output_path(), data)

    #Returns the path were the tools output will be output
    @staticmethod
    def get_output_path():
        return External_Tool_Util.relative_to_absolute("comread_output.json", __file__)