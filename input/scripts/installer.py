"""
FHIR Resource Installation and Management System

This module provides the core installer functionality for the SMART guidelines
system, managing the generation, transformation, and installation of FHIR
resources from various source formats. It coordinates resource processing,
XSLT transformations, and file management for the entire build pipeline.

The installer serves as the central orchestrator for:
- FHIR resource generation and validation
- XSLT transformation management
- File system operations and directory structure maintenance
- Logging and quality assurance tracking
- Resource dependency resolution and installation

Author: SMART Guidelines Team
"""
import lxml.etree as ET
from typing import Union
import glob
import re
import os
import shutil
import yaml
from typing import List
from pathlib import Path
import pprint
import sys
from lxml import etree
import stringer
import codesystem_manager
import logging

class installer(object):

  dt_prefix = "DT"
  dd_prefix = "DD"

  resources = { 'requirements' : {} ,'codesystems' : {} , 'valuesets' : {} , 'rulesets' : {},
                'actors' : {} , 'instances': {}, 'rulesets' : {}, 'libraries' : {}, 'profiles' : {},
                'plandefinitions':{}, 'activitydefinitions':{}}  
  cqls = {}
  pages = {}
  sushi_config = {}
  multifile_xsd = "includes/multifile.xsd" #relative to the dir containing this file
  sushi_file = "sushi-config.yaml"
  multifile_schema = None  
  codesystem_manager = None
  xslts = {}
  temp_path = "temp"
  
  @property
  def logger(self):
    """Get logger instance for this class."""
    return logging.getLogger(self.__class__.__name__)
  
  def __init__(self):

    Path(self.temp_path).mkdir(exist_ok = True)
    logfile_path = self.temp_path  + "/" + os.path.basename(sys.argv[0]) + ".log"
    log_handlers = [logging.StreamHandler(), logging.FileHandler(logfile_path,mode = 'w')]
    logging.basicConfig(level=logging.INFO, handlers = log_handlers, format='%(levelname)s (%(name)s): %(message)s')
    if not self.read_sushi_config():
      raise Exception('Could not load sushi-config')
    Path("input/dmn").mkdir(exist_ok = True, parents = True)
    Path("input/bpmn").mkdir(exist_ok = True, parents = True)
    Path("input/cql").mkdir(exist_ok = True, parents = True)
    Path("input/fsh").mkdir(exist_ok = True, parents = True)
    Path("input/fsh/actordefinitions").mkdir(exist_ok = True, parents = True)
    Path("input/fsh/activitydefinitions").mkdir(exist_ok = True, parents = True)
    Path("input/fsh/plandefinitions").mkdir(exist_ok = True, parents = True)
    Path("input/pagecontent").mkdir(exist_ok = True, parents = True)
    if not self.load_multifile_schema():
      raise Exception('Could not load multifile xsd')
    
    publisher = self.get_ig_publisher()
    version = self.get_ig_version()
    self.codesystem_manager = codesystem_manager.codesystem_manager(publisher,version)

    #self.add_rulesets()

    
  def load_multifile_schema(self):
    """
        Loads and parses the multifile XML XSD, storing it as self.multifile_schema.
        """
    script_directory = self.get_base_dir() + "/input/scripts" 
    xsd_path = Path(script_directory + "/"  + self.multifile_xsd)
    try:
      with open(xsd_path, "rb") as xsd_file:
        schema_doc = ET.parse(xsd_file)
        self.multifile_schema = ET.XMLSchema(schema_doc)
        self.logger.info(f"Loaded multifile.xsd schema from {xsd_path}")
    except Exception as e:
      self.logger.info(f"FATAL: Could not load multifile.xsd from {xsd_path}: {e}")
      self.multifile_schema = None
      return False
    return True
 
  def get_base_dir(self):
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


  def register_transformer(self,key:str,xsl_file: Union[str,Path],namespaces:dict = {}):
    try:
      script_directory = self.get_base_dir() + "/input/scripts" 
      xsl_file = script_directory + "/" +  xsl_file
      self.logger.info("initializing xslt at " + xsl_file)
      for prefix,namespace in namespaces.items():
        ET.register_namespace(prefix , namespace)
      with open(Path(xsl_file), "rb") as f:
        self.xslts[key] = ET.XSLT(ET.parse(f))

    except BaseException as e:
      self.logger.info("WARNING: Could not find XSLT at " + xsl_file)
      self.logger.info(f"\tError: {e}")
      sys.exit(88)


    
  def read_sushi_config(self):
    try:
        with open(self.sushi_file, 'r') as file:
            self.sushi_config = yaml.safe_load(file)
            if not self.sushi_config:
              self.logger.info("Could not load sushi config")
              return False          
            self.logger.info("Got sushi config:\n\t" + pprint.pformat(self.sushi_config).replace("\n","\n\t"))
            return True
    except FileNotFoundError:
        self.logger.info("Could not find sushi config")
        return False
    except yaml.YAMLError as e:
       self.logger.info("Could not parse sushi config")
       return False
    return True

  def get_ig_config(self):
    return self.sushi_config

  def get_ig_publisher(self):
    if not 'publisher' in self.sushi_config or not 'name' in self.sushi_config['publisher']:
      return "Self Published"
    return self.sushi_config['publisher']['name']
  
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
    self.install_aliases()
    for cs_id,cs in self.codesystem_manager.render_codesystems().items():
      self.add_resource('codesystems',cs_id,cs)
    self.install_resources()
    self.install_dmns()
    self.install_pages()
    self.install_cqls()
    return True

  def install_cqls(self):
    for id,cql in self.cqls.items():
      self.install_cql(id,cql)
        
  def install_pages(self):
    for id,page in self.pages.items():
      self.install_page(id,page)


  dmn_tables = {}
  def add_dmn_table(self,dt_id:str,dt_dmn:str):
    if dt_id in self.dmn_tables:
      self.logger.info("**Warning** found duplicated decitiosn table with id=" + dt_id)
    self.logger.info("Added " + dt_id + " with content\n" + str(dt_dmn))
    self.dmn_tables[dt_id] = dt_dmn


  def get_codesystem_manager(self):
    return self.codesystem_manager
  



  def install_dmns(self):
    result = True
    for dt_id,dmn_table in self.dmn_tables.items():
      result &= self.install_dmn(dt_id,dmn_table)
    return result



  def add_rulesets(self):
    return True
    for ruleset_file in glob.glob(self.get_base_dir() + "/input/fsh/rulesets/*fsh"):      
      ruleset_id =  str(os.path.splitext(os.path.basename(ruleset_file))[0])
      with open(ruleset_file, 'r') as file:
        self.logger.info("Opned " + ruleset_file)
        ruleset = str(file.read())
        self.add_resource("rulesets",ruleset_id,ruleset)



    
  alias_file = "input/fsh/Aliases.fsh"
  aliases = []  #should change this to a set...

  def get_base_aliases(self):
    ig_alias_file = self.get_base_dir() + "/" + self.alias_file
    with open(ig_alias_file, 'r') as file:
      return str(file.read()).split("\n")
        
  
  def add_aliases(self , aliases):
    for alias in aliases:
      if alias not in self.aliases:
        self.aliases.append(alias)

  def install_aliases(self):
    try:
        if not os.path.exists(self.alias_file):
            with open(filename, 'w') as file:
                for alias in set(self.aliases):
                    self.logger.info("Adding alias:" + alias)
                    file.write(alias + "\n")
                file.close()
        else:
            with open(self.alias_file, 'r+') as file:
                content = file.read()
                for alias in set(self.aliases):
#                    self.logger.info("Checking alias:" + alias)
                    if alias not in content:
                        self.logger.info("Adding alias:" + alias)
                        file.write('\n' + alias + '\n')
                file.close()
    except IOError as e:
        self.logger.info("Could not insert aliases")
        self.logger.info(f"\tError: {e}")



  def install_page(self,id,page:str):
    try:
      file_path = "input/pagecontent/" + id + ".md"
      file = open(file_path,"w")
      print (page,file=file)
      file.close()
      self.logger.info("Installed " + file_path)
    except IOError as e:
      self.logger.info("Could not save page with id: " + id + "\n")
      self.logger.info(f"\tError: {e}")
    return True
    

        
  def install_cql(self,id,cql:str):
    try:
      file_path = "input/cql/" + id + ".cql"
      file = open(file_path,"w")
      print (cql,file=file)
      file.close()
      self.logger.info("Installed " + file_path)
    except IOError as e:
      self.logger.info("Could not save CQL with id: " + id + "\n")
      self.logger.info(f"\tError: {e}")
    return True


  def process_multifile_xml(self, multifile_xml: Union[str, ET.Element]) -> bool:
    """
        Parses a multi-file XML bundle and writes each file to disk according to its 'name' attribute.
        This is for XML of the form:
        <files>
          <file name="path/to/file.ext" mime-type="..."><![CDATA[...]]></file>
          ...
        </files>

        Args:
            multifile_xml: XML as string or lxml.etree.Element/ElementTree

        Returns:
            True on success, False on error (with logging).
    """
    try:
      # Parse input if it's a string
      if isinstance(multifile_xml, str):
        try:
          root = ET.fromstring(multifile_xml)
        except Exception as e:
          self.logger.info(f"ERROR: Could not parse multifile_xml string: {e}")
          return False
      elif isinstance(multifile_xml, (ET._Element, ET.ElementBase)):
        root = multifile_xml
      elif hasattr(multifile_xml, "getroot"):  # ElementTree
        root = multifile_xml.getroot()
      else:
        self.logger.info(f"ERROR: multifile_xml is not a recognized XML type: {type(multifile_xml)}")
        return False
      self.logger.info(f"Multifile={ET.tostring(multifile_xml)}")


      # Validate XML against schema
      if not self.multifile_schema.validate(multifile_xml):
        self.logger.info("XML failed XSD validation!")
        for error in self.multifile_schema.error_log:
          self.logger.info(f"XSD validation error: {error}")
        return False
      
      if root.tag != "files":
        self.logger.info(f"ERROR: Expected root element <files>, got <{root.tag}> instead.")
        return False
      file_elements = root.findall("file")
      if not file_elements:
        self.logger.info("WARNING: No <file> elements found in multifile XML.")
        return False
      for file_elem in file_elements:
        file_path = file_elem.get("name")
        self.logger.info("Extracting "  + file_path)
        mime_type = file_elem.get("mime-type", "text/plain")
        #content = etree.XML(file_elem.text) or ""
        content = file_elem.text
        if not file_path:
          self.logger.info("ERROR: <file> element missing 'name' attribute, skipping.")
          continue
        
        try:
          os.makedirs(os.path.dirname(file_path), exist_ok = True)
          with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            self.logger.info(f"Created file: {file_path} (mime-type: {mime_type}, {len(content)} bytes) with content:" + str(content))
        except Exception as fe:
          self.logger.info(f"ERROR: Could not write to file '{file_path}': {fe}")
          return False          

    except Exception as ex:
      self.logger.info(f"FATAL ERROR in process_multifile_xml: {ex}")
      return False

    return True
  
  def transform_xml(self,prefix:str,xml:Union[str,ET.ElementTree],out_path:Union[str,Path,bool] = False , process_multiline = False):
    if not prefix in self.xslts:
      self.logger.info("trying to transform unregistered thing "  + prefix)
      return False
    if isinstance(xml,ET._ElementTree) or isinstance(xml,ET._Element):
      xml_tree = xml
    elif isinstance(xml,str):
      xml = re.sub(r'<\?xml[^>]+\?>', '', xml)
      try:        
        xml_tree = ET.XML(xml)
        ET.indent(xml_tree)
      except BaseException as e:
        self.logger.info("ERROR: Generated invalid XML for " + prefix + "\n" +  f"\tError: {e}\n" )
        return False
    else:
      self.logger.info("invalid xml sent to transformer=" + str(xml))
      return False

    
    try:
      out = self.xslts[prefix](xml_tree)
      if out_path:
        self.logger.info("Transforming " + prefix + " to " + str(out_path))
        out = str(ET.tostring(out.getroot() , encoding="unicode",pretty_print = True, doctype=None))
        out_file = open(out_path, "w")
        out_file.write(out)
        out_file.close()
      elif process_multiline:
        return self.process_multifile_xml(out)
      else:
        return out
    except BaseException as e:
      self.logger.info("Could not process " + prefix + " in " + str(xml_tree))
      self.logger.info(f"\tError: {e}")
      return False
    
    return True


  
  def install_dmn(self,id,dmn:str):
    try:
      dmn_tree = ET.XML(dmn)
      ET.indent(dmn_tree)
    except BaseException as e:
      self.logger.info("ERROR: Generated invalid XML for DMN id " + id +"\n" +  f"\tError: {e}\n" )
      return False
    
    try:
      dmn_path = Path("input/dmn/") /  f"{id}.dmn"
      dmn_file = open(dmn_path,"w")
      #self.logger.info(ET.tostring(dmn_tree,encoding="unicode"))
      dmn_file.write(ET.tostring(dmn_tree,encoding="unicode"))
      #print(ET.tostring(dmn_tree,encoding="unicode"),file=dmn_file)
      dmn_file.close()
      self.logger.info("Installed " + str(dmn_path))
    except IOError as e:
      self.logger.info("Could not save DMN with id: " + id + "\n")
      log(f"\tERROR: {e}")
      return False

    html_path = Path("input/pagecontent/") / f"{id}.xml"
    return self.transform_xml("dmn",dmn_tree,out_path = html_path )
    
      
  
  def install_resources(self):
    result = True
    for directory, instances in self.resources.items() :
      for id,resource in instances.items() :
        try:
          file_path = "input/fsh/" + directory + "/" + id + ".fsh"
          Path("input/fsh/" + directory).mkdir(exist_ok = True, parents = True)
          file = open(file_path,"w")
          print(resource,file=file)
          file.close()
          self.logger.info("Installed " + file_path)
        except IOError as e:
          result = False
          self.logger.info("Could not save resource of type: " + directory + "  with id: " + id + "\n")
          self.logger.info(f"\tError: {e}")
    return result







  
  def add_resource(self,dir,id,resource:str):
    self.resources[dir][id]=resource
    return True


  def get_resource(self,dir,id):
    if self.has_resource(dir,id):
      return self.resources[dir][id]
    return None

  def has_resource(self,dir,id):
    return  dir in self.resources and id in self.resources[dir]

  def add_cql(self,id,cql:str):
    self.cqls[id]=cql
    return True

  def add_page(self,id,page:str):
    self.pages[id]=page
    return True


  def create_cql_library(self,lib_name,cql_codes:dict ={}, properties:dict = {}):
    lib_id = stringer.name_to_id(lib_name)
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
      self.logger.info("Invalid CQL code definitions for " + lib_name)
      sys.exit()
      return False
    
    for name,val in cql_codes.items():
      if isinstance(val,str):
        cql += "\n/*\n"
        cql += "@name: " + name + "\n"
        cql += "@pseudocode: " + val + "\n"
        cql += " */\n"
        cql += "define \"" + stringer.escape(name) + "\":\n"
        cql += "  //CQL AUTHORS: you need to insert stuff here\n"
      elif isinstance(val,dict):
        cql += "\n/*\n"
        cql += "Autogenerated documentation from DAK\n"
        cql += "@name: " + name + "\n"
        for k,v in val.items():
          cql += "@" + k + ": " + str(v) + "\n"            
        cql += " */\n"
        cql += "define \"" + stringer.escape(name) + "\":\n"
        cql += "  //CQL AUTHORS: you need to insert stuff here\n"
        if 'pseudocode' in val:
          cql += "  // " + "\n   // ".join(val['pseudocode'].splitlines(True)) + "\n"
          
    self.add_cql(lib_id,cql)
    
    library = "Instance: " + lib_id + "\n"
    library += "InstanceOf: Library\n"
    library += "Title: \"" + stringer.escape(lib_name) + "\"\n"
    library += "Description: \"This library defines context-independent elements for "  + lib_name + "\"\n"
    library += "Usage: #definition\n"
    library += "* insert LogicLibrary( " + lib_id + " )\n"    
    self.add_resource("libraries",lib_id,library)




    
