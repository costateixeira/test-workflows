#!/usr/bAin/env python3

import os
import glob as glob
import re
import pandas as pd
import sys
import getopt

class_cs = "http://smart.who.int/base/CodeSystem/CDHIv1"


def usage():
    print("Usage: scans input/system-requirements for excel sheets ")
    print("where the referenced excel contains a sheet entitled 'Non-functional'")
    print("and one entitled 'Functional' which contain the requirements.")
    print("The header row of the 'Non-functional' sheet should contain: ")
    print("   " , ', '.join(nonfunctional_headers))
    print("The header row of the 'Functional' sheet should contain: ")
    print("   " , ', '.join(nonfunctional_headers))
    print("OPTIONS:")
    print(" none")
    print("--help|h : print this information")
    sys.exit(2)


def main():
    try:
        opts,args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.GetoptError:
        usage()


    insert_aliases()    
    inputfile_names = glob.glob("input/system-requirements/*xlsx")
    print("Found the following files\n  " + "\n  ".join(inputfile_names) )

    resources = { 'requirements' : {} ,'codesystems' : {} , 'valuesets' : {} , 'actors' : {} }

    for inputfile_name in inputfile_names:
        try:
            extract_requirements_file_to_resources(inputfile_name,resources)
        except ValueError as e:
            print("Could not process: " +  inputfile_name + "\n" )
            print(f"\tError: {e}")

    for directory, instances in resources.items() :
        save_resources(instances,directory)
        
def insert_aliases():
    aliases = ['Alias: $pubStatus = http://hl7.org/fhir/publication-status',
               'Alias: $actorType = http://hl7.org/fhir/examplescenario-actor-type',
               'Alias: $SGActor = http://smart.who.int/base/StructureDefinition/SGActor',
               'Alias: $DHIClassificationv1 = http://smart.who.int/base/CodeSystem/DHIv1',
               'Alias: $DHIClassificationv2 = http://smart.who.int/base/CodeSystem/DHIv2'
               ]
    aliasfile = "input/fsh/Aliases.fsh"

    try:
        if not os.path.exists(aliasfile):
            with open(filename, 'w') as file:
                for alias in aliases:
                    print("Adding alias:" + alias)
                    file.write(alias + "\n")
                file.close()
        else:
            with open(aliasfile, 'r+') as file:
                content = file.read()
                print(content)
                for alias in aliases:
                    print("Checking alias:" + alias)
                    if alias not in content:
                        print("Adding alias:" + alias)
                        file.write('\n' + alias + '\n')
                file.close()
    except IOError as e:
        print("Could not insert aliases")
        print(f"\tError: {e}")
        
        
def save_resources(resources,directory):
    for id,resource in resources.items() :
        try:
            file = open("input/fsh/" + directory + "/" + id + ".fsh","w")
            print(resource,file=file)
            file.close()
        except IOError as e:
            print("Could not save resource of type: " + directory + "  with id: " + id + "\n")
            print(f"\tError: {e}")

# see https://www.youtube.com/watch?v=EnSu9hHGq5o&t=1184s&ab_channel=NextDayVideo
def generate_pairs_from_lists(lista,listb):
    for a in lista:
        for b in listb:
            yield a,b

def generate_pairs_from_column_maps(column_maps):
    for desired_column_name,possible_column_names in column_maps.items():
        for possible_column_name in possible_column_names:
            yield desired_column_name,possible_column_name

def retrieve_data_frame_by_headers(inputfile_name,column_maps,sheet_names):
    # sheet_names is an array of potential excel sheet names to look for data on
    #
    # example column_maps which has key the desired column name, value is an array of potential matching names
    # mathhing is case insensitive on alphanumeric, hyphen and .  with other characters ignored
    # functional_column_maps = {
    #     'reqid':["Requirement ID"],
    #     'activityid-and-name':["Activity ID and name", "Activity ID and description"],
    #     'as-a': ["As a"],
    #     'i-want': ["I want","I want to"],
    #     'so-that':["So that"]
    #     }

    print("Seeking the following input data columns ", column_maps)
    for sheet_name, header_row in generate_pairs_from_lists(sheet_names,[0,1,2]):
        print("\tChecking sheetname/header row #: " , sheet_name, "/", header_row)
        try:
            data_frame = pd.read_excel(inputfile_name, sheet_name=sheet_name, header=header_row)
        except Exception as e:
            print("Could not open sheet " + sheet_name + " on header row ", header_row)
            continue
        
        print("\tOpened sheet " + sheet_name +  " on header_row " , header_row, "\n\tReading columns: ",list(data_frame))    

        true_column_map = {} #this is where we will map current column names to canonicalized/normalied column names        
        for column in list(data_frame):
            print("\t\tLooking at data frame column: ",column)                    
            column_id = name_to_lower_id(column)
            print("\t\tLooking at data frame column id: ",column_id)                                
            #loop through potential names and try to match desired column
            for desired_column_name,possible_column_name in generate_pairs_from_column_maps(column_maps):
                possible_column_id = name_to_lower_id(possible_column_name)
                if (possible_column_id == column_id):
                    #we found what we needed
                    print("\t\tMatched input sheet column " + column + " with desired column " + desired_column_name)
                    true_column_map[column] =  desired_column_name

                                  
            if not column in true_column_map:
                #we dont need this input/source data frame column
                #we get rid of it to help normalize for downstream processing
                data_frame.drop(column,axis='columns', inplace=True)
                print("\t\tDropped: ",column)
                continue
                                  
        print("\tMapping the following columns: ",true_column_map)
        #normalize column names
        data_frame = data_frame.rename(columns=true_column_map)
        print("\tNormalized Data frame Columns:" , list(data_frame))
        if ( list(data_frame) != list(column_maps.keys()) ):
            print("\t\tIncorrect headers at ", header_row, " for data frame at " + sheet_name  + ".")
            print("\t\tReceived: ", list(data_frame))
            continue
                                       
        print("\tFound desired column headers at sheet name / header row: " , sheet_name, "/", header_row)
        #we are happy, return the data frame with normalized column names
        return data_frame

    #we tried all combinations and failed.
    return None
    

def extract_requirements_file_to_resources(inputfile_name,resources):
    functional_column_maps = {
        'reqid':["Requirement ID","Requirement"],
        'activityid-and-name':["Activity ID and name", "Activity ID and description"],
        'as-a': ["As a"],
        'i-want': ["I want","I want to"],
        'so-that':["So that"]
        }
    sheet_names = ['Functional']
    functional = retrieve_data_frame_by_headers(inputfile_name,functional_column_maps,sheet_names)
            
    if isinstance(functional,pd.DataFrame):
        if (not  extract_functional_requirements_to_resources(functional,resources)):
            print("Could not extract functional requirements from: " + inputfile_name)
            return False        
    else:
        print("Could not find functional requirements in:" + inputfile_name) 



    nonfunctional_column_maps ={
        'reqid':["Requirement","Requirement ID"],
        'category':["Category","Category ID"],
        'requirement':["Non-functional requirement","Non-functional requirements", "Nonfunctional requirements", "nonfunctional requirement"]
    }
    sheet_names = ['Non-Functional','Non-functional']
    nonfunctional = retrieve_data_frame_by_headers(inputfile_name,nonfunctional_column_maps,sheet_names)
        
    if isinstance(nonfunctional,pd.DataFrame):
        if (not  extract_nonfunctional_requirements_to_resources(nonfunctional,resources)):
            print("Could not extract non-functional requirements from: " + inputfile_name)
            return False        
    else:
        print("Could not find non-functional requirements in:" + inputfile_name)


    return True


        
  
def name_to_id(name):
    if ( not (isinstance(name,str))):
        return None
    return re.sub('[^0-9a-zA-Z\\-\\.]+', '', name)

def name_to_lower_id(name):
    if ( not (isinstance(name,str))):
        return None
    return re.sub('[^0-9a-zA-Z\\-\\.]+', '', name).lower()

def escape(input):
    if ( not (isinstance(input,str))):
        return None
    return input.replace('"', r'\"')


def generate_cs_and_vs_from_dict(id:str, title:str, dict:dict, resources:dict):
    if len(dict) == 0:
        return False
    
    codesystem = 'CodeSystem: ' + escape(id) + '\n'
    codesystem += 'Title: "' + escape(title) + '"\n'
    codesystem += 'Description:  "CodeSystem for ' + escape(title) + '. Autogenerated from DAK artifacts"\n'
    codesystem += '* ^experimental = true\n'
    codesystem += '* ^caseSensitive = false\n'
    codesystem += '* ^status = #active\n'
    for code,name in dict.items():
        codesystem += '* #' + escape(code) +  ' "' + escape(name) + '"\n'
        
    valueset = 'ValueSet: ' + escape(id) + '\n'
    valueset += 'Title: "' + escape(title) + '"\n'
    valueset += 'Description:  "Value Set for ' + escape(title) + '. Autogenerated from DAK artifacts"\n'
    valueset += '* ^status = #active\n'
    valueset += '* ^experimental = true\n'
    valueset += '* include codes from system ' + escape(id) + '\n'
    

    resources['codesystems'][id] = codesystem
    resources['valuesets'][id] = valueset

    return True



def extract_nonfunctional_requirements_to_resources(nonfunctional,resources):
    print("Reading non-functional requirements")
    nonfunctional.drop(index=0)

    categories={}
    cat_cs = 'FXREQCategories'
    classification = ""
    classification_codes = []

    for index, row in nonfunctional.iterrows():
        if not "reqid" in row or not isinstance(row["reqid"], str):
            print("// skipping row "+str(index+1)+": no reqid")
            continue
        reqid = name_to_id(row["reqid"])

        print("\tRow:\n" + "\t\t" + row.to_string().replace("\n", "\n\t\t"))


        #check if this is setting up the classifications
        if ( row["reqid"].strip().lower().startswith("classification of digital health interventions")):            
            classification = row["reqid"].strip()
            classification_codes = re.findall(r'\d+\.?\d*', classification )
            print("\tFound classification text: " + classification)
            print("\tFound classification codes: " , classification_codes)
            continue


        if not "category" in row or not isinstance(row["category"], str):
            print("// skipping row "+str(index+1)+": no category")
            continue        
        if not "requirement" in row or not isinstance(row["requirement"], str):
            print("// skipping row "+str(index+1)+": no requirement")
            continue        
        
        cat = row["category"].strip()
        catid = name_to_id(cat)
        categories[catid] = cat     #OK to overwrite existing
        
        nfreq = row["requirement"].strip()
        
        instance = "//non-functional requirment instance generated from row " + str(index+1) + "\n"
        instance += "Instance: " + reqid + "\n"
        instance += "InstanceOf: SGRequirements\n"
        instance += "Usage: #definition" + "\n"
        instance += '* title = "' + escape(nfreq) + '"\n'
        instance += '* status = $pubStatus#active\n'
        instance += '* name = "' + escape(nfreq) + '"\n'
        instance += '* publisher = "WHO"\n'
        instance += '* experimental = true\n'
        if (catid):
            instance += '* extension[classification].valueCoding[+] = ' + escape(cat_cs) + '#' + escape(catid) + '\n'
        for classification_code in classification_codes:
            instance += '* extension[classification].valueCoding[+] = ' + escape(class_cs) + '#' \
                + escape(classification_code) + '\n'
        description = '*Category*: ' + escape(cat) + "\n" +escape(nfreq)
        description = '* description = """\n' + description + '\n"""\n\n'
        instance += description + "\n"
        resources['requirements'][reqid] = instance        

    print("Extracted " + str(index) + " functional requirement(s)")

    generate_cs_and_vs_from_dict(cat_cs,'Functional Requirement Categories',categories,resources)
    return True


        

def extract_functional_requirements_to_resources(functional,resources):
    print("Reading functional requirements")
    businessprocess_code = ""
    businessprocess_name = ""
    businessprocess_codes = {}
    classification = ""
    classification_codes = []
    bpid = "FXREQBusinessProcesses"
    
    functional.drop(index=0)

    for index, row in functional.iterrows():
        if not "reqid" in row or not isinstance(row["reqid"], str):
            print("// skipping row "+str(index+1)+": no reqid")
            continue
        reqid = name_to_id(row["reqid"])

        print("\tRow:\n" + "\t\t" + row.to_string().replace("\n", "\n\t\t"))

        #check if this is setting up the classifications
        if ( row["reqid"].strip().lower().startswith("classification of digital health interventions")):            
            classification = row["reqid"].strip()
            classification_codes = re.findall(r'\d+\.?\d*', classification )
            print("\tFound classification text: " + classification)
            print("\tFound classification codes: " , classification_codes)
            continue

        if ( row["reqid"].strip().lower().startswith("business process")):
            businessprocess = row["reqid"].strip()[16:].strip()
            print("\tFound business process row " + str(index+1) +  ": "+ businessprocess)
            parts = businessprocess.split(":",2)
            if (len(parts) == 2):
                businessprocess_code = parts[0].strip()
                businessprocess_name = parts[1].strip()
                print("\tFound business process code (" + businessprocess_code + ") associated to " + businessprocess_name )
                businessprocess_codes[businessprocess_code] = businessprocess_name

        if (businessprocess_code):
            reqid = reqid + "." + businessprocess_code

        if not "activityid-and-name" in row or not isinstance(row["activityid-and-name"], str):
            print("\t*warning* skipping row "+str(index+1)+": no activityid-and-name")
            continue
        
        if not "as-a" in row or not isinstance(row["as-a"], str):
            print("\t*warning* skipping row "+str(index+1)+": no as-a")
            continue

        if not "i-want" in row or not isinstance(row["i-want"], str):
            print("\t*warning* skipping row "+str(index+1)+": no i-want")
            continue

        if not "so-that" in row or not isinstance(row["so-that"], str):
            print("\t*warning* skipping row "+str(index+1)+": no so-that")
            continue
        
            
        components = row["activityid-and-name"].split(".")
        activityid = ".".join(components[:-1])
        name = components[-1]

        actor_name = row["as-a"].strip()
        actor_id = name_to_lower_id(actor_name)
        actor_instance = "Instance: " + escape(actor_id) + "\n"
        actor_instance += "InstanceOf: $SGActor\n"
        actor_instance += "Usage: #definition\n"
        actor_instance += '* name = "' + escape(actor_name) + '"\n'
        actor_instance += '* title = "' + escape(actor_name) + '"\n'
        actor_instance += '* description = "Actor ' + escape(actor_name) + ' from Function Requirements"\n'
        actor_instance += '* status = $pubStatus#active\n'
        actor_instance += '* experimental = true\n'
        actor_instance += '* publisher = "WHO"\n'
        actor_instance += '* type = $actorType#person\n'        
        resources['actors'][actor_id] = actor_instance  # ok to overwrite      
        actorlink='<a href="ActorDefinition-' + escape(actor_id) + '.html">' + escape(actor_name) +'</a>'
        
        instance = "//functional requirment instance generated from row " + str(index+1) + "\n"
        instance += "Instance: " + escape(reqid) + "\n"
        instance += "InstanceOf: SGRequirements\n"
        instance += "Usage: #definition" + "\n"
        instance += '* title = "' + escape(row['i-want']) + '"\n'
        instance += '* status = $pubStatus#active\n'
        instance += '* name = "' + escape(row['i-want']) + '"\n'
        instance += '* publisher = "WHO"\n'
        instance += '* experimental = true\n'
        instance += '* actor[+] = Canonical(' + escape(actor_id) + ')\n'
        if (businessprocess_code):
            instance += '* extension[classification].valueCoding[+] = ' + bpid + '#' + escape(businessprocess_code) + '\n'
        for classification_code in classification_codes:
            instance += '* extension[classification].valueCoding[+] = ' + escape(class_cs) + '#' \
                + escape(classification_code) + '\n'
        instance += '* extension[userstory].extension[capability].valueString = "' + escape(row['i-want']) + '"\n'
        instance += '* extension[userstory].extension[benefit].valueString = "' + escape(row['so-that']) + '"\n'
        description = "As a " + actorlink + ", I want to:\n>" + escape(row['i-want']) + '\n\nso that\n\n>' + escape(row['so-that'])
        if (businessprocess_name):
            if (businessprocess_code):
                description = "*Business process* (" + escape(businessprocess_code) + ") "  \
                    + escape(businessprocess_name) + ":\n" + description
            else:
                description = "*Business process* "  + escape(businessprocess_name) + ":\n\n" + description
        description = '* description = """\n' + description + '\n"""\n\n'
        instance += description + "\n"
        resources['requirements'][reqid] = instance
        
    print("Extracted " + str(index) + " functional requirement(s)")
    print("Business Process Codes:\n\t" , businessprocess_codes)
    generate_cs_and_vs_from_dict(bpid,'Functional Requirements Business Processes',businessprocess_codes,resources)
    return True


main()

