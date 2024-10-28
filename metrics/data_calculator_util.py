import re
import os
import json
import stat
import shutil
import subprocess
from pathlib import Path

#Static class containing utility functions
class Data_Calculator_Util:

    #Extract potential java package name from source code
    @staticmethod
    def extract_java_package_name(source_code):
        #if we have source code
        if source_code:
            #Is the package keyword present in the source code. Extract the name
            packages_modified = re.findall(r'package\s+([\w\.]+);', source_code)
            if packages_modified:
                #https://docs.oracle.com/javase/tutorial/java/package/createpkgs.html
                #file can have only one package declaration
                return packages_modified[0]
            #If you do not use a package statement, your type ends up in an unnamed package
            #if you want to consider it a unique package uncomment the line below
            #return "unnamed"
        #No package possible, we do not have source code
        return ""

    #Extracts all modified packages from the commit source file
    @staticmethod
    def extract_modified_packages(file):
        potential_packages = []
        #We are a java file
        if file.filename[len(file.filename)-5:] == ".java":
            #Get current and past source code
            file_source_codes = [file.source_code_before, file.source_code]
            #Run trough the source files
            for file_source_code in file_source_codes:
                package = Data_Calculator_Util.extract_java_package_name(file_source_code)
                if package:
                    potential_packages.append(package)
            #return unique package names
        return list(set(potential_packages))

    #Gets author of the commit
    @staticmethod
    def get_commit_author(pr_commit):
        return pr_commit.author.email.strip()

    #Gets paths of modified files in list form
    @staticmethod
    def list_commit_files(pr_commit):
        return [f.new_path for f in pr_commit.modified_files if f.new_path]

    #Output to console
    @staticmethod
    def output_to_console(*args):
        print(*args)

    #read a json file
    @staticmethod
    def read_json(path):
        data = {}
        with open(path, "r") as file:
            data = json.load(file)
        return data

    #Writes json to file
    @staticmethod
    def write_json(path, data):
        with open(path, "w+") as file:
            json.dump(data, file)

    #Writes a json file to communicate with the external tool scripts
    @staticmethod
    def write_external_instructions(path, respository, branch, commits_of_interest, analyze_only_commits_of_interest, tool_max_workers, service_needs):
        Data_Calculator_Util.write_json(path, {
                "repository": respository,
                "branch": branch,
                "COI": commits_of_interest,
                "analyze_only_commits_of_interest": analyze_only_commits_of_interest,
                "max_workers": tool_max_workers,
                "service_needs": service_needs
            }
        )

    #Starts the external tool script for the given tool
    @staticmethod
    def start_python_process(path):
        tool_path = Path(path)
        if tool_path.is_file():
            return subprocess.Popen(
                ["python", os.path.abspath(path)], 
                stdin = subprocess.DEVNULL, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL, shell=True #No external input
            )
        return None

    #Copies git from source to target
    @staticmethod
    def copy_git(source, target):
        os.makedirs(target, exist_ok=True)
        new_path = target+"\\"+os.path.basename(source)
        shutil.copytree(source, new_path)
        return new_path

    #Returns if folder exists
    @staticmethod
    def path_exists(path):
        return os.path.exists(path)

    #Removes folder at given path
    @staticmethod
    def remove_folder(path):
        if Data_Calculator_Util.path_exists(path):
            #Based on https://stackoverflow.com/questions/2656322/shutil-rmtree-fails-on-windows-with-access-is-denied#answer-2656408
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files:
                    filename = os.path.join(root, name)
                    os.chmod(filename, stat.S_IWUSR)
                    os.remove(filename)
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(path)

    #Deletes file
    @staticmethod
    def remove_file(path):
        if Data_Calculator_Util.path_exists(path):
            os.remove(path)

    @staticmethod
    #Returns name of the author that is highest commiter of the file based on the given data
    def get_highest_commiter_of_file(commit_data, file):
        hc_author = ""
        hc_commit_count = 0
        #File has commit data
        if file in commit_data.keys():
            #Loop trough the authors and find largest
            for author in commit_data[file]:
                commits_authored = commit_data[file][author]
                if commits_authored > hc_commit_count:
                    hc_commit_count = commits_authored
                    hc_author = author
        return hc_author, hc_commit_count
    
    #Returns list of hashes that contain the given file
    @staticmethod
    def commits_containing_file(commit_data, file, stop_at_commit, ignore_latest):
        data = commit_data[file]
        if stop_at_commit:
            try:
                stop_index = data.index(stop_at_commit)
                data = data[stop_index:]
            except:
                pass
        if ignore_latest:
            data = data[:-1]
        return data
    
    #Given a lists of commits per file, checks which commits have all files present
    @staticmethod
    def files_present_in_commits(smallest_list, lists):
        files_present_in_commits = []
        #Loop trought the shortest commit list and check if the others contain our commits
        for hash in lists[smallest_list]:
            present_in_all = True
            for file_path in lists.keys():
                #Commit present
                present_in_all = (file_path == smallest_list) or (hash in lists[file_path])
                #Are we done?
                if not present_in_all:
                    break
            if present_in_all:
                files_present_in_commits.append(hash)
        return files_present_in_commits