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

#max_sim_mining_procs controlls how many simultanious minings we have at given point, change it according to your specs
#if errors occur during mining, offending repos will be noted in mining_error.json

import time
import subprocess
from util import Util

#Starts the subprocess for mining and returns the proc handle
def start_refactoring_miner_proc(git_path, report_path, tool_path, branch = None):
    args = []
    #Do we have branch to pass to the tool?
    if branch:
        args = [tool_path, "-a",git_path, branch,  "-json", report_path]
    else:
        #No branch given
        args = [tool_path, "-a",git_path, "-json", report_path]
    return subprocess.Popen(
        args, 
        stdin = subprocess.DEVNULL, stdout = subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False
    )
 
#If there is a report.json assume this repo is mined
def is_mined(path):
    return Util.file_exists(path)

#Starts proc using refactoringminer
def start_refactoring_miner_on_repo(repo, reports_path, tool_path, branch):
    proc = {"p_object":None, "repo": repo}
    repo["mining_report"] = "MINING_FAILED"
    #Is it valid local repo?
    if repo["local_path"] != "FETCH_FAILED":
        report_folder = reports_path + "\\" + Util.get_repo_name(repo["source_git"])
        report_file = report_folder + "\\report.json"
        #If not mined make a proc
        if not is_mined(report_file):
            if(Util.make_directory(report_folder)):
                proc = {"p_object": start_refactoring_miner_proc(repo["local_path"], report_file, tool_path, branch),"repo": repo}
                repo["mining_report"] = report_file
        else:
            repo["mining_report"] = report_file
    return proc

#Checks return code and writes error file
def check_procc_for_error(p, repo):
    #We did not exit with nice 0
    if p.returncode != 0:
        #mining might have crashed, make a note of it
        Util.write_json(Util.relative_to_absolute("mining_error.json"), {"offening_repo": repo["source_git"]})



#Change this to reflect your placement of the miner
refactoring_miner_path = Util.relative_to_absolute("RefactoringMiner\\bin\\RefactoringMiner.bat")
input_file = Util.relative_to_absolute("fetch_index.json")
output_file = Util.relative_to_absolute("mining_index.json")
#Controls wheter all branches are mined or only main branch
mine_only_main_branch = False

if not Util.file_exists(output_file):
    #Is the tool where we need it to be?
    if Util.file_exists(refactoring_miner_path):
        if Util.file_exists(input_file):
            #Read fetch index
            local_ref_mining_targets = Util.read_json(input_file)
            #Create folder for the repots
            reports_path = Util.relative_to_absolute("rm_reports")
            if(Util.make_directory(reports_path)):
                result_index = []
                running_proc = []
                next_mining_target = 0
                #change this depending on how mutch memory and cpu you have
                max_sim_mining_procs = 2
                print(Util.get_timestamp() + ": Starting miner")
                #Run while we have targets to mine and mining procs running
                while next_mining_target < len(local_ref_mining_targets) or len(running_proc) > 0:
                    #Check if we need to start new mining procs
                    while next_mining_target < len(local_ref_mining_targets) and len(running_proc) < max_sim_mining_procs:
                        print(
                            "\n" + Util.get_timestamp() + ": Started mining on ", local_ref_mining_targets[next_mining_target]["source_git"],
                            ", repo " + str((next_mining_target+1)) + "/" + str(len(local_ref_mining_targets))
                        )
                        #If we want to mine only the main branch of the git
                        branch = None
                        if mine_only_main_branch:
                            branch = Util.get_main_branch(local_ref_mining_targets[next_mining_target]["local_path"])
                        proc = start_refactoring_miner_on_repo(local_ref_mining_targets[next_mining_target], reports_path, refactoring_miner_path, branch)
                        #Already mined repo
                        if not proc["p_object"]:
                            print("\n" + Util.get_timestamp() + ": Ended mining on ", proc["repo"]["source_git"])
                            result_index.append(proc["repo"])
                        else:
                            running_proc.append(proc)
                        next_mining_target = next_mining_target + 1
                    #Check status of running procs
                    for proc_index, proc in reversed(list(enumerate(running_proc))):
                        #https://docs.python.org/3/library/subprocess.html#subprocess.Popen.poll
                        #None means we still running
                        if not proc["p_object"].poll() == None:
                            print("\n" + Util.get_timestamp() + ": Ended mining on ", proc["repo"]["source_git"])
                            check_procc_for_error(proc["p_object"], proc["repo"])
                            result_index.append(proc["repo"])
                            #Remove done proc
                            running_proc.pop(proc_index)
                    #Sleep 30 seconds, long running procs
                    if len(running_proc) > 0:
                        time.sleep(30)

                #Write mining index for further processing
                Util.write_json(output_file, result_index)
            else:
                print("Could not create folder. Cant proceed")
        else:
            print("Did not find input file: ", input_file)
    else:
        print("Could not find refactoringminer executable! Nothign will be mined! Expected path: ", refactoring_miner_path)
else:
    print("Found ", output_file, " skipping")