#Reports are in a json format. commits of the branch are listed  commit by commit (["commits"] => array of commits)
#Each commit lists it sha1 signiture (["commits"]["sha1"]) and refactorings that were found in it  (["commits"]["refactorings"])
#Each refactoring has a refactoring type (["commits"]["refactorings"][0]["type"])
#Each refactoring lists the pre change info of the change (["commits"]["refactorings"][0]["leftSideLocations"]) 
#And post change info (["commits"]["refactorings"][0]["rightSideLocations"])

#If you run into git error: detected dubious ownership ownership of repo
#this might help https://stackoverflow.com/questions/72978485/git-submodule-update-failed-with-fatal-detected-dubious-ownership-in-reposit#answer-73100228

import shutil
from git import Repo  # pip install gitpython
from pydriller import Repository #pip install pydriller
from common import relative_to_absolute, read_csv, write_csv, read_json, makedirs_helper, get_repo_name, write_json

#Extract all the commits that have been deemed to have refactorings
def get_refactored_commits(mined_repo):
    rf_commits = []
    #is valid report?
    if mined_repo["mining_report"] != "MINING_FAILED":
        mining_report = read_json(mined_repo["mining_report"])
        for commit in mining_report["commits"]:
            #If the commit has refactorings
            if len(commit["refactorings"]) > 0:
                #Take hash, we only need that
                rf_commits.append(commit["sha1"])
    print(len(rf_commits))
    return rf_commits

def mine_details_from_repo(mr, mined_commits):
    detailed_commit_info = []
    if len(mined_commits) > 0:
        #https://pydriller.readthedocs.io/en/latest/commit.html for commit struct info
        #set flag for getting previous commit hash, I dont seem to find any direct way to get this
        need_previous_commit = False
        for commit in Repository(mr["local_path"]).traverse_commits():
            if need_previous_commit:
                need_previous_commit = False
                detailed_commit_info[-1]["previous_hash"] = commit.hash
            #is refactoring commit?
            if(commit.hash in mined_commits):
                detailed_commit_info.append({
                    "hash":commit.hash,
                    "msg": commit.msg ,
                    "diff":[{"file": mf.filename, "diff_parsed": mf.diff_parsed} for mf in commit.modified_files]
                })
                need_previous_commit = True
    print(len(detailed_commit_info))
    return detailed_commit_info


#make submission folder
submission_folder = relative_to_absolute("part_1_submission")
makedirs_helper(submission_folder)

#Read the mined repos for processing
mined_repos = read_csv(relative_to_absolute("mining_index.csv"), ",", {"source_git":0,"local_path":1,"mining_report":2})

#process repos
for mr in mined_repos:
    print("Mining details from: " + mr["source_git"])
    #Get all refactored commits
    refactored_commits = get_refactored_commits(mr)
    #Mine wanted data from the repo
    mined_commits = mine_details_from_repo(mr, refactored_commits)
    print("Outputting submission for: " + mr["source_git"])

    #output to submission folder
    #Create folder for repo
    repo_submission_folder = submission_folder + "/" + get_repo_name(mr["source_git"])
    makedirs_helper(repo_submission_folder)
    #Copy rminer output
    shutil.copyfile(mr["mining_report"], repo_submission_folder + "/rminer-output.json")
    #write refactor commit message file
    write_csv(
        repo_submission_folder + "/rcommit-messages.csv", 
        [{"commit_hash" : commit["hash"], "commit_message": commit["msg"]} for commit in mined_commits],
        ",", {"commit_hash": 0, "commit_message":1}
    )
    #write diff json
    write_json(
        repo_submission_folder + "/rcommit-diffs.json",
        [{"commit_hash": commit["hash"], "previous_commit_hash": commit["previous_hash"], "diff": commit["diff"]} for commit in mined_commits]
    )

    #Create index for easy access in part 2
    mr["commit_messages"] = repo_submission_folder + "/rcommit-messages.csv"
    mr["commit_diffs"] = repo_submission_folder + "/rcommit-diffs.json"

write_csv(relative_to_absolute("part_1_submission_index.csv"), mined_repos, ",", {"source_git":0, "local_path":1, "mining_report":2, "commit_messages":3, "commit_diffs":4})
