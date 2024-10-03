import re
from os import path

#Summs metrics into one number
def helper_summ_to_commit_level(metric):
    return sum([m["metric"] for m in metric])

#Sums the given data per given rfm file
def helper_sum_metric_per_rfm_file(rfm_files, data):
    metric = []
    for rfm_file in rfm_files:
        if rfm_file in data.keys():
            metric.append({"file": rfm_file, "metric": sum(data[rfm_file])})
    return metric

#Per rfm file returns metric normalized by the total data
def helper_normalized_metric_per_rfm_file(cur_data, total_data):
    norm_metric = []
    for cur in cur_data:
        for total in total_data:
            #We have files and they match
            if cur["file"] and total["file"] and path.normpath(cur["file"]) == path.normpath(total["file"]):
                data = {"file": cur["file"], "metric": 0}
                #We have data, dont divide by 0
                if total["metric"] and total["metric"] > 0:
                    data["metric"] = cur["metric"] / total["metric"]
                norm_metric.append(data)
                break
    return norm_metric

#Makes a waypoint from given data
def helper_make_waypoint_per_rfm_file(data, rfm_files, waypoint_metric_func):
    #waypoint for each rfm_file in the commit
    waypoint = []
    for rfm_file in rfm_files:
        #file has data
        if rfm_file in data.keys():
            waypoint.append(
                {
                    "file": rfm_file,
                    "metric": waypoint_metric_func(data[rfm_file])
                }
            )
    return waypoint

#Calculates metric values for the given rfm_files from the given data
def helper_make_waypoint_per_rfm_file_neigbours(data, rfm_files, waypoint_metric_func):
    metric_data = []
    #Dont modify the source
    neighbours = list(rfm_files)
    excluded_file_index = len(neighbours) - 1
    #run trough files calculating metric
    while excluded_file_index >= 0:
        #Pick out the targeted file
        excluded_file = neighbours.pop(excluded_file_index)
        #Calculate metric using the remaining files
        metric_value = 0
        for neighbour_file in neighbours:
            metric_value = metric_value + waypoint_metric_func(data[neighbour_file])
        #Remember the value for the excluded file
        metric_data.append({"file": excluded_file, "metric": metric_value})
        #Move to the next file and push the previous back on the neighbours
        excluded_file_index = excluded_file_index - 1
        neighbours.append(excluded_file)
    return metric_data

#Extract potential java package name from source code
def helper_extract_java_package_name(source_code):
    #if we have source code
    if source_code:
        #Is the package keyword present in the source code. Extract the name
        packages_modified = re.findall(r'package\s+([\w\.]+);', source_code)
        if packages_modified:
            #https://docs.oracle.com/javase/tutorial/java/package/createpkgs.html
            #file can have only one package declaration
            return packages_modified[0]
        #If you do not use a package statement, your type ends up in an unnamed package
        #docs say so, thus we consider this a package
        return "unnamed"
    #No package possible, we do not have source code
    return ""

#Extracts all modified packages from the commit source file
def helper_extract_modified_packages(file):
    #Get current and past source code
    file_source_codes = [file.source_code_before, file.source_code]
    potential_packages = []
    #Run trough the source files
    for file_source_code in file_source_codes:
        package = helper_extract_java_package_name(file_source_code)
        if package:
            potential_packages.append(package)
    #return unique package names
    return list(set(potential_packages))

#Returns the largest contributor to the given file
def helper_get_largest_contributor_for_file(data, file):
    largest_contributor = {"author": "",  "lines": 0}
    #Find out the largest contributor
    for author in data[file]:
        if data[file][author] > largest_contributor["lines"]:
            largest_contributor = {"author": author, "lines": data[file][author]}
    return largest_contributor

#Returns name of the author that is highest commiter of the file based on the given data
def helper_get_highest_commiter_of_file(data, file):
    highest_commiter = {"author": "", "commits":0}
    for author in data[file]:
        commits_authored = sum(data[file][author])
        if commits_authored > highest_commiter["commits"]:
            highest_commiter = {"author":author, "commits": commits_authored}
    return highest_commiter