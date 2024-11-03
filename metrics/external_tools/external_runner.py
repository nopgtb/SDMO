import os
import math
import time
import queue
import threading
from pathlib import Path
from pydriller import Repository

if __name__ == "__main__":
    #if run from service 
    from external_ck import CK
    from external_comread import COMREAD
    from external_c3_hslcom import C3_HSLCOM
    from external_tool_util import External_Tool_Util
else:
    from .external_ck import CK
    from .external_comread import COMREAD
    from .external_c3_hslcom import C3_HSLCOM
    from .external_tool_util import External_Tool_Util

#Tool mappings
external_tool_mappings = {
    CK.get_tool_id(): {
        "collect": CK.collect_tool_data,
        "analyze": CK.start_tool_proc,
        "present": CK.tool_present,
        "output": CK.output_tool_data,
        "output_path": CK.get_output_path,
        "collection_method": CK.get_method
    },
    C3_HSLCOM.get_tool_id(): {
        "collect": C3_HSLCOM.collect_tool_data,
        "analyze": C3_HSLCOM.start_tool_proc,
        "present": C3_HSLCOM.tool_present,
        "output": C3_HSLCOM.output_tool_data,
        "output_path": C3_HSLCOM.get_output_path,
        "collection_method": C3_HSLCOM.get_method,
    },
    COMREAD.get_tool_id(): {
        "collect": COMREAD.collect_tool_data,
        "analyze": COMREAD.start_tool_proc,
        "present": COMREAD.tool_present,
        "output": COMREAD.output_tool_data,
        "output_path": COMREAD.get_output_path,
        "collection_method": COMREAD.get_method,
    },
}

#Reads a json file to communicate with the external tool scripts
def read_external_instructions(path):
    structure = ["repository", "COI", "analyze_only_commits_of_interest", "branch", "max_workers", "service_needs"]
    data = External_Tool_Util.read_json(path)
    values = {}
    valid_instructions = True
    for k in structure:
        if k in data.keys():
            values[k] = data[k]
        else:
            valid_instructions = False
    return values, valid_instructions

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
    return External_Tool_Util.relative_to_absolute("external_instructions.json", __file__)

#Returns tools temp folder
def get_tool_temp_folder():
    return External_Tool_Util.relative_to_absolute("external_service_temp", __file__)

#Writes the commit files onto hdd
def write_commit_files(path, commit):
    External_Tool_Util.create_folder(path)
    #avoid conflicts by prefixing file names
    written_paths = []
    file_num = 0
    for file in commit["files"]:
        #If we have a path and source_code
        if file and commit["files"][file] and ".java" in file:
            file_temp_path = path + "\\" + str(file_num) + "_" + file
            #Write the source_code to the path
            with open(file_temp_path, "w+", encoding="utf-8") as fw:
                fw.write(commit["files"][file])
            written_paths.append(file_temp_path.strip())
        file_num = file_num + 1
    return written_paths

#Pick a job from the queue and run it
def worker():
    while True:
        patch = tool_queue.get()
        if patch == None:
            break
        patch_path = get_tool_temp_folder() + "\\patch_" + patch[0]["hash"]
        patch_file_paths = []
        #Write files for analysis by the tool
        for commit in patch:
            commit_temp_folder = patch_path + "\\" + commit["hash"]
            patch_file_paths.extend(write_commit_files(commit_temp_folder, commit))
        #Start patch jobs
        patch_jobs = {tool:None for tool in external_tool_mappings.keys() if external_tool_mappings[tool]["collection_method"]() == "patch"}
        for tool in patch_jobs:
            patch_jobs[tool] = external_tool_mappings[tool]["analyze"](patch_path, patch_file_paths)
        #Manage the commit level jobs
        commit_jobs = {tool:{"proc":None, "job_index":-1, "target_folder":"", "job_read":False} for tool in external_tool_mappings.keys() if external_tool_mappings[tool]["collection_method"]() == "commit"}
        commit_jobs_left = True
        while commit_jobs_left:
            commit_jobs_left = False
            #Check if we need to read output or start job
            for tool in commit_jobs.keys():
                #We have a job and its not running
                if commit_jobs[tool]["proc"] and not commit_jobs[tool]["proc"].poll() == None and not commit_jobs[tool]["job_read"]:
                    tool_data_per_commit[tool][patch[commit_jobs[tool]["job_index"]]["hash"]] = external_tool_mappings[tool]["collect"](commit_jobs[tool]["target_folder"])
                    commit_jobs[tool]["job_read"] = True
                #Check if we need to start new jobs
                if not commit_jobs[tool]["proc"] or not commit_jobs[tool]["proc"].poll() == None:
                    next_job_index = commit_jobs[tool]["job_index"] + 1
                    if next_job_index < len(patch):
                        commit_jobs[tool]["job_index"] = next_job_index
                        commit_jobs[tool]["target_folder"] = patch_path + "\\" + patch[next_job_index]["hash"]
                        commit_jobs[tool]["proc"] = external_tool_mappings[tool]["analyze"](patch_path + "\\" + patch[next_job_index]["hash"], patch_file_paths)
                        commit_jobs[tool]["job_read"] = False
                        commit_jobs_left = True
                else:
                    commit_jobs_left = True
            #Sleep
            if commit_jobs_left:
                time.sleep(1)
        #collect patch job output
        for tool in patch_jobs:
            patch_jobs[tool].wait()
            tool_data_per_commit[tool].update(external_tool_mappings[tool]["collect"](patch_path))
        tool_queue.task_done()

#Run if we have a tool to run
if __name__ == "__main__":
    #Load the instructions
    tool_instructions, valid_instructions = read_external_instructions(get_tool_instruction_path())
    if valid_instructions and tool_is_present(tool_instructions["service_needs"]):
        #Tool job queue
        tool_queue = queue.Queue()
        tool_data_per_commit = {service:{} for service in tool_instructions["service_needs"]}
        worker_threads = []
        patch_size = 500
        #Start worker threads
        for i in range(tool_instructions["max_workers"]):
            worker_threads.append(threading.Thread(target=worker, daemon=True).start())
        current_patch = []
        #Run trough all the commits of the git and push them to the worker threads
        for commit in Repository(tool_instructions["repository"], only_in_branch=tool_instructions["branch"]).traverse_commits():
            #Git can be weird
            try:
                #If we are a commit of interest or analyse all commits
                if (tool_instructions["analyze_only_commits_of_interest"] and commit.hash in tool_instructions["COI"]) or not tool_instructions["analyze_only_commits_of_interest"]:
                    current_patch.append({"hash":commit.hash,"files":{f.filename:f.source_code for f in commit.modified_files}})

                    if len(current_patch) >= patch_size:
                        tool_queue.put(current_patch)
                        current_patch = []
            except:
                continue
        tool_queue.join()
        
        for _ in range(len(worker_threads)):
            tool_queue.put(None)
    
        #Write results to output
        for service in tool_instructions["service_needs"]:
            external_tool_mappings[service]["output"](tool_data_per_commit[service])

        for thread in tool_queue:
            thread.join()
