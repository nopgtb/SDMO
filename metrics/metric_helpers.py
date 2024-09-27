from os import path

#Summs metrics into one number
def helper_summ_to_commit_level(metric):
    return sum([m["metric"] for m in metric])

#Picks metrics for given refactored files
def helper_metric_for_rf_file(file_metrics, rf_files):
    metric = []
    #Get data for files that have been refactored
    for file in file_metrics.keys():
        norm_path = path.normpath(str(file))
        #Reformat here for consistency accross tools        
        if(norm_path in rf_files):
            metric.append({"file": norm_path, "metric": file_metrics[norm_path]})
    return metric

#Makes a waypoint from given data
def helper_make_waypoint(commits_made, commit, rfm_commit):
    #Set DDEV waypoint for each file in the commit
    waypoint = []
    for rfm_file in rfm_commit["rfm_data"]["refactored_files"]:
        #File has contributors
        if rfm_file in commits_made.keys():
            #Append object: file => unique count of devs
            waypoint.append(
                {
                    "file": rfm_file,
                    "metric": sum(commits_made[rfm_file])
                }
            )
    return waypoint