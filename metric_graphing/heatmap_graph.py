from .graph_interface import Graph_Interface
from plotly.subplots import make_subplots
from .graph_util import Graph_Util
import plotly.graph_objects as go
import plotly.express as px
import pandas

class HeatMap_Graph(Graph_Interface):

    #Returns a string representation of the graphs type
    @staticmethod
    def get_graph_type():
        return "heatmap"

    #Visualize the given data
    @staticmethod
    def graph(data, metric):
        fig = None
        if metric.get_collection_level() == "commit" or metric.get_collection_level() == "author":
            fig = px.imshow(data["values"], y=data["git"])
        else:
            #Subplot
            fig = make_subplots(rows=len(data))
            for i, df in enumerate(data):
                fig.add_trace(go.Heatmap(z=df["values"], y=df["sub_key"],x=df["hash_num"], coloraxis = "coloraxis"), (i+1), 1)
            fig.update_layout(coloraxis = {'colorscale':'viridis'})
        return fig

    #Returns the data frame fitting the graph for the metric
    @staticmethod
    def get_data_frame(git, data, metric):
        if metric.get_collection_level() == "commit" or metric.get_collection_level() == "author":
            return HeatMap_Graph.commit_level_data(git, data, metric)
        elif metric.get_collection_level() == "file" or  metric.get_collection_level() == "class":
            return HeatMap_Graph.sub_level_data(data, metric, metric.get_collection_level())
        return None

    @staticmethod
    def commit_level_data(git, data, metric):
        graph_data = {
            "git":[git],
            "values":[],
            "hash_num":[]
        }
        metric_key = "metric_" + metric.get_metric_name()
        for index, hash in enumerate(data):
            if not hash[metric_key] == None:
                graph_data["values"].append(hash[metric_key])
        graph_data["hash_num"] = [i+1 for i in range(len(graph_data["values"]))]
        graph_data["values"] = pandas.DataFrame([graph_data["values"]])
        return graph_data

    @staticmethod
    def sub_level_data(data, metric, sub_key):
        metric_key = "metric_" + metric.get_metric_name()
        sub_keys = Graph_Util.get_unique_subkeys(data, metric_key, metric.get_collection_level(), 5)
        if sub_keys:
            #Sample 10/len(subkey) samples for graphing
            sample_n = 10
            if sample_n > len(sub_key):
                sample_n = len(sub_key)
            sample_keys = Graph_Util.sample_n(sub_keys, 5)
            #Prepare the data structure for the samples
            graph_data = [{"sub_key":[sample_keys[i]], "values":[], "hash_num":[]} for i in range(0,len(sample_keys))]
            #Get the subkeys from the data
            for hash in data:
                if not hash[metric_key] == None:
                    for sub_metric in hash[metric_key]:
                        #Is this data relevant to our sampling?
                        if sub_metric[sub_key] in sample_keys:
                            graph_data[sample_keys.index(sub_metric[sub_key])]["values"].append(sub_metric["metric"])
            #Frame the data and add hash number indicators
            for g in graph_data:
                g["hash_num"] = [i+1 for i in range(len(g["values"]))]
                g["values"] = pandas.DataFrame([g["values"]])
            return graph_data
        return None