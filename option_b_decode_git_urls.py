#Reads the sonar_measures.csv and returns a sources.csv containing .git links for all the projects
#You can then feed it into github_fetcher.py
from pathlib import Path
import csv

#Make relative path to absolute path
#returns absolute path of given relative path
#example: github_search.py to C:\mycoolproject\github_search.py 
def relative_to_absolute(path):
    return str(Path(__file__).parent) + "\\" + path

#Read sonar_measures.csv
def read_sonar_measures(path, delimiter):
    sources = []
    #we only care about index 1, "project"
    struct = {"project":1}
    try:
        with open(path, newline='') as csv_file:
            source_reader = csv.reader(csv_file, delimiter=delimiter)
            sources = [r[struct["project"]] for r in source_reader]
    except Exception as e:
        print("Failed to read sources:", path, ",", repr(e))
        return []
    #remove header
    return sources[1:]

def sonar_to_git(path):
    #Read the file, asuming its in the same forlder with the script
    sonar_sources = read_sonar_measures(path, ",")
    #Get unique projects
    sonar_sources = list(set(sonar_sources))
    #Drop the apache_ and turn into git link
    sonar_sources = [{"source_git":"https://github.com/apache/" + r.replace("apache_", "") + ".git"} for r in sonar_sources]
    return sonar_sources
    
#Writes source csv
def write_source(path, sources, delimiter):
    try:
        with open(path, "a+", newline="", encoding="utf-8") as source_file:
            csv_writer = csv.writer(source_file, delimiter=delimiter)
            #write header row
            csv_writer.writerow(["source_git"])
            #write data
            csv_writer.writerows([[i["source_git"]] for i in sources])
    except Exception as e:
        print("Failed to write source csv: ", path, repr(e))


#fetch gits
sonar_gits = sonar_to_git(relative_to_absolute("sonar_measures.csv"))
#write gits to source.csv
write_source(relative_to_absolute("source.csv"), sonar_gits, ",")