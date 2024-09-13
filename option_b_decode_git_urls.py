#Reads the sonar_measures.csv and returns a sources.csv containing .git links for all the projects
#You can then feed it into github_fetcher.py
from common import relative_to_absolute, read_csv, write_csv

def sonar_to_git(path):
    #Read the file, asuming its in the same forlder with the script
    sonar_sources = read_csv(path, ",", {"project":1})
    sonar_sources = [r["project"] for r in sonar_sources]
    #Get unique projects
    sonar_sources = list(set(sonar_sources))
    #Drop the apache_ and turn into git link
    sonar_sources = [{"source_git":"https://github.com/apache/" + r.replace("apache_", "") + ".git"} for r in sonar_sources]
    return sonar_sources
    
#fetch gits
sonar_gits = sonar_to_git(relative_to_absolute("sonar_measures.csv"))
#write gits to source.csv
write_csv(relative_to_absolute("source.csv"), sonar_gits, ",", {"source_git":0})