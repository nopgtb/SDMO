from numpy import random
import plotly.io

class Graph_Util:
    #Samples n of the given data at random
    @staticmethod
    def sample_n(data, n):
        sample_index = random.randint(0, len(data), size=(n))
        return list(set([data[sn] for sn in sample_index]))

    #Returns a list of all the unique subkeys present in the data
    @staticmethod
    def get_unique_subkeys(data, metric_key, subkey, min_num_of_non_zero_values):
        sub_data = {}
        #Get the subkeys from the data
        for hash in data:
            if not hash[metric_key] == None:
                for file_metric in hash[metric_key]:
                    if float(file_metric["metric"]) > 0:
                        sub_data[file_metric[subkey]] = sub_data.get(file_metric[subkey],0) + 1
        #Make it unique
        candidates = [f for f in sub_data.keys() if sub_data[f] >= min_num_of_non_zero_values]
        return list(set(candidates))
    
    #Saves given fig as html page to the given path
    @staticmethod
    def save_fig_html(path, fig):
        plotly.io.write_html(fig, path)

    #Saves given fig as a png at the given path
    @staticmethod
    def save_fig_image(path, fig):
        plotly.io.write_image(fig, path, "png")