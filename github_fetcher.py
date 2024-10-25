#given a .csv file this script will fetch all the projects present in that csv file

#option a csv file can be retrieved by copying the html table from the website into this tool https://www.convertcsv.com/html-table-to-csv.htm
#option b csv file can be retrieved using script "option_b_decode_git_urls.py"
#remove unwanted projects from the csv file before feeding it to this script

#Depending on project size, fetching local version migth take very long
#It gave me checkout errors this helped if you get them too: git config --system core.longpaths true

import time
from git import Repo
from util import Util

#Fetches the given git project and stores it into target/name folder
#name is decoded from the source
#returns the gits new local path
def fetch_git(source, target):
    name = Util.get_repo_name(source)
    try:
        repo_local_path = target + "\\" + name
        #If it exists assume we fetched earlier
        #Just return the path
        if not Util.file_exists(repo_local_path):
            Repo.clone_from(source, repo_local_path)
        return repo_local_path
    except Exception as e:
        print("Failed to fetch: ", name, repr(e))
    return "FETCH_FAILED"
 
#Source of data, modify to reflect the file you importing the gits from
input_file = Util.relative_to_absolute("source.csv")
output_file = Util.relative_to_absolute("fetch_index.json")

if not Util.file_exists(output_file):
    if Util.file_exists(input_file):
        #Read sources
        sources = Util.read_csv(input_file, ",", {"source_git":0})
        #create a folder to fetch to
        fetch_target = Util.relative_to_absolute("fetched_git")
        if(Util.make_directory(fetch_target)):
            #Start fetching gits
            result_index = []
            for i,source in enumerate(sources):
                print("Fetching source: " + source["source_git"])
                repo_local_path = fetch_git(source["source_git"], fetch_target)
                result_index.append({"source_git": source["source_git"], "local_path": repo_local_path})
                #sleep 30 seconds and dont spam
                time.sleep(30)
            #Write index for further processing
            Util.write_json(output_file, result_index)
        else:
            print("Failed to create folder. Cant proceed")
    else:
        print("Could not find input file: ", input_file)
else:
    print("Found ", output_file, " skipping")
