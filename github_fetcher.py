#given a .csv file this script will fetch all the projects present in that csv file

#option a csv file can be retrieved by copying the html table from the website into this tool https://www.convertcsv.com/html-table-to-csv.htm
#option b csv file can be retrieved using script "option_b_decode_git_urls.py"
#remove unwanted projects from the csv file before feeding it to this script
import time
from git import Repo  # pip install gitpython
from common import relative_to_absolute, read_csv, write_csv, makedirs_helper, get_repo_name

#Fetches the given git project and stores it into target/name folder
#name is decoded from the source
#returns the gits new local path
def fetch_git(source, target):
    name = get_repo_name(source)
    try:
        repo_local_path = target + "\\" + name
        Repo.clone_from(source, repo_local_path)
        return repo_local_path
    except Exception as e:
        print("Failed to fetch: ", name, repr(e))
    return "FETCH_FAILED"
 
#Source of data, modify to reflect the file you importing the gits from
source_file = relative_to_absolute("source.csv")
#Read sources
sources = read_csv(source_file, ",", {"source_git":0})
#create a folder to fetch to
fetch_target = relative_to_absolute("fetched_git")
makedirs_helper(fetch_target)

#Start fetching gits
index = []
for i,source in enumerate(sources):
    print("Fetching source: " + str(i))
    repo_local_path = fetch_git(source["source_git"], fetch_target)
    index.append({"source_git": source["source_git"], "local_path": repo_local_path})
    #sleep 30 seconds and dont spam
    time.sleep(30)

#Write index for further processing
write_csv(relative_to_absolute("fetch_index.csv"), index, ",", {"source_git":0, "local_path":1})