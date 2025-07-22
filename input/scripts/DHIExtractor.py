import installer

class DHIExtractror(extractor):
  installer = None
  def __init__(self,installer:installer):
    self.installer = installer

  
  def find_files():
      return ['input/data/system_categories.txt','input/data/dhi_v1.txt']
    
  def extract_file()
    if (self.inputfile_name == 'input/data/system_categories.txt'):
      extract_classifications()
    if (self.inputfile_name == 'input/data/dhi_v1.txt'):
      extract_categories()
    
    
  def extract_categories():
    cdhi_id = 'CDHIv1'
    cdhsc_id = 'CDSCv1'
    cm_id = "CDHIv1Hierarchy"

    logging.getLogger(self.__class__.__name__).info ("System Categories")
    interventions = {}
    for line in open(self.inputfile_name, 'r'):
      parts = line.strip().split(' ',1)
      if (len(parts) < 2):
          continue
      code = parts[0].strip().rstrip(".")
      intervention = parts[1].strip()
      logging.getLogger(self.__class__.__name__).info ("\t" + intervention + ' = ' + code)
      interventions[code] = intervention
    
    self.installer.get_codesystem_manager().add_cs_and_vs_from_dict(cdhsc_id, 'Classification of Digital Health System Categories v1', interventions)
    

  def extract_interventions():
    interventions = {}
    parent_map = {}

    for line in open(self.inputfile_name, 'r'):
      parts = line.strip().split(' ',1)
      if (len(parts) < 2):
          continue
      codes = parts[0].strip().split('.')
      code = ".".join(codes)
      parent_code = ".".join(codes[:-1])
      intervention = parts[1].strip()
      logging.getLogger(self.__class__.__name__).info ("\t" + intervention + ' = ' + code)
      interventions[code] = intervention
      if (parent_code):
          parent_map[code] = parent_code
    title = 'Classification of Digital Health Interventions v1'
    self.installer.get_codesystem_manager().add_cs_and_vs_from_dict(cdhi_id, title , interventions)


    if (len(parent_map) > 0): 
      title = "Hierarchy of the Classification of Digital Health Interventions v1"
      cm = "Instance:  " + escape(cm_id) + '\n'
      cm += "InstanceOf:   ConceptMap\n"
      cm += "Description:  \"Mapping to represent hierarchy within " + title + ".\"\n"
      cm += "Usage:        #definition\n"
      cm += "* name = \"" + escape(cm_id) + "\"\n"
      cm += "* title = \"" + escape(title) + "\"\n"
      cm += "* status = #active\n"
      cm += "* experimental = false\n"
      cm += "* sourceCanonical = Canonical(" + cdhi_id + ")\n"
      cm += "* targetCanonical = Canonical(" + cdhi_id + ")\n"
      cm += "* group[+]\n"
      cm += "  * source = Canonical(" + cdhi_id + ")\n"
      cm += "  * target = Canonical(" + cdhi_id + ")\n"
      for code,parent_code in parent_map.items():
          cm += "  * insert ElementMap( " +  code + ", " + parent_code + ", narrower)\n"
      self.installer.add_resource('conceptmaps',cm_id,cm)
    






    
    
