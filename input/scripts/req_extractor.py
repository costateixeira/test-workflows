import os
import glob
import re
import pandas as pd

from extractor import extractor 
from installer import installer

class req_extractor(extractor):

  def __init__(self,installer:installer):
    super().__init__(installer)

  def find_files(self):
      return glob.glob("input/system-requirements/*xlsx")


  # def usage():
  #   print("Usage: scans input/system-requirements for excel sheets ")
  #   print("where the referenced excel contains a sheet entitled 'Non-functional'")
  #   print("and one entitled 'Functional' which contain the requirements.")
  #   print("The header row of the 'Non-functional' sheet should contain: ")
  #   print("   " , ', '.join(nonfunctional_headers))
  #   print("The header row of the 'Functional' sheet should contain: ")
  #   print("   " , ', '.join(nonfunctional_headers))
  #   print("OPTIONS:")
  #   print(" none")
  #   print("--help|h : print this information")
  #   sys.exit(2)

  def get_aliases(self):
      return ['Alias: $pubStatus = http://hl7.org/fhir/publication-status',
               'Alias: $actorType = http://hl7.org/fhir/examplescenario-actor-type',
               'Alias: $SGActor = http://smart.who.int/base/StructureDefinition/SGActor',
               'Alias: $DHIClassificationv1 = http://smart.who.int/base/CodeSystem/DHIv1',
               'Alias: $DHIClassificationv2 = http://smart.who.int/base/CodeSystem/DHIv2'
               ]

  def extract_file(self):
    try: 
      self.extract_resources()
    except ValueError as e:
      logging.getLogger(self.__class__.__name__).info("Could not process: " +  self.inputfile_name + "\n" )
      logging.getLogger(self.__class__.__name__).info(f"\tError: {e}")
    
  
  def extract_resources(self):
    functional_column_maps = {
        'reqid':["Requirement ID","Requirement"],
        'activityid-and-name':["Activity ID and name", "Activity ID and description"],
        'as-a': ["As a"],
        'i-want': ["I want","I want to"],
        'so-that':["So that"]
        }
    sheet_names = ['Functional']
    functional = self.retrieve_data_frame_by_headers(functional_column_maps,sheet_names)
            
    if (not  self.extract_functional_requirements(functional)):
      logging.getLogger(self.__class__.__name__).info("Could not extract functional requirements from: " + self.inputfile_name)
      return False        
    else:
        logging.getLogger(self.__class__.__name__).info("Could not find functional requirements in:" + self.inputfile_name) 



    nonfunctional_column_maps ={
        'reqid':["Requirement","Requirement ID"],
        'category':["Category","Category ID"],
        'requirement':["Non-functional requirement","Non-functional requirements", "Nonfunctional requirements", "nonfunctional requirement"]
    }
    sheet_names = ['Non-Functional','Non-functional']
    nonfunctional = self.retrieve_data_frame_by_headers(nonfunctional_column_maps,sheet_names)
        
    if (not  self.extract_nonfunctional_requirements_to_resources(nonfunctional)):
      logging.getLogger(self.__class__.__name__).info("Could not extract non-functional requirements from: " + self.inputfile_name)
      return False        
    else:
      logging.getLogger(self.__class__.__name__).info("Could not find non-functional requirements in:" + self.inputfile_name)

    return True


        

  def extract_nonfunctional_requirements_to_resources(nonfunctional:pd.DataFrame ):
    logging.getLogger(self.__class__.__name__).info("Reading non-functional requirements")
    nonfunctional.drop(index=0)

    categories={}
    cat_cs = 'FXREQCategories'
    classification = ""
    classification_codes = []

    for index, row in nonfunctional.iterrows():
        if not "reqid" in row or not isinstance(row["reqid"], str):
            logging.getLogger(self.__class__.__name__).info("// skipping row "+str(index+1)+": no reqid")
            continue
        reqid = stringer.name_to_id(row["reqid"])

        logging.getLogger(self.__class__.__name__).info("\tRow:\n" + "\t\t" + row.to_string().replace("\n", "\n\t\t"))


        #check if this is setting up the classifications
        if ( row["reqid"].strip().lower().startswith("classification of digital health interventions")):            
            classification = row["reqid"].strip()
            classification_codes = re.findall(r'\d+\.?\d*', classification )
            logging.getLogger(self.__class__.__name__).info("\tFound classification text: " + classification)
            logging.getLogger(self.__class__.__name__).info("\tFound classification codes: " , classification_codes)
            continue


        if not "category" in row or not isinstance(row["category"], str):
            logging.getLogger(self.__class__.__name__).info("// skipping row "+str(index+1)+": no category")
            continue        
        if not "requirement" in row or not isinstance(row["requirement"], str):
            logging.getLogger(self.__class__.__name__).info("// skipping row "+str(index+1)+": no requirement")
            continue        
        
        cat = row["category"].strip()
        catid = stringer.name_to_id(cat)
        categories[catid] = cat     #OK to overwrite existing
        
        nfreq = row["requirement"].strip()


        lm_id = "LM." + reqid 
        lm = "Instance: " + self.escape(lm_id) + '\n'
        lm += 'InstanceOf: NonFunctionalRequirement\n'
        lm += 'Description: "' + self.escape(nfreq) + '"\n'
        lm += 'Usage: #definition\n'
        lm += '* id = "' + self.escape(lm_id) + '"\n'
        lm += '* requirement = "' + self.escape(nfreq) + '"\n'
        if (catid):
            lm += '* category = ' + self.escape(cat_cs) + '#' + self.escape(catid) + '\n'
        for classification_code in classification_codes:
            lm += '* classification[+] = ' + self.escape(class_cs) + '#' \
                + self.escape(classification_code) + '\n'


        
        instance = "//non-functional requirment instance generated from row " + str(index+1) + "\n"
        instance += "Instance: " + reqid + "\n"
        instance += "InstanceOf: SGRequirements\n"
        instance += "Usage: #definition" + "\n"
        instance += '* title = "' + self.escape(nfreq) + '"\n'
        instance += '* status = $pubStatus#active\n'
        instance += '* name = "' + self.escape(nfreq) + '"\n'
        instance += '* publisher = "WHO"\n'
        instance += '* experimental = true\n'
        if (catid):
            instance += '* extension[classification][+].valueCoding = ' + self.escape(cat_cs) + '#' + self.escape(catid) + '\n'
        for classification_code in classification_codes:
            instance += '* extension[classification][+].valueCoding = ' + self.escape(class_cs) + '#' + self.escape(classification_code) + '\n'
        description = '*Category*: ' + self.escape(cat) + "\n" + self.escape(nfreq)
        description = '* description = """\n' + description + '\n"""\n\n'
        instance += description + "\n"
        self.installer.add_resource('instances',lm_id,lm)
        self.installer.add_resource('requirements',reqid, instance)

    logging.getLogger(self.__class__.__name__).info("Extracted " + str(index) + " functional requirement(s)")

    self.installer.generate_cs_and_vs_from_dict(cat_cs,'Functional Requirement Categories',categories)
    return True


        

  def extract_functional_requirements_to_resources(functional: pd.DataFrame):
    logging.getLogger(self.__class__.__name__).info("Reading functional requirements")
    businessprocess_code = ""
    businessprocess_name = ""
    businessprocess_codes = {}
    classification = ""
    classification_codes = []
    bpid = "FXREQBusinessProcesses"
    
    functional.drop(index=0)

    for index, row in functional.iterrows():
        if not "reqid" in row or not isinstance(row["reqid"], str):
            logging.getLogger(self.__class__.__name__).info("// skipping row "+str(index+1)+": no reqid")
            continue
        reqid = stringer.name_to_id(row["reqid"])

        logging.getLogger(self.__class__.__name__).info("\tRow:\n" + "\t\t" + row.to_string().replace("\n", "\n\t\t"))

        #check if this is setting up the classifications
        if ( row["reqid"].strip().lower().startswith("classification of digital health interventions")):            
            classification = row["reqid"].strip()
            classification_codes = re.findall(r'\d+\.?\d*', classification )
            logging.getLogger(self.__class__.__name__).info("\tFound classification text: " + classification)
            logging.getLogger(self.__class__.__name__).info("\tFound classification codes: " , classification_codes)
            continue

        if ( row["reqid"].strip().lower().startswith("business process")):
            businessprocess = row["reqid"].strip()[16:].strip()
            logging.getLogger(self.__class__.__name__).info("\tFound business process row " + str(index+1) +  ": "+ businessprocess)
            parts = businessprocess.split(":",2)
            if (len(parts) == 2):
                businessprocess_code = parts[0].strip()
                businessprocess_name = parts[1].strip()
                logging.getLogger(self.__class__.__name__).info("\tFound business process code (" + businessprocess_code + ") associated to " + businessprocess_name )
                businessprocess_codes[businessprocess_code] = businessprocess_name

        if (businessprocess_code):
            reqid = reqid + "." + businessprocess_code

        if not "activityid-and-name" in row or not isinstance(row["activityid-and-name"], str):
            logging.getLogger(self.__class__.__name__).info("\t*warning* skipping row "+str(index+1)+": no activityid-and-name")
            continue
        
        if not "as-a" in row or not isinstance(row["as-a"], str):
            logging.getLogger(self.__class__.__name__).info("\t*warning* skipping row "+str(index+1)+": no as-a")
            continue

        if not "i-want" in row or not isinstance(row["i-want"], str):
            logging.getLogger(self.__class__.__name__).info("\t*warning* skipping row "+str(index+1)+": no i-want")
            continue

        if not "so-that" in row or not isinstance(row["so-that"], str):
            logging.getLogger(self.__class__.__name__).info("\t*warning* skipping row "+str(index+1)+": no so-that")
            continue
        
            
        components = row["activityid-and-name"].split(".")
        activityid = ".".join(components[:-1])
        activity_name = components[-1]

        actor_name = row["as-a"].strip()
        actor_id = string.name_to_id(actor_name)
        actor_instance = "Instance: " + self.escape(actor_id) + "\n"
        actor_instance += "InstanceOf: $SGActor\n"
        actor_instance += "Usage: #definition\n"
        actor_instance += '* name = "' + self.escape(actor_name) + '"\n'
        actor_instance += '* title = "' + self.escape(actor_name) + '"\n'
        actor_instance += '* description = "Actor ' + self.escape(actor_name) + ' from Function Requirements"\n'
        actor_instance += '* status = $pubStatus#active\n'
        actor_instance += '* experimental = true\n'
        actor_instance += '* publisher = "WHO"\n'
        actor_instance += '* type = $actorType#person\n'        
        self.installer.add_resource('actors',actor_id,actor_instance)  # ok to overwrite      
        actorlink='<a href="ActorDefinition-' + self.escape(actor_id) + '.html">' + self.escape(actor_name) +'</a>'
        

        description = 'Activity: ' + activity_name + ':\n' + \
            "As a " + actorlink + ", I want to:\n>" + self.escape(row['i-want']) + '\n\nso that\n\n>' + self.escape(row['so-that'])
        if (businessprocess_name):
            if (businessprocess_code):
                description = "*Business process* (" + self.escape(businessprocess_code) + ") "  \
                    + self.escape(businessprocess_name) + ":\n" + description
            else:
                description = "*Business process* "  + self.escape(businessprocess_name) + ":\n\n" + description

        
        lm_id = "LM." + reqid 
        lm = "Instance: " + self.escape(lm_id) + '\n'
        lm += 'InstanceOf: FunctionalRequirement\n'
        lm += 'Description: """' + description + '"""\n'
        lm += 'Usage: #definition\n'
        lm += '* id = "' + self.escape(lm_id) + '"\n'
        lm += '* activity = "' + self.escape(activity_name) + '"\n'
        lm += '* actor[+] = Reference(' + self.escape(actor_id) + ')\n'
        lm += '* capabilityString = "' + self.escape(row['i-want']) + '"\n'
        lm += '* benefitString = "' + self.escape(row['so-that']) + '"\n'
        if (businessprocess_code):
            lm += '* classification[+] = ' + bpid + '#' + self.escape(businessprocess_code) + '\n'
        for classification_code in classification_codes:
            lm += '* classification[+] = ' + self.escape(class_cs) + '#' \
                + self.escape(classification_code) + '\n'
        self.installer.add_resource('instances',lm_id,lm)

        instance = "//functional requirment instance generated from row " + str(index+1) + "\n"
        instance += "Instance: " + self.escape(reqid) + "\n"
        instance += "InstanceOf: SGRequirements\n"
        instance += "Usage: #definition" + "\n"
        instance += '* title = "' + self.escape(activity_name) + '"\n'
        instance += '* status = $pubStatus#active\n'
        instance += '* name = "' + self.escape(activity_name) + '"\n'
        instance += '* publisher = "WHO"\n'
        instance += '* experimental = true\n'
        instance += '* actor[+] = Canonical(' + self.escape(actor_id) + ')\n'
        if (businessprocess_code):
            instance += '* extension[classification][+].valueCoding = ' + bpid + '#' + self.escape(businessprocess_code) + '\n'
        for classification_code in classification_codes:
            instance += '* extension[classification][+].valueCoding = ' + self.escape(class_cs) + '#' \
                + self.escape(classification_code) + '\n'
        instance += '* extension[userstory].extension[capability].valueString = "' + self.escape(row['i-want']) + '"\n'
        instance += '* extension[userstory].extension[benefit].valueString = "' + self.escape(row['so-that']) + '"\n'
        description = '* description = """\n' + description + '\n"""\n\n'
        instance += description + "\n"
        self.installer.add_resource('requirements',reqid,instance)
        
    logging.getLogger(self.__class__.__name__).info("Extracted " + str(index) + " functional requirement(s)")
    logging.getLogger(self.__class__.__name__).info("Business Process Codes:\n\t" , businessprocess_codes)
    self.installer.generate_cs_and_vs_from_dict(bpid,'Functional Requirements Business Processes',businessprocess_codes)
    return True
