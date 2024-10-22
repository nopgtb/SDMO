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


if __name__ == "__main__":
    #if run from service 
    from ck import ck_collect_tool_data, ck_analyze_commit_files, ck_tool_is_present, ck_get_tool_id, ck_output_data, ck_get_tool_output_path
else:
    from .ck import ck_collect_tool_data, ck_analyze_commit_files, ck_tool_is_present, ck_get_tool_id, ck_output_data, ck_get_tool_output_path

#Tool mappings
external_tool_mappings = {
    ck_get_tool_id(): {
        "collect": ck_collect_tool_data,
        "analyze": ck_analyze_commit_files,
        "present": ck_tool_is_present,
        "output": ck_output_data,
        "output_path": ck_get_tool_output_path
    }
}

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
    structure = ["repository", "COI", "analyze_only_commits_of_interest", "branch", "max_workers", "service_needs"]
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

#Returns the absolute path of this file
def get_file_path():
    return str(Path(os.path.abspath(__file__)))

#Checks if the external tool is present at the expected path
def tool_is_present(service_need):
    all_present = True
    for service in service_need:
        if not external_tool_mappings[service]["present"]():
            all_present = False
    return all_present

#Returns external tool output paths
def get_output_paths():
    output_paths = []
    for tool in external_tool_mappings:
        output_paths.append(external_tool_mappings[tool]["output_path"]())
    return output_paths

#Returns the absolute path we expect to find our instructions at
def get_tool_instruction_path():
    return relative_to_absolute("external_instructions.json")

#Returns tools temp folder
def get_tool_temp_folder():
    return relative_to_absolute(external_temp_folder)

#Returns if folder exists
def folder_exists(path):
    return os.path.exists(path)

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

#Pick a job from the queue and run it
def worker():
    while True:
        commit = tool_queue.get()
        #Write files for analysis by the tool
        commit_temp_folder = relative_to_absolute(external_temp_folder + "\\" + commit["hash"])
        write_commit_files(commit_temp_folder, commit)
        #Analyze files using the external tools and wait for them to finish
        service_procs = {}
        for service in tool_instructions["service_needs"]:
            service_procs[service] = external_tool_mappings[service]["analyze"](commit_temp_folder)
        for service in tool_instructions["service_needs"]:
            service_procs[service].wait()
        #Collect data
        for service in tool_instructions["service_needs"]:
            tool_data_per_commit[service][commit["hash"]] = external_tool_mappings[service]["collect"](commit_temp_folder)
        #move to next job
        tool_queue.task_done()

external_temp_folder = "external_service_temp"

#Run if we have a tool to run
if __name__ == "__main__":
    #Load the instructions
    tool_instructions, valid_instructions = read_external_instructions(get_tool_instruction_path())
    if valid_instructions and tool_is_present(tool_instructions["service_needs"]):
        #Tool job queue
        tool_queue = queue.Queue()
        tool_data_per_commit = {service:{} for service in tool_instructions["service_needs"]}
        #Start worker threads
        for i in range(tool_instructions["max_workers"]):
            threading.Thread(target=worker, daemon=True).start()
        #Run trough all the commits of the git and push them to the worker threads
        for commit in Repository(tool_instructions["repository"], only_in_branch=tool_instructions["branch"]).traverse_commits():
            #Git can be weird
            try:
                #If we are a commit of interest or analyse all commits
                if (tool_instructions["analyze_only_commits_of_interest"] and commit.hash in tool_instructions["COI"]) or not tool_instructions["analyze_only_commits_of_interest"]:
                    tool_queue.put({"hash":commit.hash,"files":{f.filename:f.source_code for f in commit.modified_files}})
            except:
                continue
        tool_queue.join()
        #Write results to output
        for service in tool_instructions["service_needs"]:
            external_tool_mappings[service]["output"](tool_data_per_commit[service])
