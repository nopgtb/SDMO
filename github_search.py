#If allowed this file will allow to query the github api for projects for option_a_bonus
#It will place projects into source.csv
#It requires a github api key, placed into variable api_token

import csv
import json
import requests
import time
from pathlib import Path

#Api token for authenticating wiht github api
#https://github.com/settings/tokens - Generate new token => Generate new token (classic)
#Scope doesnt matter, copy the "ghp_" string here
api_token = ""

#Make relative path to absolute path
#returns absolute path of given relative path
#example: github_search.py to C:\mycoolproject\github_search.py 
def relative_to_absolute(path):
    return str(Path(__file__).parent) + "\\" + path

#Uses the api to get repos present in the search using the given query
#https://docs.github.com/en/rest/search/search#search-repositories
#takes a query string https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#constructing-a-search-query
#takes a sort string: empty string, stars, forks, help-wanted-issues, updated
#takes a order string: emnty string, desc, asc
def get_repo_json(token, query, sort, order, page, per_page):
    request_url = "https://api.github.com/search/repositories?sort=" + sort + "&order=" + order + "&q=" + query + "&page=" + str(page) + "&per_page=" + str(per_page)
    response = requests.request("GET", request_url, headers={'Authorization': 'Token ' + token})
    return json.loads(response.text)

#generate a structure that we can use for academic purposes and creating a dataset
#https://docs.github.com/en/rest/search/search#search-repositories
def parse_source_info(json, query):
    sources = []
    for item in json["items"]:
        sources.append(
            {
                "source_git":item["git_url"],
            }
        )
    return sources

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

#Query the Github API
query = "language:Java license:Unlicense"
sources = []
for i in range(2):
    #Query starting from page 1, for total of 124 projects
    repo_json = get_repo_json(api_token, query, "stars", "desc", i+1, 62)
    sources.extend(parse_source_info(repo_json, query))


#Write all the data to source.csv
write_source(relative_to_absolute("source.csv"), sources, ",")