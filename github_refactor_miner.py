#Download https://github.com/tsantalis/RefactoringMiner Zip
#Get Gradle and requirements https://gradle.org/install/
#cd into the extracted RefactoringMiner root 
#run gradlew distZip or ./gradlew distZip to build distro
#Assumed that build version of RefactorMiner is added to the system path (*/bin)
#You could also modify refactoring_miner_path to point to your version

#If you run into heapsize error you can play around with -Xmx input to the java VM 
#for example -Xmx8192m to set it to around 8GB, mine was 4Gb for default
#https://docs.oracle.com/javase/7/docs/technotes/tools/windows/java.html#BGBGEDBG
#You need to modify the refactoringminer startup script: linux(RefactoringMiner) or windows(RefactoringMiner.bat)
#And add your -Xmx flag to DEFAULT_JVM_OPTS variable in the script: DEFAULT_JVM_OPTS="-Xmx8192m" for linux and set DEFAULT_JVM_OPTS="-Xmx8192m" for windows
#If it doesnt help you better off dropping the project from the list for another

import os
import subprocess
from common import relative_to_absolute, read_csv, write_csv, makedirs_helper, get_repo_name, file_exists, write_json

#try suppress output
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
    #Change this to reflect your placement of the miner
    #refactoring_miner_path = relative_to_absolute("RefactoringMiner-3.0.7\\bin\\RefactoringMiner")
    refactoring_miner_path = "RefactoringMiner"
    proc = subprocess.Popen(
        refactoring_miner_path + " -a " +  s["git_path"] + " -json " + s["report_path"], 
        stdin = devnull, stdout = devnull, shell=True)
    return proc

#If there is a report.json assume this repo is mined
def is_mined(path):
    return file_exists(path)

#Processes the given patch
def run_refactoring_miner_on_patch(patch, reports_path):
    #sub process vars
    procs = []
    #Start subprocesses
    for repo in patch:
        repo["mining_report"] = "MINING_FAILED"
        #Is it valid local repo?
        if repo["local_path"] != "FETCH_FAILED":
            report_folder = reports_path + "\\" + get_repo_name(repo["source_git"])
            report_file = report_folder + "\\report.json"
            if not is_mined(report_file):
                makedirs_helper(report_folder)
                procs.append({
                    "p_object": start_refactoring_miner_proc({"git_path": repo["local_path"],"report_path": report_file}),
                    "repo": repo["local_path"]
                })
            repo["mining_report"] = report_file
    #Wait for mining to finish
    for p in procs:
        p["p_object"].wait()
    #check return codes
    for p in procs:
        if p["p_object"].returncode != 0:
            #mining might have crashed, make a note of it
            write_json(relative_to_absolute("mining_error.json"), {"offening_repo": p["repo"]})
    return patch

#Read fetch index
local_ref_mining_targets = read_csv(relative_to_absolute("fetch_index.csv"), ",", {"source_git":0, "local_path":1})

#Split data into patches for processing
#Increase only if you have tons of memory 
patch_size = 1
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
write_csv(relative_to_absolute("mining_index.csv"), [r for p in mining_index for r in p], ",", {"source_git":0, "local_path":1, "mining_report":2})
#Clean up
devnull.close()
