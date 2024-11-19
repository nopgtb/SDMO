import numpy as np
from util import Util
import metrics 

def get_metric_sd_data(metric_val, metric):
    sub_key = metric.get_collection_level()
    if sub_key == "commit" or sub_key == "author":
        return metric_val
    else:
        sub_values = [float(sub_val["metric"]) for sub_val in metric_val if sub_val and sub_val["metric"]]
        if len(sub_values) > 0:
            return sum(sub_values) / len(sub_values)
    return 0

def metric_sd(data, metric):
    sd_data = []
    metric_key = "metric_" + metric.get_metric_name()
    for hash_data in data:
        if hash_data and hash_data[metric_key]:
            sd_data.append(get_metric_sd_data(hash_data[metric_key], metric))
    return np.std(sd_data)

metrics_table = {
    metrics.Metric_COMM: [], #commit level
    metrics.Metric_NCOMM: [], #file level
    metrics.Metric_ADEV: [], #commit level
    metrics.Metric_DDEV: [], #commit level
    metrics.Metric_ADD: [], #commit level
    metrics.Metric_DEL: [], #commit level
    metrics.Metric_OWN: [], #commit level
    metrics.Metric_MINOR: [], #commit level
    metrics.Metric_NADEV: [], #file level
    metrics.Metric_NDDEV: [], #file level
    metrics.Metric_OEXP: [], #file level
    metrics.Metric_EXP: [], #author level
    metrics.Metric_ND: [], #commit level
    metrics.Metric_NF: [], #commit level
    metrics.Metric_NS: [], #commit level
    metrics.Metric_ENTROPY: [], #commit level
    metrics.Metric_LA: [], #commit level
    metrics.Metric_LD: [], #commit level
    metrics.Metric_LT: [], #commit level
    metrics.Metric_FIX: [], #commit level
    metrics.Metric_NDEV: [], #commit level
    metrics.Metric_AGE: [], #commit level
    metrics.Metric_NUC: [], #commit level
    metrics.Metric_CEXP: [], #commit level
    metrics.Metric_REXP: [], #file level
    metrics.Metric_SEXP: [], #file level
    metrics.Metric_CBO: [], #class level
    metrics.Metric_WMC: [], #class level
    metrics.Metric_RFC: [], #class level
    metrics.Metric_ELOC: [], #class level
    metrics.Metric_NOM: [], #class level
    metrics.Metric_NOPM: [], #class level
    metrics.Metric_DIT: [], #class level
    metrics.Metric_NOC: [], #class level
    metrics.Metric_NOF: [], #class level
    metrics.Metric_NOSF: [], #class level
    metrics.Metric_NOPF: [], #class level
    metrics.Metric_NOSM: [], #class level
    metrics.Metric_NOSI: [], #class level
    metrics.Metric_C3: [], #class level
    metrics.Metric_HSLCOM: [], #class level
    metrics.Metric_COMREAD: [], #class level
}

input_file = Util.relative_to_absolute("part_2_submission_index.json")
output_path = Util.relative_to_absolute("part_2_submission/graphs")

if Util.file_exists(input_file):
    if Util.make_directory(output_path):
        #Read index
        repositories = Util.read_json(input_file)
        #Load metric datas
        metric_reports = {}
        metric_sd = {}
        for repository in repositories:
            repo_name = Util.get_repo_name(repository["source_git"])
            #Create folder for the git and add the data for processing
            if repository["metric_report"] != "METRIC_ERROR" and Util.file_exists(repository["metric_report"]):
                metric_reports[repo_name] = Util.read_json(repository["metric_report"])
                #For each metric

                for metric in metrics_table:
                    #Get data in format for the graph
                    metric_sd.setdefault(metric.get_metric_name(),[]).append(metric_sd(metric_reports[repo_name], metric))
            else:
                print("Could not output graphs for ", repository["source_git"])
        
        metric_sd = {key:sum(metric_sd[key])/len(metric_sd[key]) for key in metric_sd}
        metric_sd = dict(sorted(metric_sd.items(), key=lambda item: item[1]))
        print("top lowest sds: ")
        for key in metric_sd:
            print(key, ": ", metric_sd[key])
else:
    print("Did not find input file: ", input_file)