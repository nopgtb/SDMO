import re
import os
import csv
import json
import datetime
from pathlib import Path
from git import Repo  # pip install gitpython
from pydriller import Repository #pip install pydriller

#Get repo name from github .git link
def get_repo_name(url):
    return re.sub(r'https:\/\/github\.com\/[^\/]+\/|\.git', '', url)

#Make relative path to absolute path
#returns absolute path of given relative path
#example: github_search.py to C:\mycoolproject\github_search.py 
def relative_to_absolute(path):
    return str(Path(__file__).parent) + "\\" + path

#Read csv with given structure
def read_csv(path, delimiter, struct):
    sources = []
    try:
        with open(path, newline='') as csv_file:
            source_reader = csv.reader(csv_file, delimiter=delimiter)
            sources = [{key:r[struct[key]] for key in struct.keys()} for r in source_reader]
    except Exception as e:
        print("Failed to read sources:", path, ",", repr(e))
        return []
    #remove header
    return sources[1:]

#Writes source csv
def write_csv(path, sources, delimiter, struct):
    try:
        with open(path, "a+", newline="", encoding="utf-8") as source_file:
            csv_writer = csv.writer(source_file, delimiter=delimiter)
            #write header row
            csv_writer.writerow([key for key in struct.keys()])
            #write data
            csv_writer.writerows([[i[key] for key in struct.keys()] for i in sources])
    except Exception as e:
        print("Failed to write source csv: ", path, repr(e))

#Does the file exist
def file_exists(path):
    return os.path.exists(path)

#Checks if folder exits and makes if it doesnt recursivly
def makedirs_helper(target):
    try:
        if not os.path.exists(target):
            os.makedirs(target)
        return True
    except Exception as e:
        print("Failed to create folder: ", target, repr(e))
    return False

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

#Gets a formated timestamp
def get_timestamp():
    return datetime.datetime.now().strftime('%H:%M:%S')

#Returns single commit object based on given sha
#from the given repo
def get_commit_by_hash(repo, sha):
    return next(Repository(repo, single=sha).traverse_commits())

#based on https://stackoverflow.com/questions/69651536/how-to-get-master-main-branch-from-gitpython#answer-77281772
#returns default branch name
def get_main_branch(path):
    show_result = Repo.init(path).git.remote("show", "origin")  
    matches = re.search(r"\s*HEAD branch:\s*(.*)", show_result)
    if matches:
        return matches.group(1)
    return ""