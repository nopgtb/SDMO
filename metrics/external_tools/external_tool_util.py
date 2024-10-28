import os
import csv
import json
from pathlib import Path

#Static class for external tool utility
class External_Tool_Util:

    #Writes json to file
    @staticmethod
    def write_json(path, data):
        with open(path, "a+") as file:
            json.dump(data, file)

    #read a json file
    @staticmethod
    def read_json(path):
        data = {}
        with open(path, "r") as file:
            data = json.load(file)
        return data

    #Given a relative path, makes it a absolute path using the location of the request orignator file
    @staticmethod
    def relative_to_absolute(path, current_file):
        return str(Path(os.path.abspath(current_file)).parent) + "\\" + path 
    
    #Read csv and pick only data assosiated with given keys of interest
    @staticmethod
    def read_csv(path, delimiter, keys_of_interest):
        out_data = []
        try:
            csv_data = []
            #Read csv data
            with open(path, newline='') as csv_file:
                source_reader = csv.reader(csv_file, delimiter=delimiter)
                csv_data = [l for l in source_reader if l]
            #Map keys_of_interest to indexs in the csv by checking the header
            interest_map = {v:i for i,v in enumerate(csv_data[0]) if v in keys_of_interest}
            #Fetch data of interest using the map
            out_data = [{k:l[interest_map[k]] for k in keys_of_interest} for l in csv_data[1:]]
        except OSError as e:
            out_data = []
        return out_data
    
    #Returns if folder exists
    @staticmethod
    def path_exists(path):
        return os.path.exists(path)

    #Create a folder
    @staticmethod
    def create_folder(path):
        if not External_Tool_Util.path_exists(path):
            os.makedirs(path, exist_ok=True)