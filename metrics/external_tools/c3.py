#Implementation based on the description provided at https://github.com/cqfn/jpeek/blob/master/src/main/resources/org/jpeek/metrics/C3.xsl#L32
import javalang
import argparse
import os
import re
from os import walk
from pathlib import Path
import numpy as np
import json
import javalang.tree
import datetime
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity

#Create co occurance matrix from the words. How many times did each word occur with its pair in the context?
def create_co_occurance_matrix(m_words, word_map, unique_word_count):
    #Each function is considered its own context window
    #unique_word_count * unique_word_count zero matrix
    co_occurance = np.zeros((unique_word_count, unique_word_count), dtype=np.int32)

    #No word can co occur with itself
    if len(m_words) > 1:
        #Loop trough each word in context
        word_counts = {}
        #Findout how many times did each word occur
        for word in m_words:
            word_counts[word] = word_counts.get(word, 0) + 1

        word_1 = 0
        word_2 = 0
        context_unique_words = list(word_counts.keys())
        #Build co occurance matrix
        while word_1 < len(context_unique_words) -1:
            word_2 = (word_1 + 1)
            while word_2 < len(context_unique_words):
                #Find out words place in matrix and their co occurance value
                word_1_index = word_map[context_unique_words[word_1]]
                word_2_index = word_map[context_unique_words[word_2]]
                word_co_occurance_value = min(word_counts[context_unique_words[word_1]], word_counts[context_unique_words[word_2]])
                #Set value for both letters
                co_occurance[word_1_index, word_2_index] = word_co_occurance_value
                co_occurance[word_2_index, word_1_index] = word_co_occurance_value
                word_2 = word_2 + 1
            word_1 = word_1 + 1
    return co_occurance

#Calculates truncated svd
def svd(co_occurance_matrix, truncsvd):
    return truncsvd.fit_transform(co_occurance_matrix)

#Calculates the LSI value for the given words
def lsi(m_words, word_map, unique_word_count, truncsvd):
    #Create co-occurance matrix from the given words
    co_occurance_matrix = create_co_occurance_matrix(m_words, word_map, unique_word_count)
    #Reduce using svd
    if np.max(co_occurance_matrix) > 0:
        #If max is 0 svd will error
        svd_reduced = svd(co_occurance_matrix, truncsvd)
        return svd_reduced
    return None

#Splits CamelCase and vars_seperated_using a _ into individual words
def split_name(name):
    words = []
    #Handle words seperated using _
    for part in name.split("_"):
        #Handle camelcase
        words.extend(re.findall(r'[A-Za-z][a-z]*|[a-z]+', part))
    return words

#Given a function fetches all variable names
def get_method_variable_names(m):
    names = []
    #Parameters
    for var in m.parameters:
        if isinstance(var, javalang.tree.FormalParameter) or isinstance(var, javalang.tree.TypeParameter):
            names.extend(split_name(var.name))
    #Local vars
    if m.body:
        for var in m.body:
            if isinstance(var, javalang.tree.LocalVariableDeclaration):
                for dc in var.declarators:
                    names.extend(split_name(dc.name))
    return names

#Removes every non word element from the comment
def split_comment(comment):
    comment = re.sub(r'[^a-zA-Z0-9\s]', '', comment)
    return comment.split()

def get_method_comments(m, code):
    words = []
    #Javadoc
    if m.documentation:
        words.extend(split_comment(m.documentation))
    #Local comments
    comments = re.findall(r'(//.*?$)|(/\*.*?\*/)', code, re.DOTALL|re.MULTILINE)
    for comment in comments:
        mutlipart_context = []
        #Process possible multilines and keep them in same context
        if not isinstance(comment, str):
            for comment_part in comment:
                mutlipart_context.extend(split_comment(comment_part))
        else:
            mutlipart_context.extend(split_comment(comment))
        #Append the context to the words list
        words.extend(mutlipart_context)
    return words

#Retrieves words present in the method
def get_words_with_context(m, code):
    words = []
    #Function name
    #words.append(split_name(m.name))
    #Get variable name words
    words.extend(get_method_variable_names(m))
    #Get words from comments associated with the method
    words.extend(get_method_comments(m, code))
    #lower case all words and return them
    return [w.lower() for w in words]

#Retrives methods present in the class and their raw source code
def get_class_methods(c, code):
    methods = []
    #Get all methods from the parsed tree
    for item in c.body:
        if isinstance(item, javalang.tree.MethodDeclaration):
            methods.append({"m":item, "code": ""})

    #Retrieve the raw code for the method
    code_split = code.splitlines()
    #Estimate the raw code of the function using the starting point and last know statement of the function
    for m in methods:
        if m["m"].body:
            #Raw code is from declaration to line following last stament
            m["code"] = "\n".join(code_split[m["m"].position.line: m["m"].body[-1].position.line+1])
        else:
            m["code"] = ""
    return methods

#Combines the LSI values of the methods into single matrix
def combine_methods(methods):
    #Get all LSI values shaped as 2D array in one matrix
    lsi_array = [m["lsi_value"].reshape(1,-1) for m in methods if isinstance(m["lsi_value"], np.ndarray)]
    if lsi_array:
        return np.vstack(lsi_array)
    return None

#Calculates the average cms value of the class
def acsm(c, code):
    #Get methods present in class
    methods = get_class_methods(c, code)
    #Cant compare one method
    if len(methods) > 1:
        #Get words from the methods
        all_words = []
        for m in methods:
            #Get the words and their context from the method
            m["words"] = get_words_with_context(m["m"], m["code"])
            #Append the method words to the all words 
            all_words.extend(m["words"])

        min_dimensions = 3
        #We need atleast 3 words total
        if len(all_words) >= min_dimensions:
            #Calculate word matrix dimensions and a word => mat map
            single_dim_uniq_words = list(set(all_words))
            word_map = {w:i for i,w in enumerate(single_dim_uniq_words)}
            word_count = len(single_dim_uniq_words)
            truncsvd = TruncatedSVD(n_components=min_dimensions)
            for m in methods:
                m["lsi_value"] = lsi(m["words"], word_map, word_count, truncsvd)
            #Combine LSIs into single matrix
            lsi_matrix = combine_methods(methods)
            if isinstance(lsi_matrix, np.ndarray):
                #Calculate size of non diag upper mat_size - (n*(n+1))/2, where n is mat size in dim 1
                values_in_upper = (lsi_matrix.shape[0] * lsi_matrix.shape[0]) - ((lsi_matrix.shape[0] * (lsi_matrix.shape[0] + 1)) / 2)
                if values_in_upper > 0:
                    #Calculate similarity between each row pair in LSI matrix == CMS
                    lsi_sim_matrix = cosine_similarity(lsi_matrix)
                    #We only care about the values in the non diagonal upper triangle, sum them
                    #The upper and lower matrix are mirrored, avg wont be affected if we only calculate one of them
                    #Diag contains identity similarity == 1
                    np.fill_diagonal(lsi_sim_matrix, 0)
                    upper_sum = np.triu(lsi_sim_matrix).sum()
                    #Return the average similarity
                    return upper_sum / values_in_upper
    elif len(methods) == 1:
        #There is only 1 function, it is 100% similiar with itself
        return 1
    return 0

#Calculates the c3 value for the given class
def c3(c, code):
    val = acsm(c, code)
    if val > 0:
        return val
    return 0

#Traverses the given parsed tree and returns present classes
def get_file_classes(parsed_java):
    classes_present = []
    for type in parsed_java.types:
        #Are we a class?
        if isinstance(type, javalang.tree.ClassDeclaration):
            #Get a class name prefixed with possible package
            class_name = ""
            if parsed_java.package:
                class_name = parsed_java.package.name + "."
            class_name = class_name + type.name
            #Store obj and name
            classes_present.append({"class": class_name, "obj": type})
    return classes_present

#Walks given path, returns contained java files
def get_java_files_in_path(path):
    files = []
    #Walk the target path along with subfolders
    for (dp, dn, fn) in walk(path):
        #Extract only .java files in the current path
        files.extend([dp + "\\" + f for f in fn if f[len(f)-5:] == ".java"])
    return files

#Parses given java file paths
def parse_java_files(files):
    parsed_java = []
    for file in files:
        try:
            #Read the file and try to parse the java code
            java = Path(file).read_text()
            parsed_java.append(
                {
                    "path": file,
                    "code": java,
                    "parse":  javalang.parse.parse(java)
                }
            )
        except:
            pass
    return parsed_java

#Given a relative path, makes it a absolute path using the location of the request orignator file
def relative_to_absolute(path, current_file):
    return str(Path(os.path.abspath(current_file)).parent) + "\\" + path 

#Write given data as json to the given path
def write_json(path, data):
    with open(path, "w+") as file:
        json.dump(data, file)

#Returns wheter the given path exists
def folder_exists(path):
    return os.path.exists(path)

#Gets a formated timestamp
def get_timestamp():
    return datetime.datetime.now().strftime('%H:%M:%S')

#Get console arguments
parser = argparse.ArgumentParser("Given path containing java files, calculates c3 value for the classes contained in them")
parser.add_argument("target", help="Absolute path containing targeted files", type=str)
args = parser.parse_args()

#Walk targeted path and parse java files from it
target_path = args.target
if folder_exists(target_path):
    java_files = get_java_files_in_path(target_path)
    print(get_timestamp(), ": parsing files")
    parsed_java = parse_java_files(java_files)
    print(get_timestamp(), ": parsed files")
    result_per_class = []
    #For each file
    for unit in parsed_java:
        #Get classes
        print(get_timestamp(), ": working on ", unit["path"])
        unit_classes = get_file_classes(unit["parse"])
        for c in unit_classes:
            #For each class calculate C3 metric
            result_per_class.append({"class":c["class"], "metric":c3(c["obj"], unit["code"])})

    #Write the results back to the targeted path
    write_json(target_path + "\\" + "c3_class.json", result_per_class)
else:
    print("Given a invalid path as target")

    
    