#Excepts a packaged version of https://github.com/mauricioaniche/ck
#to be placed in same folder with this script named "ck.jar"
import subprocess
from pathlib import Path

if __name__ == "external_ck":
    #if run from service 
    from external_tool_interface import External_Tool_Interface
    from external_tool_util import External_Tool_Util
else:
    from .external_tool_interface import External_Tool_Interface
    from .external_tool_util import External_Tool_Util

class CK(External_Tool_Interface):

    #Returns a identifier for the tool
    @staticmethod
    def get_tool_id():
        return "ck"

    #Collect the output of the external tool
    @staticmethod
    def collect_tool_data(path):
        file_path = path + "\\" + "class.csv"
        if External_Tool_Util.path_exists(file_path):
            return External_Tool_Util.read_csv(
                file_path, ",", 
                [
                    #Header keys in class.csv
                    "class", #Name of the class
                    "cbo", #Coupling between object classes
                    "wmc", #Weighted methods per class
                    "rfc", #Response for a class
                    "loc", #Effective lines of code
                    "totalMethodsQty", #Number of methods in class
                    "publicMethodsQty", #Number of public methods in class
                    "dit", #Depth of inheritance tree
                    "noc", #Number of children
                    "totalFieldsQty", #Number of fields in class
                    "staticFieldsQty", #Number of static fields in class
                    "publicFieldsQty", #Number of public fields in class
                    "staticMethodsQty", #Number of static methods in class
                    "nosi" #Number of static invocations in class
                ]
            )
        return []

    #Returns the tools execution path
    @staticmethod
    def get_tool_path():
        return External_Tool_Util.relative_to_absolute("ck.jar", __file__)

    #Is the external tool present and usable?
    @staticmethod
    def tool_present():
        return Path(External_Tool_Util.relative_to_absolute(CK.get_tool_path(), __file__)).is_file

    #Starts external proc for analysing the given path
    @staticmethod
    def start_tool_proc(path):
        #Arguments for starting java with tool path and pointing it to the given path
        args = ["java", "-jar", CK.get_tool_path(), path] 
        #Additional Tool flags
        args = args + [
            "false", #USE_JARS
            "0", #Max files per partition
            "false", #Variable and field metrics
            path + "\\" #Output path for the tool output
        ]
        return subprocess.Popen(
            args, 
            stdin = subprocess.DEVNULL, stdout = subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True
        )

    #Outputs the given data as output of the tool
    @staticmethod
    def output_tool_data(data):
        External_Tool_Util.write_json(CK.get_output_path(), data)

    #Returns the path were the tools output will be output
    @staticmethod
    def get_output_path():
        return External_Tool_Util.relative_to_absolute("ck_output.json", __file__)