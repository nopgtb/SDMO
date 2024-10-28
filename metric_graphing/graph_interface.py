from .graph_util import Graph_Util

class Graph_Interface:

    #Visualize the given data
    @staticmethod
    def graph(data, metric):
        pass

    #Returns the data frame fitting the graph for the metric
    @staticmethod
    def get_data_frame(git, data, metric):
        pass
    
    #Returns a string representation of the graphs type
    @staticmethod
    def get_graph_type():
        pass

    #Stores the fig as html and image at the given path
    @staticmethod
    def save_fig(image_path, html_path, name, fig):
        Graph_Util.save_fig_html(html_path + "\\" + name + ".html", fig)
        Graph_Util.save_fig_image(image_path + "\\" + name + ".png", fig)