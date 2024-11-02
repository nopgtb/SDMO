import re
import os
import csv
import json
import datetime
from pathlib import Path
from git import Repo

#Static class containing utility functions
class Util:

    #Get repo name from github .git link
    @staticmethod
    def get_repo_name(url):
        return re.sub(r'https:\/\/github\.com\/[^\/]+\/|\.git', '', url)

    #Make relative path to absolute path
    @staticmethod
    def relative_to_absolute(path):
        return str(Path(os.path.abspath(__file__)).parent) + "\\" + path

    #Read csv with given structure
    @staticmethod
    def read_csv(path, delimiter, struct):
        sources = []
        try:
            with open(path, newline='') as csv_file:
                source_reader = csv.reader(csv_file, delimiter=delimiter)
                sources = [{key:r[struct[key]] for key in struct.keys()} for r in source_reader]
        except Exception as e:
            print("Failed to read sources:", path, ",", repr(e))
            return []
        #remove header
        return sources[1:]

    #Does the file exist
    @staticmethod
    def file_exists(path):
        return os.path.exists(path)

    #Checks if folder exits and makes if it doesnt recursivly
    @staticmethod
    def make_directory(target):
        try:
            if not os.path.exists(target):
                os.makedirs(target)
            return True
        except Exception as e:
            print("Failed to create folder: ", target, repr(e))
        return False

    #read a json file
    @staticmethod
    def read_json(path):
        data = {}
        with open(path, "r") as file:
            try:
                data = json.load(file)
            except json.decoder.JSONDecodeError:
                pass
        return data

    #Writes json to file
    @staticmethod
    def write_json(path, data):
        with open(path, "w+") as file:
            json.dump(data, file)

    #Gets a formated timestamp
    @staticmethod
    def get_timestamp():
        return datetime.datetime.now().strftime('%H:%M:%S')

    #returns default branch name
    @staticmethod
    def get_main_branch(path):
        return Repo.init(path).active_branch.name