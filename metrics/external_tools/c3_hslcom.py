
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

#Implements the calculation of metric C3
#Implementation based on the description provided at https://github.com/cqfn/jpeek/blob/master/src/main/resources/org/jpeek/metrics/C3.xsl#L32
class C3:

    #Splits CamelCase and vars_seperated_using a _ into individual words
    @staticmethod
    def split_name(name):
        words = []
        #Handle words seperated using _
        for part in name.split("_"):
            #Handle camelcase
            words.extend(re.findall(r'[A-Za-z][a-z]*|[a-z]+', part))
        return words

    #Given a function fetches all variable names
    def get_method_variable_names(m, class_variables):
        names = []
        #Parameters
        for var in m.parameters:
            if isinstance(var, javalang.tree.FormalParameter) or isinstance(var, javalang.tree.TypeParameter):
                names.extend(C3.split_name(var.name))
        #Local vars
        if m.body:
            for var in m.body:
                if isinstance(var, javalang.tree.LocalVariableDeclaration):
                    for dc in var.declarators:
                        names.extend(C3.split_name(dc.name))
        #Class variables accesed
        class_variables_accessed = Util.member_variables_used_in_method(class_variables, m)
        for c_var in class_variables_accessed:
            names.extend(C3.split_name(c_var))
        return names

    #Removes every non word element from the comment
    @staticmethod
    def split_comment(comment):
        comment = re.sub(r'[^a-zA-Z0-9\s]', '', comment)
        return comment.split()
    
    #Returns words present in comments found in the methods code
    @staticmethod
    def get_method_comments(m, code):
        words = []
        #Javadoc
        if m.documentation:
            words.extend(C3.split_comment(m.documentation))
        #Local comments
        comments = re.findall(r'(//.*?$)|(/\*.*?\*/)', code, re.DOTALL|re.MULTILINE)
        for comment in comments:
            mutlipart_context = []
            #Process possible multilines and keep them in same context
            if not isinstance(comment, str):
                for comment_part in comment:
                    mutlipart_context.extend(C3.split_comment(comment_part))
            else:
                mutlipart_context.extend(C3.split_comment(comment))
            #Append the context to the words list
            words.extend(mutlipart_context)
        return words

    #Retrieves words present in the method
    @staticmethod
    def get_words_with_context(m, code, class_variables):
        words = []
        #Function name
        #words.append(split_name(m.name))
        #Get variable name words
        words.extend(C3.get_method_variable_names(m, class_variables))
        #Get words from comments associated with the method
        words.extend(C3.get_method_comments(m, code))
        #lower case all words and return them
        return [w.lower() for w in words]

    #Create co occurance matrix from the words. How many times did each word occur with its pair in the context?
    @staticmethod
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
    @staticmethod
    def svd(co_occurance_matrix, truncsvd):
        return truncsvd.fit_transform(co_occurance_matrix)

    #Calculates the LSI value for the given words
    @staticmethod
    def lsi(m_words, word_map, unique_word_count, truncsvd):
        #Create co-occurance matrix from the given words
        co_occurance_matrix = C3.create_co_occurance_matrix(m_words, word_map, unique_word_count)
        #Reduce using svd
        if np.max(co_occurance_matrix) > 0:
            #If max is 0 svd will error
            svd_reduced = C3.svd(co_occurance_matrix, truncsvd)
            return svd_reduced
        return None

    #Combines the LSI values of the methods into single matrix
    @staticmethod
    def combine_methods(methods):
        #Get all LSI values shaped as 2D array in one matrix
        lsi_array = [m["lsi_value"].reshape(1,-1) for m in methods if isinstance(m["lsi_value"], np.ndarray)]
        if lsi_array:
            return np.vstack(lsi_array)
        return None

    #Calculates the average cms value of the class
    @staticmethod
    def acsm(c, code):
        #Get methods present in class
        methods = Util.get_class_methods(c, code)
        #Cant compare one method
        if len(methods) > 1:
            #Get words from the methods
            all_words = []
            class_variables = Util.get_class_variables(c)
            for m in methods:
                #Get the words and their context from the method
                m["words"] = C3.get_words_with_context(m["m"], m["code"], class_variables)
                #Append the method words to the all words 
                all_words.extend(m["words"])

            #Calculate word matrix dimensions and a word => mat map
            single_dim_uniq_words = list(set(all_words))
            min_dimensions = 3
            #We need atleast 3 words total
            if len(single_dim_uniq_words) >= min_dimensions:
                word_map = {w:i for i,w in enumerate(single_dim_uniq_words)}
                word_count = len(single_dim_uniq_words)
                truncsvd = TruncatedSVD(n_components=min_dimensions)
                for m in methods:
                    m["lsi_value"] = C3.lsi(m["words"], word_map, word_count, truncsvd)
                #Combine LSIs into single matrix
                lsi_matrix = C3.combine_methods(methods)
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
        return None

    #Calculates the c3 value for the given class
    @staticmethod
    def c3(c, code):
        val = C3.acsm(c, code)
        if not val == None:
            if val > 0:
                return val
            return 0
        return None

#Calculates metric HsLCOM
#Based on this https://eclipse-metrics.sourceforge.net/descriptions/pages/cohesion/HendersonSellers.html
#M = Number of methods
#F = Set of class member variables
#avgMF = Average number of methods accessing member variables
#HSLCOM = (avgMF - M) / (1 - M)
class HSLCOM:

    #Runs the hslcom metric on the given class
    @staticmethod
    def hslcom(c, code):
        #F
        class_variables = Util.get_class_variables(c)
        #M
        class_methods = Util.get_class_methods(c, code)
        if class_variables and class_methods and not len(class_methods) == 1:
            #Get possible variable names in the methods
            class_variables_accessed = 0
            for method in class_methods:
                member_variables_accesed = Util.member_variables_used_in_method(class_variables, method["m"])
                class_variables_accessed = class_variables_accessed + len(member_variables_accesed)
            #avgMF
            class_variables_accessed_avg = class_variables_accessed / len(class_variables)
            return (class_variables_accessed_avg - len(class_methods)) / (1 - len(class_methods))
        return None

#Common utility for the metrics
class Util:

    #Given variables and methods, returns set of methods that access the given variable
    @staticmethod
    def member_variables_used_in_method(member_variables, method):
        variables_used = []
        if method.body:
            variables_in_method = []
            #Get variable names seen in method
            variables_in_method = []
            for statement in method.body:
                 Util.findVariablesInTree(statement, variables_in_method)
            #Get variables used in method
            for member_variable in member_variables:
                if member_variable in variables_in_method:
                    variables_used.append(member_variable)
        return variables_used

    #Given a class, retrieves all its member variables
    @staticmethod
    def get_class_variables(c):
        class_variables = []
        if c.body:
            for member in c.body:
                if isinstance(member, javalang.tree.FieldDeclaration):
                    for var in member.declarators:
                        class_variables.append(var.name)
        return class_variables

    #Recursive function that finds variables in the javalang tree
    @staticmethod
    def findVariablesInTree(tree, variables_found):
        if tree:
            if hasattr(tree, "children"):
                #Travel the children
                for child in tree.children:
                    if child: 
                        if not isinstance(child, (tuple, list, set)):
                            Util.findVariablesInTree(child, variables_found)
                        else:
                            for sub_child in child:
                                if sub_child:
                                    Util.findVariablesInTree(sub_child, variables_found)
            variable_indicators = ["member", "name", "qualifier"]
            #Look for variables
            for indicator in variable_indicators:
                if hasattr(tree, indicator):
                    variables_found.append(getattr(tree, indicator))
            return variables_found

    @staticmethod

    #Walks given path, returns contained java files
    @staticmethod
    def get_java_files_in_path(path):
        files = []
        #Walk the target path along with subfolders
        for (dp, dn, fn) in walk(path):
            #Extract only .java files in the current path
            files.extend([dp + "\\" + f for f in fn if f[len(f)-5:] == ".java"])
        return files

    #Parses given java file paths
    @staticmethod
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

    #Traverses the given parsed tree and returns present classes
    @staticmethod
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

    #Retrives methods present in the class and their raw source code
    @staticmethod
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

    #Returns wheter the given path exists
    @staticmethod
    def folder_exists(path):
        return os.path.exists(path)

    #Write given data as json to the given path
    @staticmethod
    def write_json(path, data):
        with open(path, "w+") as file:
            json.dump(data, file)
            
    #Gets a formated timestamp
    @staticmethod
    def get_timestamp():
        return datetime.datetime.now().strftime('%H:%M:%S')

#Get console arguments
parser = argparse.ArgumentParser("Given path containing java files, calculates c3 value for the classes contained in them")
parser.add_argument("target", help="Absolute path containing targeted files", type=str)
args = parser.parse_args()

#Walk targeted path and parse java files from it
target_path = args.target
if Util.folder_exists(target_path):
    java_files = Util.get_java_files_in_path(target_path)
    print(Util.get_timestamp(), ": parsing files")
    parsed_java = Util.parse_java_files(java_files)
    print(Util.get_timestamp(), ": parsed files")
    result_per_class = []
    #For each file
    for unit in parsed_java:
        #Get classes
        print(Util.get_timestamp(), ": working on ", unit["path"])
        unit_classes = Util.get_file_classes(unit["parse"])
        for c in unit_classes:
            #For each class calculate C3 metric
            result_per_class.append(
                {
                    "class":c["class"], 
                    "metric_c3":C3.c3(c["obj"], unit["code"]), 
                    "metric_hslcom":HSLCOM.hslcom(c["obj"], unit["code"])
                }
            )

    #Write the results back to the targeted path
    Util.write_json(target_path + "\\" + "c3_hslcom_class.json", result_per_class)
else:
    print("Given a invalid path as target")

    
    