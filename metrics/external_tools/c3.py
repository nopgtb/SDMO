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

#Create co occurance matrix from the words. How many times did each word occur with its pair in the context?
def create_co_occurance_matrix(m_words, all_words):
    #Each array (variable/comment) in the words is treated as its own context window
    single_dim_uniq_words = list(set([w for c in all_words for w in c]))
    word_mat_map = {w:i for i,w in enumerate(single_dim_uniq_words)}
    word_count = len(single_dim_uniq_words)
    #word_count * word_count zero matrix
    co_occurance = np.zeros((word_count, word_count), dtype=np.int32)
    #Loop trough each context
    for context in m_words:
        #Loop trough each word in context
        for word_1 in context:
        #Loop trough the same context again and set values in 
            for word_2 in context:
                #Ignore word itself
                if not word_1 == word_2:
                    row = word_mat_map[word_1]
                    column = word_mat_map[word_2]
                    co_occurance[row, column] = co_occurance[row, column] + 1
    #word_count * word_count co_occurance matrix
    return co_occurance

#Calculates svd and reduction for the given matrix
def svd(co_occurance_matrix):
    k = 3
    #Calculate svd
    U, S, Vh = np.linalg.svd(co_occurance_matrix)
    #Turn s into a diag matrix
    s_diag = np.zeros(co_occurance_matrix.shape)
    np.fill_diagonal(s_diag, S)
    #Reduce the svd output
    u_k = U[:, :k],
    s_k = s_diag[:k, :k]
    vh_k = Vh[:k, :]
    #Reconstruct reduced matrix
    #Approximates the orignal while capturing significant features in reduced state
    return np.dot(u_k, np.dot(s_k, vh_k))

#Calculates the cosine similarity of the two given lsi values
def cms(lsi1, lsi2):
    #Flatten to vector
    lsi1 = lsi1.flatten()
    lsi2 = lsi2.flatten()
    #Calculate norms
    lsi1_norm = np.linalg.norm(lsi1)
    lsi2_norm = np.linalg.norm(lsi2)
    #Avoid div by 0
    if not lsi1_norm == 0 and not lsi2_norm == 0:
        return np.dot(lsi1, lsi2) / (lsi1_norm * lsi2_norm)
    return 0.0

#Calculates the LSI value for the given words
def lsi(m_words, all_words):
    #Create co-occurance matrix from the given words
    co_occurance_matrix = create_co_occurance_matrix(m_words, all_words)
    #Reduce using svd
    svd_reduced = svd(co_occurance_matrix)
    return svd_reduced

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
    for m in methods:
        m["lsi_value"] = lsi(m["words"], all_words)

    #Calculate cosine similarity for each method LSI pair
    for i, lsi1 in enumerate(methods):
        for j, lsi2 in enumerate(methods):
            if not i == j:
                #non diagonial pairs only
                cms_values.append(cms(lsi1["lsi_value"], lsi2["lsi_value"]))
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

#Get console arguments
parser = argparse.ArgumentParser("Given path containing java files, calculates c3 value for the classes contained in them")
parser.add_argument("target", help="Absolute path containing targeted files", type=str)
args = parser.parse_args()

#Walk targeted path and parse java files from it
target_path = args.target
if folder_exists(target_path):
    java_files = get_java_files_in_path(target_path)
    parsed_java = parse_java_files(java_files)

    result_per_class = []
    #For each file
    for unit in parsed_java:
        #Get classes
        unit_classes = get_file_classes(unit["parse"])
        for c in unit_classes:
            #For each class calculate C3 metric
            result_per_class.append({"class":c["class"], "metric":c3(c["obj"], unit["code"])})

    #Write the results back to the targeted path
    write_json(target_path + "\\" + "c3_class.json", result_per_class)
else:
    print("Given a invalid path as target")

    
    