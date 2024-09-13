#Download https://github.com/tsantalis/RefactoringMiner Zip
#Get Gradle and requirements https://gradle.org/install/
#cd into the extracted RefactoringMiner root 
#run gradlew distZip or ./gradlew distZip to build distro
#Assumed that build version of RefactorMiner is added to the system path (*/bin)

import re
import os
import csv
import time
import shutil
import urllib.request
from pathlib import Path
import subprocess

#Make relative path to absolute path
#returns absolute path of given relative path
#example: github_search.py to C:\mycoolproject\github_search.py 
def relative_to_absolute(path):
    return str(Path(__file__).parent) + "\\" + path

#Read sources.csv, assumes structure(source_git ...)
def read_sources(path, delimiter):
    sources = []
    #assumed file struct, git link is at index 0
    struct = {"source_git":0, "local_path":1}
    try:
        with open(path, newline='') as csv_file:
            source_reader = csv.reader(csv_file, delimiter=delimiter)
            sources = [{"source_git":r[struct["source_git"]].strip(), "local_path":r[struct["local_path"]]} for r in source_reader]
    except Exception as e:
        print("Failed to read sources:", path, ",", repr(e))
        return []
    #remove header
    return sources[1:]

#Checks if folder exits and makes if it doesnt recursivly
def makedirs_helper(target):
    try:
        if not os.path.exists(target):
            os.makedirs(target)
        return True
    except Exception as e:
        print("Failed to create folder: ", target, repr(e))
    return False

#Does regex on the url to extract the repo name
def get_repo_name(url):
    return re.sub(r'https:\/\/github\.com\/[^\/]+\/|\.git', '', url)

#Splits data into patches
def get_patches(data, size):
    patches = []
    while len(data) > size:
        patches.append(data[:size])
        data = data[size:]
    patches.append(data)
    return patches

#suppress output
devnull = open(os.devnull, "w")

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

#Writes index csv, assumes struct
def write_index(path, index, delimiter):
    try:
        with open(path, "w", newline="") as index_file:
            csv_writer = csv.writer(index_file, delimiter=delimiter)
            csv_writer.writerow(["source_git", "local_path", "mining_report"])
            csv_writer.writerows([[i["source_git"], i["local_path"], i["mining_report"]] for i in index])
    except Exception as e:
        print("Failed to write index: ", path, repr(e))

#Read fetch index
local_ref_mining_targets = read_sources(relative_to_absolute("fetch_index.csv"), ",")

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
write_index(relative_to_absolute("mining_index.csv"), [r for p in mining_index for r in p], ",")

#Clean up
devnull.close()
