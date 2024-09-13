#Download https://github.com/tsantalis/RefactoringMiner Zip
#Get Gradle and requirements https://gradle.org/install/
#cd into the extracted RefactoringMiner root 
#run gradlew distZip or ./gradlew distZip to build distro
#Assumed that build version of RefactorMiner is added to the system path (*/bin)

import os
import subprocess
from common import relative_to_absolute, read_csv, write_csv, makedirs_helper, get_repo_name

#suppress output
devnull = open(os.devnull, "w")

#Splits data into patches
def get_patches(data, size):
    patches = []
    while len(data) > size:
        patches.append(data[:size])
        data = data[size:]
    patches.append(data)
    return patches

#Starts the subprocess for mining and returns the proc handle
def start_refactoring_miner_proc(s):
    proc = subprocess.Popen(
        'RefactoringMiner -a ' +  s["git_path"] + " -json " + s["report_path"], 
        stdin = devnull, stdout = devnull, shell=True)
    return proc

def create_report_file(path):
    report_path = path+"\\report.json"
    if os.path.exists(report_path):
        os.remove(report_path)
    makedirs_helper(path)
    open(path+"\\report.json", "x").close()
    return path+"\\report.json"

#Processes the given patch
def run_refactoring_miner_on_patch(patch, reports_path):
    #sub process vars
    procs = []
    #Start subprocesses
    for repo in patch:
        repo["mining_report"] = "MINING_FAILED"
        #Is it valid local repo?
        if repo["local_path"] != "FETCH_FAILED":
            #create report.json file
            #repo_report_path = reports_path + "\\" + get_repo_name(repo["source_git"]) +"\\report.json"
            repo_report_path = create_report_file(reports_path + "\\" + get_repo_name(repo["source_git"]))
            procs.append(start_refactoring_miner_proc({
                "git_path": repo["local_path"],
                "report_path": repo_report_path
            }))
            repo["mining_report"] = repo_report_path
    #Wait for mining to finish
    for p in procs:
        p.wait()
    return patch

#Read fetch index
#local_ref_mining_targets = read_sources(relative_to_absolute("fetch_index.csv"), ",")
local_ref_mining_targets = read_csv(relative_to_absolute("fetch_index.csv"), ",", {"source_git":0, "local_path":1})

#Split data into patches for processing
patch_size = 2
local_ref_mining_targets = get_patches(local_ref_mining_targets, patch_size)

#Create folder for the repots
reports_path = relative_to_absolute("rm_reports")
makedirs_helper(reports_path)

mining_index = []
#Start mining according to the settings
for i, patch in enumerate(local_ref_mining_targets):
    print("\n\nProcessing patch: " + str(i))
    mining_index.append(run_refactoring_miner_on_patch(patch, reports_path))

#Write mining index for further processing
#write_index(relative_to_absolute("mining_index.csv"), [r for p in mining_index for r in p], ",")
write_csv(relative_to_absolute("mining_index.csv"), [r for p in mining_index for r in p], ",", {"source_git":0, "local_path":1, "mining_report":2})
#Clean up
devnull.close()
