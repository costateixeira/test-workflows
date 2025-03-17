#!/usr/bin/env python3

import glob as glob
import re
# import pandas lib as pd
import pandas as pd
#import string
import sys
import getopt



nonfunctional_headers = ["Requirement ID","Category","Non-functional requirement"]
functional_headers = ["Requirement ID","Activity ID and name","As a…","I want…","So that…"]

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

    functional_file = open("input/fsh/requirements/Functional-Requirements.fsh",'w')
    nonfunctional_file = open("input/fsh/requirements/NonFunctional-Requirements.fsh",'w')
    inputfile_names = glob.glob("input/system-requirements/*xlsx")
    print("Found the following files\n  " + "\n  ".join(inputfile_names) )
    for inputfile_name in inputfile_names:
        try:
            extract_file(inputfile_name,functional_file,nonfunctional_file)
        except ValueError as e:
            print("Could not process: " +  inputfile_name + "\n" )
            print(f"\tError: {e}")
        
    functional_file.close()
    nonfunctional_file.close()


def extract_file(inputfile_name,functional_file,nonfunctional_file):
    print("Examining file: " + inputfile_name)
    try:
        functional = pd.read_excel(inputfile_name, sheet_name='Functional')
        nonfunctional = pd.read_excel(inputfile_name, sheet_name='Non-functional')
    except IOError as e:
        print("Sheets not found or processable:" + inputfile_name + "...aborting")
        print(f"\tError: {e}")
        return False
    
    if ( list(nonfunctional) != nonfunctional_headers):
        print("Incorrect headers for Non-functional requirements.  Expecting: " , ', '.join(nonfunctional_headers))
        print("Received: ", ", ".join(list(nonfunctional)))
        return False
    if ( list(functional) != functional_headers):
        print("Incorrect headers for Non-functional requirements.  Expecting: " , ', '.join(nonfunctional_headers))
        print("Received: ", ", ".join(list(functional)))
        return False

    r = True
    if (not extract_functional(functional,functional_file)):
        print("Could not extract non-functional requirements from: " + inputfile_name )
        r = False
    if (not extract_nonfunctional(nonfunctional,nonfunctional_file)):
        print("Could not extract non-functional requirements from: " + inputfile_name)
        r = False
    return r

  
def name_to_id(name):
    return re.sub('[^0-9a-zA-Z]+', '', name)

def escape(str):
    return str.replace('"', r'\"')


def extract_nonfunctional(nonfunctional,nonfunctional_file):
    print("Reading non-functional requirements")
    return False

def extract_functional(functional,functional_file):
    print("Reading functional requirements")
    businessprocess = False
    functional.drop(index=0) 
    for index, row in functional.iterrows():
        reqid = name_to_id(row["Requirement ID"])
        if (pd.isnull(reqid)):
            print("// skipping row "+str(index+1)+": no reqid", file=functional_file)
            continue
        activityid_and_name = row["Activity ID and name"]
        # check if this is a business process:
        if ( pd.isnull(activityid_and_name ) and reqid[:16] == "Business process"):
            businessprocess = reqid[16:]
            print("// Found business process row " + str(index+1) +  ": "+ businessprocess ,file=functional_file)
            continue
        if (pd.isnull(activityid_and_name)):
            print("// skipping row "+ str(index +1) + ": no activity id",file=functional_file)
            continue
        
        components = activityid_and_name.split(".")
        activityid = ".".join(components[:-1])
        name = components[-1]
        asa = row["As a…"]
        iwant = row["I want…"]
        sothat = row["So that…"]
        actorlink='<a href="ActorDefinition-' + name_to_id(asa) + '.html">' + escape(asa) +'</a>'
        instance = "//functional requirment instance generated from row " + str(index+1) + "\n"
        instance += "Instance: " + reqid + "\n"
        instance += "InstanceOf: SGRequirements\n"
        instance += "Usage: #definition" + "\n"
        instance += '* title = "' + escape(iwant) + '"\n'
        instance += '* status = $pubStatus#active\n'
        instance += '* name = "' + escape(iwant) + '"\n'
        instance += '* publisher = "WHO"\n'
        instance += '* experimental = true\n'
        instance += '* extension[userstory].extension[capability].valueString = "' + escape(iwant) + '"\n'
        instance += '* extension[userstory].extension[benefit].valueString = "' + escape(sothat) + '"\n'
        description = "As a " + actorlink + ", I want:\n>" + escape(iwant) + '\n\nso that\n\n>' + escape(sothat)
        if (businessprocess):
            description = "Under the business process " + businessprocess + ":\n" + description
        description = '* description = """\n' + description + '\n"""\n\n'
        instance += description + "\n"
        print(instance + "\n" ,file=functional_file)
    print("Extracted " + str(index) + " functional requirement(s)")
    return True

main()

