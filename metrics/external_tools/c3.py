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
    #Each array (variable/comment) in the words is treated as its own context window
    #unique_word_count * unique_word_count zero matrix
    co_occurance = np.zeros((unique_word_count, unique_word_count), dtype=np.int32)
    #Loop trough each context
    for context in m_words:
        #Loop trough each word in context
        word_counts = {}
        #Findout how many times did each word occur
        for word in context:
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

#Calculates the cosine similarity of the two given lsi values
def cms(lsi1, lsi2):
    cs = cosine_similarity(lsi1.reshape(1,-1), lsi2.reshape(1,-1))
    if cs[0,0] > 0:
        return cs[0,0]
    return 0

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
            names.append(split_name(var.name))
    #Local vars
    if m.body:
        for var in m.body:
            if isinstance(var, javalang.tree.LocalVariableDeclaration):
                for dc in var.declarators:
                    names.append(split_name(dc.name))
    return names

#Removes every non word element from the comment
def split_comment(comment):
    comment = re.sub(r'[^a-zA-Z0-9\s]', '', comment)
    return comment.split()

def get_method_comments(m, code):
    words = []
    #Javadoc
    if m.documentation:
        words.append(split_comment(m.documentation))
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
        words.append(mutlipart_context)
    return words

#Retrieves words present in the method
def get_words_with_context(m, code):
    words = []
    #Function name
    words.append(split_name(m.name))
    #Get variable name words
    words.extend(get_method_variable_names(m))
    #Get words from comments associated with the method
    words.extend(get_method_comments(m, code))
    #lower case all words and return them
    return [[w.lower() for w in c] for c in words]

#Retrives methods present in the class and their raw source code
def get_class_methods(c, code):
    methods = []
    #Get all methods from the parsed tree
    for item in c.body:
        if isinstance(item, javalang.tree.MethodDeclaration):
            methods.append({"m":item, "code": ""})

    #Retrieve the raw code for the method
    code_split = code.splitlines()
    brackets = 0
    for m in methods:
        #approximate the raw code block for the method
        method_code = code_split[m["m"].position.line-1:]
        entered_func = False
        #Using brackets get the accurate raw code block
        for i,l in enumerate(method_code):
            brackets = brackets + l.count("{")
            #Have we entered the function?
            entered_func = entered_func or brackets > 0
            if entered_func:
                brackets = brackets - l.count("}")
                #Have we exited the function?
                if brackets == 0:
                    method_code = method_code[:i+1]
                    break
        #Assign the raw code block to the method
        m["code"] = "\n".join(method_code)
    return methods

#Calculates the average cms value of the class
def acsm(c, code):
    #Get methods present in class
    methods = get_class_methods(c, code)
    #Get words from the methods
    all_words = []
    for m in methods:
        #Get the words and their context from the method
        m["words"] = get_words_with_context(m["m"], m["code"])
        #Append the method words to the all words 
        all_words.extend(m["words"])
    #Pre calculate LSI value for each method in class
    cms_values = []
    min_dimensions = 3
    #We need atleast 3 words total
    if len(all_words) >= min_dimensions:
        #Calculate word matrix dimensions and a word => mat map
        single_dim_uniq_words = list(set([w for c in all_words for w in c]))
        word_map = {w:i for i,w in enumerate(single_dim_uniq_words)}
        word_count = len(single_dim_uniq_words)
        truncsvd = TruncatedSVD(n_components=min_dimensions)
        for m in methods:
            m["lsi_value"] = lsi(m["words"], word_map, word_count, truncsvd)

        method_1 = 0
        method_2 = 0
        #Roll trough LSI pairs once calculating cms
        #Dot(a,b) == Dot(b,a) 
        #Average wont be affected by missing extra pair of same values
        while method_1 < len(methods) -1:
            method_2 = (method_1 + 1)
            while method_2 < len(methods):
                if isinstance(methods[method_1]["lsi_value"], np.ndarray) and isinstance(methods[method_2]["lsi_value"], np.ndarray):
                    cms_values.append(cms(methods[method_1]["lsi_value"], methods[method_2]["lsi_value"]))
                method_2 = method_2 + 1
            method_1 = method_1 + 1
        #If we have cms values
        if cms_values:
            #Return the average cms value
            return sum(cms_values) / len(cms_values)
    return 0

#Calculates the c3 value for the given class
def c3(c, code):
    return acsm(c, code)

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

    
    