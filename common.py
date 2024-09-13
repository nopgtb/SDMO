import re
import os
import csv
from pathlib import Path

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
            #csv_writer.writerows([[i["source_git"]] for i in sources])
    except Exception as e:
        print("Failed to write source csv: ", path, repr(e))

#Checks if folder exits and makes if it doesnt recursivly
def makedirs_helper(target):
    try:
        if not os.path.exists(target):
            os.makedirs(target)
        return True
    except Exception as e:
        print("Failed to create folder: ", target, repr(e))
    return False