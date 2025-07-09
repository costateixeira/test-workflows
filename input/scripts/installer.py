import xml.etree.ElementTree as ET
import re
import os
import yaml
from typing import List
from pathlib import Path
import pprint
import sys

class installer:
  resources = { 'requirements' : {} ,'codesystems' : {} , 'valuesets' : {} , 'rulesets' : {},
                'actors' : {} , 'instances': {}, 'rulesets' : {}, 'libraries' : {}}  
  cqls = {}
  logfile = None
  sushi_config = {}

  def __init__(self):
    logfile_path = Path("temp/DAKExtract.log.txt")
    print("Logging status messages to stderr and: " + str(logfile_path))
    logfile_path.parent.mkdir(exist_ok=True, parents=True)
    self.logfile = open(logfile_path,"w")
    Path("input/dmn").mkdir(exist_ok=True, parents=True)
    Path("input/cql").mkdir(exist_ok=True, parents=True)
    Path("input/fsh").mkdir(exist_ok=True, parents=True)
    if not self.read_sushi_config():
      raise Exception('Could not load sushi-config')
    self.add_rulesets()


    
    
  def read_sushi_config(self):
    sushi_file = "sushi-config.yaml"
    try:
        with open(sushi_file, 'r') as file:
            self.sushi_config = yaml.safe_load(file)
            if not self.sushi_config:
              self.log("Could not load sushi config")
              return False          
            self.log("Got sushi config:\n\t" + pprint.pformat(self.sushi_config).replace("\n","\n\t"))
            return True
    except FileNotFoundError:
        self.log("Could not find sushi config")
        return False
    except yaml.YAMLError as e:
       self.log("Could not parse sushi config")
       return False
    return True

  def get_ig_config(self):
    return self.sushi_config

  def get_ig_canonical(self):
    return self.sushi_config['canonical']

  def get_ig_name(self):
    return self.sushi_config['name']

  def get_ig_title(self):
    return self.sushi_config['title']

  def get_ig_id(self):
    return self.sushi_config['id']

  def get_ig_version(self):
    return self.sushi_config['version']
  
  def install(self):
    self.save_aliases()
    self.save_resources()
    self.save_dmns()
    
    for id,cql in self.cqls.items() :
        self.save_cql(id,cql)
        



  dmn_tables = {}
  def add_dmn_table(self,dt_id:str,dt_dmn:str):
    if dt_id in self.dmn_tables:
      self.log("**Warning** found duplicated decitiosn table with id=" + dt_id)
    self.dmn_tables[dt_id] = dt_dmn

  def name_to_lower_id(self,name):    
    if ( not (isinstance(name,str))):
      return None
    return re.sub('[^0-9a-zA-Z\\-\\.]+', '', name).lower()
    
  def name_to_id(self,name):    
    if ( not (isinstance(name,str))):
      return None
    return re.sub('[^0-9a-zA-Z\\-\\.]+', '', name)
      
  def escape(self,input):
    if ( not (isinstance(input,str))):
        return None
    return input.replace('"', r'\"')

      

  def save_dmns(self):
    
    for dt_id,dmn_table in self.dmn_tables.items():
        xml_dclr = "<?xml version='1.0' encoding='UTF-8' standalone='no'?>"
        namespace =  "https://www.omg.org/spec/DMN/20240513/MODEL/"
        out = xml_dclr + "\n"
        out += "<dmn:definitions  xmlns:dmn='" + namespace + "'\n"
        out += " namespace='" + self.get_ig_canonical() + "'\n"
        out += " name='"  + self.escape(dt_id) + "'\n"
        out += " id='" + self.name_to_id(self.get_ig_canonical() + "/dmn/" + dt_id) + ".dmn'>\n"            
        out += "  <dmn:decision id='" + self.name_to_id(dt_id) + "' name='" + self.escape(dt_id) + "'>\n"
        out +=  dmn_table + "\n"
        out += "  </dmn:decision>\n"
        out += "</dmn:definitions>\n"

        try:
          dmn = ET.XML(out)
          ET.register_namespace('dmn' , namespace )
          ET.indent(dmn)
        except:
          self.log("WARNING: Generated invalid XML for dt_id " + dt_id +". saving to input/dmn for review")
          self.save_dmn(dt_id ,out)
          return False
        # dmn_schema = XMLSchema('X110.xsd')
        # if not dmn.validate(dmn_schema):
        #   self.log("Invalid DMN for tab " + tab)
        #   return False
        if not self.save_dmn(dt_id,ET.tostring(dmn, encoding='unicode',xml_declaration=xml_dclr)):
          self.log("Could not save decision table id " + dt_id)
    return True



  def add_rulesets(self):
    ruleset_id = "LogicLibrary"
    ruleset = """RuleSet: LogicLibrary( library )
* meta.profile[+] = "http://hl7.org/fhir/uv/crmi/StructureDefinition/crmi-shareablelibrary"
* meta.profile[+] = "http://hl7.org/fhir/uv/crmi/StructureDefinition/crmi-publishablelibrary"
* meta.profile[+] = "http://hl7.org/fhir/uv/cql/StructureDefinition/cql-library"
* meta.profile[+] = "http://hl7.org/fhir/uv/cql/StructureDefinition/cql-module"
* extension[+]
  * url = "http://hl7.org/fhir/StructureDefinition/cqf-knowledgeCapability"
  * valueCode = #computable
* name = "{library}"
* status = #draft
* experimental = false
* publisher = "World Health Organization (WHO)"
* type = $library-type#logic-library
* content
  * id = "ig-loader-{library}.cql"
"""
    self.add_resource("rulesets",ruleset_id,ruleset)
  
  aliasfile = "input/fsh/Aliases.fsh"

  aliases = []  
  
  def add_aliases(self , aliases):
    for alias in aliases:
      if alias not in self.aliases:
        self.aliases.append(alias)

  def save_aliases(self):
    try:
        if not os.path.exists(self.aliasfile):
            with open(filename, 'w') as file:
                for alias in self.aliases:
                    self.log("Adding alias:" + alias)
                    file.write(alias + "\n")
                file.close()
        else:
            with open(self.aliasfile, 'r+') as file:
                content = file.read()
                for alias in self.aliases:
#                    self.log("Checking alias:" + alias)
                    if alias not in content:
                        self.log("Adding alias:" + alias)
                        file.write('\n' + alias + '\n')
                file.close()
    except IOError as e:
        self.log("Could not insert aliases")
        self.log(f"\tError: {e}")




        
  def save_cql(self,id,cql:str):
    try:
      file_path = "input/cql/" + id + ".cql"
      file = open(file_path,"w")
      print (cql,file=file)
      file.close()
      self.log("Installed " + file_path)
    except IOError as e:
      self.log("Could not save CQL with id: " + id + "\n")
      self.log(f"\tError: {e}")
    return True
    

  def save_dmn(self,id,dmn:str):
    try:
      file_path = "input/dmn/" + id + ".dmn"
      file = open(file_path,"w")
      print(dmn,file=file)
      file.close()
      self.log("Installed " + file_path)
    except IOError as e:
      self.log("Could not save DMN with id: " + id + "\n")
      log(f"\tError: {e}")
    return True

  def save_resources(self):
    result = True
    for directory, instances in self.resources.items() :
      for id,resource in instances.items() :
        try:
          file_path = "input/fsh/" + directory + "/" + id + ".fsh"
          Path("input/fsh/" + directory).mkdir(exist_ok=True, parents=True)
          file = open(file_path,"w")
          print(resource,file=file)
          file.close()
          self.log("Installed " + file_path)
        except IOError as e:
          result = False
          log("Could not save resource of type: " + directory + "  with id: " + id + "\n")
          log(f"\tError: {e}")
    return result

  def render_codesystem(self,id:str):
    if (not id in self.codesystems) or (not id in self.codesystem_titles):
      self.log("Trying to render absent codesystem " + id)
      return False
    title = self.codesystem_titles[id]
    codesystem = 'CodeSystem: ' + self.escape(id) + '\n'
    codesystem += 'Title: "' + self.escape(title) + '"\n'
    codesystem += 'Description:  "CodeSystem for ' + self.escape(title) + '. Autogenerated from DAK artifacts"\n'
    codesystem += '* ^experimental = false\n'
    codesystem += '* ^caseSensitive = false\n'
    codesystem += '* ^status = #active\n'
    for code,vals in self.codesystem_properties[id].items():
      codesystem += '* ^property[+].code = #"' + self.escape(code) + '"'
      for k,v in vals.items():
        codesystem += '* ^property[=].' + k + ' = ' + v + "\n" # user is responsible for content

    for code,val in self.codesystems[id].items():
      if isinstance(val,str):
        codesystem += '* #"' + self.escape(code) +  '" "' + self.escape(name) + '"\n'
      elif isinstance(val,dict) and 'code' in val and 'display' in val:
        codesystem += '* #"' + self.escape(val['code']) +  '" "' + self.escape(val['display']) + '"\n'
        if 'description' in val:
          description = val['title'] + "\nReferenced in the following locations:\n"
          description += " * Decision Tables: " + ", ".join(val['table']) + "\n"
          description += " * Tabs: " + ", ".join(val['tab']) + "\n"
          codesystem += '* ^description = """' + description + '\n"""\n'
        if 'propertyString' in val and isinstance(val['propertyString'],dict):
          for p_code,p_val in val['propertyString'].items():
            codesystem += '  * ^property[+].code = #"' + self.escape(p_code) +  '"\n'
            codesystem += '  * ^property[=].valueString = "' + self.escape(p_val) +  '"\n'

    return codesystem


  codesystems = {}
  codesystem_titles = {}
  codesystem_properties = {}

  def initialize_codesystem(self,codesystem_id:str,title:str):
    if codesystem_id in self.codesystems:
      self.log("WARNING: reinitializing codesystem " + codesystem_id)
    self.codesystems[codesystem_id] = {}
    self.codesystem_titles[codesystem_id] = title
    self.codesystem_properties[codesystem_id] = {}
    # need to replace this type of logic with exception handling probably
    return True


  def add_codesystem_properties(self,codesystem_id:str,vals:dict):
    for k,v in vals.items():
      self.add_codesystem_property(codesystem_id,k,v)
      
  def add_codesystem_property(self,codesystem_id:str,k:str,v):
    self.codesystem_properties[codesystem_id][k] = v

  def add_dict_to_codesystem(self,codesystem_id:str,inputs):
    result = True
    for code,expr in inputs.items():
      result &= self.add_to_codesystem(codesystem_id,code,expr)
    return result
    
  def add_to_codesystem(self,codesystem_id:str,code:str,expr:str):
    if not codesystem_id in self.codesystems:
      self.log("ERROR: Code system not initialized " + codesystem_id)
      return False

    if code in self.codesystems[codesystem_id] and expr != self.codesystems[codesystem_id][code]:
        # want this to be a structured ERROR for quality control back to the L2 authors
        self.log("ERROR: non-matching definitions for code " + code + " in code system " + codesystem_id)
        return False
      
    self.codesystems[codesystem_id][code] = expr
    return True


  def generate_vs_from_list(self,id:str, codesystem_id:str, title:str, codes):
        
    valueset = 'ValueSet: ' + self.escape(id) + '\n'
    valueset += 'Title: "' + self.escape(title) + '"\n'
    valueset += 'Description:  "Value Set for ' + self.escape(title) + '. Autogenerated from DAK artifacts"\n'
    valueset += '* ^status = #active\n'
    valueset += '* ^experimental = false\n'
    for code in codes:
      valueset += '* include ' + self.escape(codesystem_id) + '#"' + self.escape(code) + '"\n'
    
    self.add_resource('valuesets',id, valueset)

    return True

  

  def generate_cs_and_vs_from_dict(self,id:str, title:str, codelist:dict ):
    if not self.initialize_codesystem(id,title):
      self.log("Skipping CS and VS for " + str + " could not initialize")
      return False
    if not self.add_dict_to_codesystem(id,codelist):
      self.log("Skipping CS and VS for " + str + " could not add dictionary")
      return False
    cs_prop = {'description':'Decision Table ID','type':'#string'}
    self.add_codesystem_property(id,'table',cs_prop)
    codesystem = self.render_codesystem(id)
    
    valueset = 'ValueSet: ' + self.escape(id) + '\n'
    valueset += 'Title: "' + self.escape(title) + '"\n'
    valueset += 'Description:  "Value Set for ' + self.escape(title) + '. Autogenerated from DAK artifacts"\n'
    valueset += '* ^status = #active\n'
    valueset += '* ^experimental = false\n'
    valueset += '* include codes from system ' + self.escape(id) + '\n'

    self.add_resource('codesystems',id,codesystem)
    self.add_resource('valuesets',id, valueset)
    return True
  
  def add_resource(self,dir,id,resource):
    self.resources[dir][id]=resource


  def add_cql(self,id,cql):
    self.cqls[id]=cql    


  def create_cql_library(self,lib_name,cql_codes, properties = {}):
    lib_id = self.name_to_id(lib_name)
    cql =  "/*\n"
    cql += "@libname: " + lib_name + "\n"
    cql += "@libid: " + lib_id + "\n"
    for k,v in properties.items():
      cql += '@' + k + ': ' + v + "\n"
    cql += "*/\n"
    cql += "library " + lib_id + "\n"
    #cql += "using FHIR version '4.0.1'\n"
    #cql += "include FHIRHelpers version '4.0.1'\n" #do we want to include some common libraries?
    cql += "\ncontext Patient\n"

    if not isinstance(cql_codes,dict):
      self.log("Invalid CQL code definitions for " + lib_name)
      sys.exit()
      return False
    
    for name,val in cql_codes.items():
      if isinstance(val,str):
        cql += "\n/*\n"
        cql += "@name: " + name + "\n"
        cql += "@pseudocode: " + val + "\n"
        cql += " */\n"
        cql += "define \"" + self.escape(name) + "\":\n"
        cql += "  //CQL AUTHORS: you need to insert stuff here\n"
      elif isinstance(val,dict):
        cql += "\n/*\n"
        cql += "Autogenerated documentation from DAK\n"
        cql += "@name: " + name + "\n"
        for k,v in val.items():
          cql += "@" + k + ": " + str(v) + "\n"            
        cql += " */\n"
        cql += "define \"" + self.escape(name) + "\":\n"
        cql += "  //CQL AUTHORS: you need to insert stuff here\n"
        if 'pseudocode' in val:
          cql += "  // " + "\n   // ".join(val['pseudocode'].splitlines(True)) + "\n"

    self.add_cql(lib_id,cql)
    
    library = "Instance: " + lib_id + "\n"
    library += "InstanceOf: Library\n"
    library += "Title: \"" + self.escape(lib_name) + "\"\n"
    library += "Description: \"This library defines context-independent elements for "  + lib_name + "\"\n"
    library += "Usage: #definition\n"
    library += "* insert LogicLibrary( " + lib_id + " )\n"    
    self.add_resource("libraries",lib_id,library)

    
  def log(self,*statements):
    for statement in statements:
      print(str(statement) ,  file=sys.stderr)
      self.logfile.write(str(statement) + "\n")
    self.logfile.flush()


    
