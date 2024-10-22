import plotly.express as px
from common import *
import plotly.io
import pandas
import metrics 

def plug_dataframe(git, data, metric_to_plug):
    if metric_to_plug.get_collection_level() == "commit":
        return pandas.DataFrame(plug_commit_level_metric(git, data, metric_to_plug.get_metric_name()))
    return pandas.DataFrame()

def plug_commit_level_metric(git, data, id):
    return {
        "git": [git for hash in data],
        "values":[hash["metric_" + id] for hash in data],
        "hash_num": [index for index,hash in enumerate(data)]
    }

def store_fig_html(path, fig):
    plotly.io.write_html(fig, path)

def store_fig_image(path, fig):
    plotly.io.write_image(fig, path, "png")

def visualize_metric(df, metric_to_plug):
    if metric_to_plug.get_collection_level() == "commit":
        return visualize_commit_level_metric(df, metric_to_plug)

def visualize_commit_level_metric(df, metric_to_plug):
    return px.line(df, x="hash_num", y="values", color = "git")


#list for metric calculating functions
metrics_table = [
    metrics.Metric_COMM(),
    metrics.Metric_NCOMM(),
    metrics.Metric_ADEV(),
    metrics.Metric_DDEV(),
    metrics.Metric_ADD(),
    metrics.Metric_DEL(),
    metrics.Metric_OWN(),
    metrics.Metric_MINOR(),
    metrics.Metric_NADEV(),
    metrics.Metric_NDDEV(),
    metrics.Metric_OEXP(),
    metrics.Metric_EXP(),
    metrics.Metric_ND(),
    metrics.Metric_NF(),
    metrics.Metric_NS(),
    metrics.Metric_ENTROPY(),
    metrics.Metric_LA(),
    metrics.Metric_LD(),
    metrics.Metric_LT(),
    metrics.Metric_FIX(),
    metrics.Metric_NDEV(),
    metrics.Metric_AGE(),
    metrics.Metric_NUC(),
    metrics.Metric_CEXP(),
    metrics.Metric_REXP(),
    metrics.Metric_SEXP(),
    metrics.Metric_CBO(),
    metrics.Metric_WMC(),
    metrics.Metric_RFC(),
    metrics.Metric_ELOC(),
    metrics.Metric_NOM(),
    metrics.Metric_NOPM(),
    metrics.Metric_DIT(),
    metrics.Metric_NOC(),
    metrics.Metric_NOF(),
    metrics.Metric_NOSF(),
    metrics.Metric_NOPF(),
    metrics.Metric_NOSM(),
    metrics.Metric_NOSI(),
]

fig_folder = relative_to_absolute("metric_figs")
if makedirs_helper(fig_folder):
    #Read index
    repositories = read_csv(relative_to_absolute("part_2_submission_index.csv"), ",", {"source_git":0, "local_path":1, "mining_report":2, "commit_messages":3, "commit_diffs":4, "metric_report": 5})
    #Load metric datas
    metric_reports = {}
    for repository in repositories:
        metric_reports[get_repo_name(repository["source_git"])] = read_json(repository["metric_report"])

    for metric in metrics_table:
        #Plug all the data for the metric accross projects
        metric_dataframes = []
        for repo_name in metric_reports:
            df = plug_dataframe(repo_name, metric_reports[repo_name], metric)
            if not df.empty :
                metric_dataframes.append(df)
        #combine them into one df
        if len(metric_dataframes) > 0:
            combined_dataframe = pandas.concat(metric_dataframes)
            #visualize the frame
            fig = visualize_metric(combined_dataframe, metric)
            fig_filename = fig_folder + "\\" + metric.get_metric_name()
            store_fig_html(fig_filename + ".html", fig)
            store_fig_image(fig_filename + ".png", fig)
    
        