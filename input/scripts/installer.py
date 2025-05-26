import xml.etree.ElementTree as ET
import re
import os
import yaml
from pathlib import Path
import pprint
import sys

class installer:
  resources = { 'requirements' : {} ,'codesystems' : {} , 'valuesets' : {} , 'actors' : {} , 'instances': {}}  
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
                    log("Adding alias:" + alias)
                    file.write(alias + "\n")
                file.close()
        else:
            with open(self.aliasfile, 'r+') as file:
                content = file.read()
                for alias in self.aliases:
#                    log("Checking alias:" + alias)
                    if alias not in content:
                        log("Adding alias:" + alias)
                        file.write('\n' + alias + '\n')
                file.close()
    except IOError as e:
        log("Could not insert aliases")
        log(f"\tError: {e}")




        
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
    

  def save_resources(self):
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
            log("Could not save resource of type: " + directory + "  with id: " + id + "\n")
            log(f"\tError: {e}")
        

  def generate_cs_and_vs_from_dict(id:str, title:str, codelist:dict ):
    if len(codelist) == 0:
        return False
    
    codesystem = 'CodeSystem: ' + escape(id) + '\n'
    codesystem += 'Title: "' + escape(title) + '"\n'
    codesystem += 'Description:  "CodeSystem for ' + escape(title) + '. Autogenerated from DAK artifacts"\n'
    codesystem += '* ^experimental = true\n'
    codesystem += '* ^caseSensitive = false\n'
    codesystem += '* ^status = #active\n'
    for code,name in codelist.items():
        codesystem += '* #' + escape(code) +  ' "' + escape(name) + '"\n'
        
    valueset = 'ValueSet: ' + escape(id) + '\n'
    valueset += 'Title: "' + escape(title) + '"\n'
    valueset += 'Description:  "Value Set for ' + escape(title) + '. Autogenerated from DAK artifacts"\n'
    valueset += '* ^status = #active\n'
    valueset += '* ^experimental = true\n'
    valueset += '* include codes from system ' + escape(id) + '\n'
    

    self.add_resource('codesystems',id,codesystem)
    self.add_resource('valuesets',id, valueset)

    return True

  
  def add_resource(self,dir,id,resource):
    self.resources[dir][id]=resource


  def add_cql(self,id,cql):
    self.cqls[id]=cql    

  def log(self,*statements):
    for statement in statements:
      print(str(statement) ,  file=sys.stderr)
      self.logfile.write(str(statement) + "\n")
    self.logfile.flush()
