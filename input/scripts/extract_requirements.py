#!/usr/bin/env python3

import os
import glob as glob
import re
import pandas as pd
import sys
import getopt




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
               'Alias: $SGActor = http://smart.who.int/base/StructureDefinition/SGActor'
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
        'reqid':["Requirement ID"],
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
        'reqid':["Requirement"],
        'category':["Category"],
        'requirement':["Non-functional requirement","Non-functional requirements"]
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


def extract_value(keys,row):
    val = None
    for key in keys:
        if ( key in row):
            print("Found " , key)
            val = row[key]
            
    if ( val == None):
        print("Could not find desired key in list: ", ",".join(keys),"\namong: ", row.keys())
        
    return val




def extract_nonfunctional_requirements_to_resources(nonfunctional,resources):
    print("Reading non-functional requirements")
    nonfunctional.drop(index=0)

    categories={}

    for index, row in nonfunctional.iterrows():
        reqid = name_to_id(row["reqid"])
        if (pd.isnull(reqid)):
            print("// skipping row "+str(index+1)+": no reqid")
            continue

        cat = extract_value(["Category"],row)
        catid = name_to_id(cat)
        if ( not isinstance(cat, str)):
            print("Could not find 'Category' in: ",row.keys())
            continue
        categories[catid] = cat     #OK to overwrite existing
        
        nfreq = extract_value(["Non-functional requirement"],row)
        if ( not isinstance(cat, str)):
            print("Could not find 'Non-functional requirement' in: ",row.keys())
            continue
        
        reqid = name_to_id(row["Requirement ID"])
        instance = "//non-functional requirment instance generated from row " + str(index+1) + "\n"
        instance += "Instance: " + reqid + "\n"
        instance += "InstanceOf: SGRequirements\n"
        instance += "Usage: #definition" + "\n"
        instance += '* title = "' + escape(nfreq) + '"\n'
        instance += '* status = $pubStatus#active\n'
        instance += '* name = "' + escape(nfreq) + '"\n'
        instance += '* publisher = "WHO"\n'
        instance += '* experimental = true\n'
        description = '*Category*: ' + escape(cat) + "\n" +escape(nfreq)
        description = '* description = """\n' + description + '\n"""\n\n'
        instance += description + "\n"
        resources['requirements'][reqid] = instance        
        print(instance)
    print("Extracted " + str(index) + " functional requirement(s)")
    
    if ( len(categories) > 0 ):
        csid = 'FunctionalRequimentCategories'
        codesystem = 'CodeSystem: ' + csid + '\n'
        codesystem += 'Title: "Functional Requirement Categories"\n'
        codesystem += 'Description:  "CodeSystem for Functional Requirements Categories.  Autogenerated from DAK artifacts"\n'
        codesystem += '* ^experimental = true\n'
        codesystem += '* ^caseSensitive = false\n'
        codesystem += '* ^status = #active\n'
        for catid,cat in categories.items():
            codesystem += '* #' + catid +  ' "' + cat + '"\n'

        valueset = 'ValueSet: ' + csid + '\n'
        valueset += 'Title: "Functional Requirement Categories"\n'
        valueset += 'Description:  "Value Set for Functional Requirements Categories. Autogenerated from DAK artifacts"\n'
        valueset += '* ^status = #active\n'
        valueset += '* ^experimental = true\n'
        valueset += '* include codes from system ' + csid + '\n'


        resources['codesystems'][csid] = codesystem
        resources['valuesets'][csid] = valueset

    return True
        

def extract_functional_requirements_to_resources(functional,resources):
    print("Reading functional requirements")
    businessprocess_code = ""
    businessprocess_name = ""
    businessprocess_codes = {}
    classification = ""
    classification_codes = []
    functional.drop(index=0)

    for index, row in functional.iterrows():
        if not isinstance(row["reqid"], str):
            print("// skipping row "+str(index+1)+": no reqid")
            continue
        reqid = name_to_id(row["reqid"])

        print("\tRow:\n" + "\t\t" + row.to_string().replace("\n", "\n\t\t"))

        #check if this is setting up the classifications
        if ( row["reqid"].strip().lower().startswith("classification of digital health interventions")):            
            classification = row["reqid"].strip()
            classifications = re.findall(r'\d+\.?\d*', classification )
            print("\tFound classification text: " + classification)
            print("\tFound classification codes: " , classifications)
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
            reqid = businessprocess_code + "." + reqid

        if not isinstance(row["activityid-and-name"], str):
            print("\t*warning* skipping row "+str(index+1)+": no activityid-and-name")
            continue
        
        if not isinstance(row["as-a"], str):
            print("\t*warning* skipping row "+str(index+1)+": no as-a")
            continue

        if not isinstance(row["i-want"], str):
            print("\t*warning* skipping row "+str(index+1)+": no i-want")
            continue

        if not isinstance(row["so-that"], str):
            print("\t*warning* skipping row "+str(index+1)+": no so-that")
            continue
        
            
        components = row["activityid-and-name"].split(".")
        activityid = ".".join(components[:-1])
        name = components[-1]

        actor_name = row["as-a"].strip()
        actor_id = name_to_lower_id(actor_name)
        actor_instance = "Instance: " + actor_id + "\n"
        actor_instance += "InstanceOf: $SGActor\n"
        actor_instance += "Usage: #definition\n"
        actor_instance += '* name = "' + escape(actor_name) + '"\n'
        actor_instance += '* title = "' + escape(actor_name) + '"\n'
        actor_instance += '* description = "Actor ' + escape(actor_name) + ' from Function Requirements"\n'
        actor_instance += '* status = $pubStatus#active\n'
        actor_instance += '* experimental = true\n'
        actor_instance += '* publisher = "WHO"\n'
        actor_instance += '* type = $actorType#individual\n'        
        resources['actors'][actor_id] = actor_instance        
        actorlink='<a href="ActorDefinition-' + actor_id + '.html">' + actor_name +'</a>'
        
        instance = "//functional requirment instance generated from row " + str(index+1) + "\n"
        instance += "Instance: " + reqid + "\n"
        instance += "InstanceOf: SGRequirements\n"
        instance += "Usage: #definition" + "\n"
        instance += '* title = "' + escape(row['i-want']) + '"\n'
        instance += '* status = $pubStatus#active\n'
        instance += '* name = "' + escape(row['i-want']) + '"\n'
        instance += '* publisher = "WHO"\n'
        instance += '* experimental = true\n'
        instance += '* extension[userstory].extension[capability].valueString = "' + escape(row['i-want']) + '"\n'
        instance += '* extension[userstory].extension[benefit].valueString = "' + escape(row['so-that']) + '"\n'
        description = "I want " + actorlink + ", I want:\n>" + escape(row['i-want']) + '\n\nso that\n\n>' + escape(row['so-that'])
        if (businessprocess_name):
            if (businessprocess_code):
                description = "Under the business process (" + businessprocess_code + ") "  + businessprocess_name + ":\n" + description                
            else:
                description = "Under the business process"  + businessprocess_name + ":\n" + description
        description = '* description = """\n' + description + '\n"""\n\n'
        instance += description + "\n"
        resources['requirements'][reqid] = instance
        
    print("Extracted " + str(index) + " functional requirement(s)")
    print("Business Process Codes:\n\t" , businessprocess_codes)    
    if (len(businessprocess_codes) > 0):
        bpid = "BPFXREQ"
        businessprocess_cs = "CodeSystem: " + bpid + "\n"
        businessprocess_cs += 'Title: "Functional Requirements - Business Process"\n'
        businessprocess_cs += 'Description: "ValueSet of Functional Requirements - Business Process"\n'
        businessprocess_cs += '* ^status = #active\n'
        businessprocess_cs += '* ^experimental = true\n'
        resources['codesystems'][bpid] = businessprocess_cs
        
        businessprocess_vs = "ValueSet: " + bpid + "\n"
        businessprocess_vs += 'Title: "Functional Requirements - Business Process"\n'
        businessprocess_vs += 'Description: "ValueSet of Functional Requirements - Business Process"\n'
        businessprocess_vs += '* ^status = #active\n'
        businessprocess_vs += '* ^experimental = true\n'
        businessprocess_vs += '* include codes from system ' + bpid + '\n'
        resources['valuesets'][bpid] = businessprocess_vs
    return True


main()

