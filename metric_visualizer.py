from util import Util
import pandas
import metrics 
from metric_graphing.heatmap_graph import HeatMap_Graph
from metric_graphing.line_graph import Line_Graph

metrics_table = {
    metrics.Metric_COMM: [Line_Graph], #commit level
    metrics.Metric_NCOMM: [HeatMap_Graph], #file level
    metrics.Metric_ADEV: [Line_Graph], #commit level
    metrics.Metric_DDEV: [Line_Graph], #commit level
    metrics.Metric_ADD: [Line_Graph], #commit level
    metrics.Metric_DEL: [Line_Graph], #commit level
    metrics.Metric_OWN: [Line_Graph], #commit level
    metrics.Metric_MINOR: [Line_Graph], #commit level
    metrics.Metric_NADEV: [HeatMap_Graph], #file level
    metrics.Metric_NDDEV: [HeatMap_Graph], #file level
    metrics.Metric_OEXP: [HeatMap_Graph], #file level
    metrics.Metric_EXP: [Line_Graph], #author level
    metrics.Metric_ND: [Line_Graph], #commit level
    metrics.Metric_NF: [Line_Graph], #commit level
    metrics.Metric_NS: [Line_Graph], #commit level
    metrics.Metric_ENTROPY: [Line_Graph], #commit level
    metrics.Metric_LA: [Line_Graph], #commit level
    metrics.Metric_LD: [Line_Graph], #commit level
    metrics.Metric_LT: [Line_Graph], #commit level
    metrics.Metric_FIX: [Line_Graph], #commit level
    metrics.Metric_NDEV: [Line_Graph], #commit level
    metrics.Metric_AGE: [Line_Graph], #commit level
    metrics.Metric_NUC: [Line_Graph], #commit level
    metrics.Metric_CEXP: [Line_Graph], #commit level
    metrics.Metric_REXP: [HeatMap_Graph], #file level
    metrics.Metric_SEXP: [HeatMap_Graph], #file level
    metrics.Metric_CBO: [HeatMap_Graph], #class level
    metrics.Metric_WMC: [HeatMap_Graph], #class level
    metrics.Metric_RFC: [HeatMap_Graph], #class level
    metrics.Metric_ELOC: [HeatMap_Graph], #class level
    metrics.Metric_NOM: [HeatMap_Graph], #class level
    metrics.Metric_NOPM: [HeatMap_Graph], #class level
    metrics.Metric_DIT: [HeatMap_Graph], #class level
    metrics.Metric_NOC: [HeatMap_Graph], #class level
    metrics.Metric_NOF: [HeatMap_Graph], #class level
    metrics.Metric_NOSF: [HeatMap_Graph], #class level
    metrics.Metric_NOPF: [HeatMap_Graph], #class level
    metrics.Metric_NOSM: [HeatMap_Graph], #class level
    metrics.Metric_NOSI: [HeatMap_Graph], #class level
    metrics.Metric_C3: [HeatMap_Graph], #class level
    metrics.Metric_HSLCOM: [HeatMap_Graph], #class level
    metrics.Metric_COMREAD: [HeatMap_Graph], #class level
}

input_file = Util.relative_to_absolute("part_2_submission_index.json")
output_path = Util.relative_to_absolute("part_2_submission/graphs")

if Util.file_exists(input_file):
    if Util.make_directory(output_path):
        #Read index
        repositories = Util.read_json(input_file)
        #Load metric datas
        metric_reports = {}
        for repository in repositories:
            repo_name = Util.get_repo_name(repository["source_git"])
            repo_graph_folder = output_path + "\\" + repo_name
            repo_html_folder = output_path + "\\" + repo_name + "\\html"
            #Create folder for the git and add the data for processing
            if Util.make_directory(repo_graph_folder) and Util.make_directory(repo_html_folder):
                metric_reports[repo_name] = Util.read_json(repository["metric_report"])
                #For each metric
                for metric in metrics_table:
                    #For each graph type
                    for graph_type in metrics_table[metric]:
                        #Get data in format for the graph
                        fig_data = graph_type.get_data_frame(repo_name, metric_reports[repo_name], metric)
                        if isinstance(fig_data, pandas.DataFrame) and not fig_data.empty or not isinstance(fig_data, pandas.DataFrame) and fig_data:
                            #If data graph and save
                            fig = graph_type.graph(fig_data, metric)
                            fig_name = graph_type.get_graph_type() + "_" + metric.get_metric_name()
                            graph_type.save_fig(repo_graph_folder, repo_html_folder, fig_name, fig)
                        else:
                            print("Could not graph: ", metric.get_metric_name())
            else:
                print("Could not create graph folder: ", repo_graph_folder, " or ", repo_html_folder)
else:
    print("Did not find input file: ", input_file)
    
        