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