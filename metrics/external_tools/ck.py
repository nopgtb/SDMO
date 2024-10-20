#Excepts a packaged version of https://github.com/mauricioaniche/ck
#to be placed in same folder with this script named "ck.jar"

import os
import csv
import json
import queue
import shutil
import threading
import subprocess
from pathlib import Path
from pydriller import Repository

#read a json file
def read_json(path):
    data = {}
    with open(path, "r") as file:
        data = json.load(file)
    return data

#Writes json to file
def write_json(path, data):
    with open(path, "a+") as file:
        json.dump(data, file)

#Reads a json file to communicate with the external tool scripts
def read_external_instructions(path):
    structure = ["repository", "COI", "analyze_only_commits_of_interest", "branch", "max_workers"]
    data = read_json(path)
    values = {}
    valid_instructions = True
    for k in structure:
        if k in data.keys():
            values[k] = data[k]
        else:
            valid_instructions = False
    return values, valid_instructions

#gets the parent folder for the script
def get_parent_folder():
    return str(Path(os.path.abspath(__file__)).parent)

#turns relative path to absolute path relative to the .py file location
def relative_to_absolute(path):
    return get_parent_folder() + "\\" + path

#Checks if the external tool is present at the expected path
def tool_is_present():
    tool_path = Path(relative_to_absolute(tool_relative_path))
    return tool_path.is_file()

#Returns the absolute path we expect to find our instructions at
def get_tool_instruction_path():
    return relative_to_absolute(tool_id + "_instructions.json")

#Returns the absolute path we expect to find our output at
def get_tool_output_path():
    return relative_to_absolute(tool_id + "_output.json")

#Returns tools temp folder
def get_tool_temp_folder():
    return relative_to_absolute(tool_folder)

#Returns the absolute path of this file
def get_file_path():
    return __file__

#Returns if folder exists
def folder_exists(path):
    return os.path.exists(path)

#Delete a folder and contained files
def delete_folder(path):
    if folder_exists(path):
        shutil.rmtree(path)

#Create a folder
def create_folder(path):
    if not folder_exists(path):
        os.makedirs(path, exist_ok=True)

#Writes the commit files onto hdd
def write_commit_files(path, commit):
    create_folder(path)
    #avoid conflicts by prefixing file names
    file_num = 0
    for file in commit["files"]:
        #If we have a path and source_code
        if file and commit["files"][file] and ".java" in file:
            file_temp_path = path + "\\" + str(file_num) + "_" + file
            #Write the source_code to the path
            with open(file_temp_path, "w+", encoding="utf-8") as fw:
                fw.write(commit["files"][file])
        file_num = file_num + 1

#Start the external tool on the given path
def analyse_commit_files(path):
    args = ["java", "-jar", relative_to_absolute(tool_relative_path), path] + tool_args + [path + "\\"]
    tool_proc = subprocess.Popen(
        args, 
        stdin = subprocess.DEVNULL, stdout = subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True
    )
    tool_proc.wait()

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
def collect_tool_data(path):
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

tool_id = "ck"
#We expect the tool to be at this path
tool_relative_path = "ck.jar"
tool_folder = "ck_temp"
#Console arguments for the tool
tool_args = [
    "false", #USE_JARS
    "0", #Max files per partition
    "false", #Variable and field metrics
]

#Pick a job from the queue and run it
def worker():
    while True:
        commit = tool_queue.get()
        #ck_temp\\sha1
        commit_temp_folder = tool_folder + "\\" + commit["hash"]
        #Write files for analysis by the tool
        write_commit_files(relative_to_absolute(commit_temp_folder), commit)
        #Analyse the commit files using the tool
        analyse_commit_files(relative_to_absolute(commit_temp_folder))
        tool_data_per_commit[commit["hash"]] = collect_tool_data(relative_to_absolute(commit_temp_folder))
        tool_queue.task_done()

#Run if we have a tool to run
if __name__ == "__main__" and tool_is_present():
    #Tool job queue
    tool_queue = queue.Queue()
    #Load the instructions
    tool_instructions, valid_instructions = read_external_instructions(get_tool_instruction_path())
    if valid_instructions:
        #Start worker threads
        for i in range(tool_instructions["max_workers"]):
            threading.Thread(target=worker, daemon=True).start()
        tool_data_per_commit = {}
        #Run trough all the commits of the git and push them to the worker threads
        for commit in Repository(tool_instructions["repository"], only_in_branch=tool_instructions["branch"]).traverse_commits():
            #If we are a commit of interest or analyse all commits
            if (tool_instructions["analyze_only_commits_of_interest"] and commit.hash in tool_instructions["COI"]) or not tool_instructions["analyze_only_commits_of_interest"]:
                tool_queue.put({"hash":commit.hash,"files":{f.filename:f.source_code for f in commit.modified_files}})
        tool_queue.join()
        #Write results to output
        write_json(get_tool_output_path(), tool_data_per_commit)
