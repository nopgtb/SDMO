from .graph_interface import Graph_Interface
from plotly.subplots import make_subplots
from .graph_util import Graph_Util
import plotly.graph_objects as go
import plotly.express as px
import pandas

class Line_Graph(Graph_Interface):

    #Returns a string representation of the graphs type
    @staticmethod
    def get_graph_type():
        return "line_graph"

    #Visualize the given data
    @staticmethod
    def graph(data, metric):
        fig = px.line(data, x="hash_num", y="values", color = "git")
        return fig

    #Returns the data frame fitting the graph for the metric
    @staticmethod
    def get_data_frame(git, data, metric):
        if metric.get_collection_level() == "commit" or metric.get_collection_level() == "author":
            return Line_Graph.commit_level_data(git, data, metric)
        elif metric.get_collection_level() == "file" or  metric.get_collection_level() == "class":
            return Line_Graph.sub_level_data(git, data, metric)
        return None

    @staticmethod
    def commit_level_data(git, data, metric):

        graph_data = {
            "git":[],
            "values":[],
            "hash_num":[]
        }
        metric_key = "metric_" + metric.get_metric_name()
        for index, hash in enumerate(data):
            if not hash[metric_key] == None:
                graph_data["git"].append(git)
                graph_data["values"].append(hash[metric_key])
                graph_data["hash_num"].append(index)
        return pandas.DataFrame(graph_data)

    @staticmethod
    def sub_level_data(git, data, metric):
        metric_key = "metric_" + metric.get_metric_name()
        graph_data = {
            "git":[],
            "values":[],
            "hash_num":[]
        }
        metric_key = "metric_" + metric.get_metric_name()
        for index, hash in enumerate(data):
            if not hash[metric_key] == None:
                hash_avg = 0
                sub_values = [float(sub_val["metric"]) for sub_val in hash[metric_key] if sub_val and sub_val["metric"]]
                if len(sub_values) > 0:
                    hash_avg = sum(sub_values) / len(sub_values)
    
                graph_data["git"].append(git)
                graph_data["values"].append(hash_avg)
                graph_data["hash_num"].append(index)
        return pandas.DataFrame(graph_data)
