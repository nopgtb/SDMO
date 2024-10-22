#Excepts a packaged version of https://github.com/mauricioaniche/ck
#to be placed in same folder with this script named "ck.jar"
import os
import csv
import json
import subprocess
from pathlib import Path

tool_id = "ck"
#We expect the tool to be at this path
tool_relative_path = "ck.jar"
#Console arguments for the tool
tool_args = [
    "false", #USE_JARS
    "0", #Max files per partition
    "false", #Variable and field metrics
]

#Writes json to file
def write_json(path, data):
    with open(path, "a+") as file:
        json.dump(data, file)

#gets the parent folder for the script
def get_parent_folder():
    return str(Path(os.path.abspath(__file__)).parent)

#turns relative path to absolute path relative to the .py file location
def relative_to_absolute(path):
    return get_parent_folder() + "\\" + path

#Checks if the external tool is present at the expected path
def ck_tool_is_present():
    tool_path = Path(relative_to_absolute(tool_relative_path))
    return tool_path.is_file()

#Returns tool id
def ck_get_tool_id():
    return tool_id

#Returns the absolute path we expect to find our output at
def ck_get_tool_output_path():
    return relative_to_absolute(tool_id + "_output.json")

#Start the external tool on the given path
def ck_analyze_commit_files(path):
    args = ["java", "-jar", relative_to_absolute(tool_relative_path), path] + tool_args + [path + "\\"]
    return subprocess.Popen(
        args, 
        stdin = subprocess.DEVNULL, stdout = subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True
    )

#Read csv and pick only data assosiated with given keys of interest
def get_csv_data(path, delimiter, keys_of_interest):
    out_data = []
    try:
        csv_data = []
        #Read csv data
        with open(path, newline='') as csv_file:
            source_reader = csv.reader(csv_file, delimiter=delimiter)
            csv_data = [l for l in source_reader if l]
        #Map keys_of_interest to indexs in the csv by checking the header
        interest_map = {v:i for i,v in enumerate(csv_data[0]) if v in keys_of_interest}
        #Fetch data of interest using the map
        out_data = [{k:l[interest_map[k]] for k in keys_of_interest} for l in csv_data[1:]]
    except OSError as e:
        out_data = []
    return out_data

#Read the external tools output
def ck_collect_tool_data(path):
    return get_csv_data(
        path + "\\" + "class.csv", ",", 
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

#Outputs the given data to the tool output path
def ck_output_data(data):
    write_json(ck_get_tool_output_path(), data)
