#given a .csv file this script will fetch all the projects present in that csv file

#option a csv file can be retrieved by copying the html table from the website into this tool https://www.convertcsv.com/html-table-to-csv.htm
#option b csv file can be retrieved using script "option_b_decode_git_urls.py"
#remove unwanted projects from the csv file before feeding it to this script


import os
import csv
import time
import shutil
import urllib.request
from pathlib import Path
from git import Repo  # pip install gitpython
import re

#Make relative path to absolute path
#returns absolute path of given relative path
#example: github_search.py to C:\mycoolproject\github_search.py 
def relative_to_absolute(path):
    return str(Path(__file__).parent) + "\\" + path

#Read sources.csv, assumes structure(source_git ...)
def read_sources(path, delimiter):
    sources = []
    #assumed file struct, git link is at index 0
    struct = {"source_git":0}
    try:
        with open(path, newline='') as csv_file:
            source_reader = csv.reader(csv_file, delimiter=delimiter)
            sources = [{"source_git":r[struct["source_git"]].strip()} for r in source_reader]
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

#Fetches the given git project and stores it into target/name folder
#name is decoded from the source
#returns the gits new local path
def fetch_git(source, target):
    name = re.sub(r'https:\/\/github\.com\/[^\/]+\/|\.git', '', source)
    try:
        repo_local_path = target + "\\" + name
        Repo.clone_from(source, repo_local_path)
        return repo_local_path
    except Exception as e:
        print("Failed to fetch: ", name, repr(e))
    return "FETCH_FAILED"

#Writes index csv, assumes struct (name, license, folder)
def write_index(path, index, delimiter):
    try:
        with open(path, "w", newline="") as index_file:
            csv_writer = csv.writer(index_file, delimiter=delimiter)
            csv_writer.writerow(["source_git", "local_path"])
            csv_writer.writerows([[i["source_git"], i["local_path"]] for i in index])
    except Exception as e:
        print("Failed to write index: ", path, repr(e))
    
#Source of data, modify to reflect the file you importing the gits from
source_file = relative_to_absolute("source.csv")
#Read sources
sources = read_sources(source_file, ",")
#create a folder to fetch to
fetch_target = relative_to_absolute("fetched_gits")
makedirs_helper(fetch_target)

#Start fetching gits
index = []
for i,source in enumerate(sources):
    print("Fetching source: " + str(i))
    repo_local_path = fetch_git(source["source_git"], fetch_target)
    index.append({"source_git": source["source_git"], "local_path": repo_local_path})
    #sleep and dont spam
    time.sleep(30)
#Write index for further processing
write_index(relative_to_absolute("fetch_index.csv"), index, ",")