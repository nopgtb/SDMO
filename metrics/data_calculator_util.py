import re
import os
import json
import stat
import shutil
import subprocess
from pathlib import Path

#Calculates metric values for the given files from the given data
def helper_make_waypoint_per_file_neigbours(data, files, waypoint_metric_func):
    metric_data = []
    #Dont modify the source
    neighbours = list(files)
    excluded_file_index = len(neighbours) - 1
    #run trough files calculating metric
    while excluded_file_index >= 0:
        #Pick out the targeted file
        excluded_file = neighbours.pop(excluded_file_index)
        #Calculate metric using the remaining files
        metric_value = 0
        for neighbour_file in neighbours:
            metric_value = metric_value + waypoint_metric_func(data[neighbour_file])
        #Remember the value for the excluded file
        metric_data.append({"file": excluded_file, "metric": metric_value})
        #Move to the next file and push the previous back on the neighbours
        excluded_file_index = excluded_file_index - 1
        neighbours.append(excluded_file)
    return metric_data

#Extract potential java package name from source code
def helper_extract_java_package_name(source_code):
    #if we have source code
    if source_code:
        #Is the package keyword present in the source code. Extract the name
        packages_modified = re.findall(r'package\s+([\w\.]+);', source_code)
        if packages_modified:
            #https://docs.oracle.com/javase/tutorial/java/package/createpkgs.html
            #file can have only one package declaration
            return packages_modified[0]
        #If you do not use a package statement, your type ends up in an unnamed package
        #if you want to consider it a unique package uncomment the line below
        #return "unnamed"
    #No package possible, we do not have source code
    return ""

#Extracts all modified packages from the commit source file
def helper_extract_modified_packages(file):
    potential_packages = []
    #We are a java file
    if file.filename[len(file.filename)-5:] == ".java":
        #Get current and past source code
        file_source_codes = [file.source_code_before, file.source_code]
        #Run trough the source files
        for file_source_code in file_source_codes:
            package = helper_extract_java_package_name(file_source_code)
            if package:
                potential_packages.append(package)
        #return unique package names
    return list(set(potential_packages))

#Gets author of the commit
def helper_commit_author(pr_commit):
    return pr_commit.author.email.strip()

#Gets paths of modified files in list form
def helper_list_commit_files(pr_commit):
    return [f.new_path for f in pr_commit.modified_files if f.new_path]

#Output to console
def helper_print(*args):
    print(*args)

#turns relative path to absolute path relative to the .py file location
def relative_to_absolute(path, file_path):
    return str(Path(file_path).parent) + "\\" + path

#read a json file
def helper_read_json(path):
    data = {}
    with open(path, "r") as file:
        data = json.load(file)
    return data

#Writes json to file
def helper_write_json(path, data):
    with open(path, "w+") as file:
        json.dump(data, file)

#Writes a json file to communicate with the external tool scripts
def helper_write_external_instructions(path, respository, branch, commits_of_interest, analyze_only_commits_of_interest, tool_max_workers, service_needs):
    helper_write_json(path, {
            "repository": respository,
            "branch": branch,
            "COI": commits_of_interest,
            "analyze_only_commits_of_interest": analyze_only_commits_of_interest,
            "max_workers": tool_max_workers,
            "service_needs": service_needs
        }
    )

#Starts the external tool script for the given tool
def helper_start_external_tool_process(path):
    tool_path = Path(path)
    if tool_path.is_file():
        return subprocess.Popen(
            ["python", os.path.abspath(path)], 
            stdin = subprocess.DEVNULL, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL, shell=True #No external input
        )
    return None

#Copies git from source to target
def helper_copy_git(source, target):
    os.makedirs(target, exist_ok=True)
    new_path = target+"\\"+os.path.basename(source)
    shutil.copytree(source, new_path)
    return new_path

#Returns if folder exists
def helper_path_exists(path):
    return os.path.exists(path)

#Removes folder at given path
def helper_remove_folder(path):
    if helper_path_exists(path):
        #Based on https://stackoverflow.com/questions/2656322/shutil-rmtree-fails-on-windows-with-access-is-denied#answer-2656408
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                filename = os.path.join(root, name)
                os.chmod(filename, stat.S_IWUSR)
                os.remove(filename)
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(path)

#Deletes file
def helper_remove_file(path):
    if helper_path_exists(path):
        os.remove(path)