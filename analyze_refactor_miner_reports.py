#If you run into git error: detected dubious ownership ownership of repo
#this might help https://stackoverflow.com/questions/72978485/git-submodule-update-failed-with-fatal-detected-dubious-ownership-in-reposit#answer-73100228
#or just run the succested command for each folder

import shutil
from pydriller import Repository
from util import Util

#Extract all the commits that have been deemed to have refactorings
def get_refactored_commits(mined_repo):
    rf_commits = []
    #is valid report?
    if mined_repo["mining_report"] != "MINING_FAILED":
        mining_report = Util.read_json(mined_repo["mining_report"])
        if mining_report:
            for commit in mining_report["commits"]:
                #If the commit has refactorings
                if len(commit["refactorings"]) > 0:
                    #Take hash, we only need that
                    rf_commits.append(commit["sha1"])
    return rf_commits

#Gets the previous commmit
def get_previous_commit(commit):
    #https://pydriller.readthedocs.io/en/latest/commit.html
    #According to this previous commits are in a parents str_list
    #For now just naively get the first one?
    #I guess if it becomes a issue, you can do branch analysis here
    return commit.parents[0]

def mine_details_from_repo(mr, mined_commits):
    detailed_commit_info = []
    if len(mined_commits) > 0:
        #https://pydriller.readthedocs.io/en/latest/commit.html for commit struct info
        for commit in Repository(mr["local_path"]).traverse_commits():
            try:
                #is refactoring commit?
                if(commit.hash in mined_commits):
                    detailed_commit_info.append({
                        "hash":commit.hash,
                        "msg": commit.msg ,
                        "diff":[{"file": mf.filename, "new_path": mf.new_path, "old_path": mf.old_path, "diff_parsed": mf.diff_parsed} for mf in commit.modified_files],
                        "previous_hash": get_previous_commit(commit)
                    })
            except:
                #Git might thorw some errors just continue
                continue
    return detailed_commit_info


output_file = Util.relative_to_absolute("part_1_submission_index.json")
input_file = Util.relative_to_absolute("mining_index.json")

if not Util.file_exists(output_file):
    if Util.file_exists(input_file):
        #make submission folder
        submission_folder = Util.relative_to_absolute("part_1_submission")
        if(Util.make_directory(submission_folder)):
            #Read the mined repos for processing
            mined_repos = Util.read_json(input_file)
            
            #process repos
            for mr in mined_repos:
                print("Mining details from: " + mr["source_git"])
                #check if we want to skip this
                repo_submission_folder = submission_folder + "/" + Util.get_repo_name(mr["source_git"])
                if not Util.file_exists(repo_submission_folder):
                    #Get all refactored commits
                    refactored_commits = get_refactored_commits(mr)
                    if refactored_commits:
                        #Mine wanted data from the repo
                        mined_commits = mine_details_from_repo(mr, refactored_commits)
                        print("Outputting submission for: " + mr["source_git"])

                        #output to submission folder
                        #Create folder for repo

                        Util.make_directory(repo_submission_folder)
                        #Copy rminer output
                        shutil.copyfile(mr["mining_report"], repo_submission_folder + "/rminer-output.json")
                        #write refactor commit message file
                        Util.write_json(
                            repo_submission_folder + "/rcommit-messages.json", 
                            [{"commit_hash" : commit["hash"], "commit_message": commit["msg"]} for commit in mined_commits]
                        )
                        #write diff json
                        Util.write_json(
                            repo_submission_folder + "/rcommit-diffs.json",
                            [{"commit_hash": commit["hash"], "previous_commit_hash": commit["previous_hash"], "diff": commit["diff"]} for commit in mined_commits]
                        )
                    else:
                        print("Warning did not find any refactoring commits for ", mr["source_git"], ". Potentially faulty mining report.")
                #Create index for easy access in part 2
                mr["commit_messages"] = repo_submission_folder + "/rcommit-messages.json"
                mr["commit_diffs"] = repo_submission_folder + "/rcommit-diffs.json"

            Util.write_json(output_file, mined_repos)
        else:
            print("Failed to create folder. Could not proceed")
    else:
        print("Did not find input file: ", input_file)
else:
    print("Found ", output_file, " skipping")