import sys
import pprint
import os
import glob as glob
import re
import pandas as pd
import urllib.parse
from extractor import extractor 
from installer import installer
from pathlib import Path
class dt_extractor(extractor):
  
  prefix = "DT"

  # internal variables
  cql_definitions : dict
  cql_definitions_by_type : dict
  tab_data : dict      
  cql_definitions = {}
  cql_definitions_by_type = {'input':{},'output':{},'annotation':{}}
  tab_data = {}
  
  def __init__(self,installer:installer):
    super().__init__(installer)
    
  def find_files(self):
    return glob.glob("input/decision-logic/*xlsx")
        
  def find_cql_files(self):
    return glob.glob("input/cql/*cql")

  
  def extract_file(self):
    cover_column_maps = {
        'id_name':["Activity ID.Activity name"],
        'tab':["Tab name"],
        'dt_id': ["Decision-support table (DT), contraindications table and scheduling-logic table (S) identification (ID)"],
        'description': ["Table description"],
        'sources': ["Reference/source"],
        }
    sheet_names = ['COVER']
    cover_sheet = self.retrieve_data_frame_by_headers(cover_column_maps,sheet_names,range(0,20))
    
    
    if (not  self.extract_activities(cover_sheet)):
      self.log("Could not extract decision logic in: " + self.inputfile_name)
      return False        
      
    return True


  def extract_activities(self,cover_sheet:pd.DataFrame):
    id_name  = ""
    id = ""
    name = ""
    tab = ""
    dt_id = ""
    description = ""
    sources = ""


    if cover_sheet is None:
      self.log("Could not load cover sheet")      
      return False
    
    for index, row in cover_sheet.iterrows():
      has_non_empty = \
        (isinstance(row["tab"],str) and bool(row["tab"]) and row["tab"] != "-" )  \
        or ( isinstance(row["id_name"],str) and bool(row["id_name"]) and row["id_name"] != "-")  \
        or (isinstance(row["dt_id"],str) and bool(row["dt_id"]) and row["dt_id"] != "-")  \
        or (isinstance(row["description"],str) and bool(row["description"]) and row["description"] != "-" )           

      if not has_non_empty:
        self.log("Reached end of cover index table")
        break
      
      if  "id_name" in row and  isinstance(row["id_name"], str) and row["id_name"]:
        id_name = row["id_name"]

        
      if not id_name:
        self.log("could not get id_name on row=" + str(row))
        continue
      
      parts = id_name.split(" ",1)
      if (len(parts) != 2):
        self.log("Skipping bad activity id.name: " + id_name ,parts)
        continue
      
      id = parts[0].strip()
      name = parts[1].strip()

      if not "dt_id" in row  or not isinstance(row["dt_id"], str) or not row["dt_id"]:
        self.log("Could not load decision dt_id data", row)
        continue
      dt_id = self.name_to_id(row["dt_id"])
      
      if "tab" in row:
        if  isinstance(row["tab"], str) and row["tab"]:
          tab = row["tab"]
      else:
        tab = dt_id
      has_non_empty |= bool(row["tab"])

      #if tab != 'BCG':
      #  continue

      if not self.load_tab(tab):      
        self.log("Could not load tab data for "  + tab)
        continue

      data = {"tab":tab,"dt_id":dt_id,"description":row["description"],"source":row["sources"]}
      if not self.extract_activity_table(id,name,tab,dt_id,data):
        self.log("Could not extract decition table for id=" + id + " name=" + name + " data=" + str(data))


    cql_files = self.find_cql_files()
    #cql_files = ["input/cql/IMMZD5DTBCGElements.cql"]        
    cql_contents = {}
    for cql_file in cql_files:
      if cql_file.startswith(self.prefix):
        continue      
      cql_contents[cql_file] = Path(cql_file).read_text()

    all_codes = {}
    for tab_id,dts in self.cql_definitions.items():
      tab_codes = {}
      tab_markdown = "### Decision Tables for Tab  " + tab_id + "\n"


      for dt_id,cql_definitions in dts.items():
        dt_include = "{% include " + self.prefix + "-" + dt_id + ".html %}\n"
        dt_markdown = "### Decision Table " + dt_id + "\n"
        dt_markdown += dt_include
        tab_markdown += "#### Decision Table " + dt_id + "\n"
        tab_markdown += dt_include
        #self.installer.add_page(self.prefix + "-" + dt_id,dt_markdown)
        
        self.log("Processing DT ID cql for " + dt_id + " on tab_id " + tab_id)
        vs_id = self.name_to_id(self.prefix + '-'  + dt_id)
        dt_codes = []
        for cql_id,val in cql_definitions.items():
          if not cql_id:
            self.log("BAD:" + cql_id + " from " + dt_id)
            sys.exit(2)
          if not cql_id in all_codes:
            self.log("  adding new " + cql_id  + " -> " + str(val))
            if isinstance(val,str):
              cql_prop = { 'title' : val,
                           'pseudocode' : val,
                           'tab' : [tab_id],
                           'table' : [dt_id]
                          }
              all_codes[cql_id] = cql_prop
              tab_codes[cql_id] = cql_prop
            elif isinstance(val,dict) and 'title' in val:
              if not 'pseudocode' in val:
                val['pseudocode'] = val['title']
              all_codes[cql_id] = val
              all_codes[cql_id]['tab'] = [tab_id]
              all_codes[cql_id]['table'] = [dt_id]
              tab_codes[cql_id] = all_codes[cql_id]                            
            else:
              self.log("  skipping " + cql_id  )
              continue
          else:
            self.log("  updating" + cql_id  + " -> " + str(val))
            if isinstance(val,str):
              title = val
              tab_codes[cql_id] = {'pseudocode':title}
            elif isinstance(val,dict) and 'title' in val:
              title = val['title']
              tab_codes[cql_id] = val
            else:
              self.log("  skipping " + cql_id  )
              continue
            
            
            if title != all_codes[cql_id]['title']:
              self.log("ERROR: cql expression " + cql_id + " has repeated non-matching definition in decision table with id " + dt_id + " on tab_id " + tab_id )

          dt_codes += [cql_id]
          
        dt_vs_id = self.name_to_id(self.prefix + '-'+dt_id)
        self.installer.generate_vs_from_list(dt_vs_id,self.prefix, \
                                             'Decision Table for ' + dt_id + ". Autogenerated from DAK artifacts", \
                                             dt_codes)

      self.installer.add_page(self.prefix + "s-" + tab_id,tab_markdown)
      cql_desc ="This library contains Decision Table elements from the decision table " \
        + "<a href='" + self.prefix + dt_id + ".html'>" + dt_id + "</a>"
      properties = {'description':cql_desc}
      self.create_cql_skeleton_for_tab(tab_id,tab_codes,properties)        
      tab_vs_id = self.name_to_id(self.prefix + 's-'+tab_id)
      self.installer.generate_vs_from_list(tab_vs_id,self.prefix,'Decision Tables For Tab ' + tab_id,list(tab_codes.keys()))
      properties = {'decisionTables' : ", ".join(dt_codes) }


    #normalize content for codesystem
    normalized_codes = {}
    for cql_id,cql_prop in all_codes.items():
      #if cql_id != "The client is pregnant": 
      #  continue
      #  # BCG test case
        
      cql_prop['display'] = cql_prop['title']
      cql_prop['definition'] = cql_prop['title'] + "\nReferenced in the following locations:\n"
      cql_prop['definition'] += " * Decision Tables: " + ", ".join(cql_prop['table']) + "\n"
      cql_prop['definition'] += " * Tabs: " + ", ".join(cql_prop['tab']) + "\n"
      cql_prop['propertyString'] = {
        'table' : ", ".join(cql_prop['table']),
        'tab' : ", ".join(cql_prop['tab'])
      }
      cql_prop.pop('tab')
      cql_prop.pop('table')

      #look for existing defintions
      cql_prop['designation'] = []
      cql_defs = ""
      for cql_file,cql_content in cql_contents.items():
        pattern = r'(^define\s+(\'|")' + re.escape(cql_id) + r'(\'|")\s*:(.*?))(\/\*|^define|\Z)'        
        match = re.search(pattern, cql_content, re.DOTALL | re.MULTILINE | re.IGNORECASE)
        if not match:
          continue
        cql_def = match.group(1)
        if self.is_blank(cql_def):
          continue
        #self.log("for " + cql_id + " found in " + cql_file + "found:" +  cql_def)
        cql_defs += "//Found in " + cql_file + "\n\n" + cql_def + "\n\n"
      if not self.is_blank(cql_defs):
        cql_prop['designation'] += [{
          'value': '"""'  + cql_defs  + '"""',
          'language' : "#CQL" # technically needs to be in https://build.fhir.org/valueset-all-languages.html
        }]
      normalized_codes[cql_id] = cql_prop
      
    
    cs_properties = {
      'table': {
        'description':'"Decision Table ID"',
        'type':'#string'
      },
      'tab': {
        'description':'"Decision Tab"',
        'type':'#string'
      }
    }
    self.installer.generate_cs_and_vs_from_dict(self.prefix,'Decision Table ',normalized_codes,cs_properties)
    self.log("Extracted codes from decision tables")
    self.produce_activities()

    return True

  def produce_activities(self):    
    for code,expr in self.cql_definitions_by_type['output'].items():
      a_id = self.name_to_id(self.prefix + "Output." + code)
      fsh_activity =  "Profile: " + a_id + "\n"
      fsh_activity += "Parent: $SGActivityDefinition\n"
      fsh_activity +=  "Title: " + a_id + "\n"
      fsh_activity += 'Description: """' + self.escape(expr)  + '\n"""'
      fsh_activity += 'Usage: #definition\n'
      fsh_activity += '* ^abstract = true\n'

      self.installer.add_resource('activitydefinitions',a_id, fsh_activity)

    return True
  
  def create_cql_skeleton_for_tab(self,tab_id,cql_codes,properties = {}):
    lib_name = self.prefix + "Elements-" + tab_id 
    return self.installer.create_cql_library(lib_name,cql_codes,properties)
  
  
  def load_tab(self,tab:str):
    tab_id = self.name_to_id("tab")
    if tab_id in self.tab_data:
      return True
    
    self.log("Attempting to load decision table metadata for tab=" + tab)
    try:
      df = pd.read_excel(self.inputfile_name, sheet_name=tab,header=None)
      
    except Exception as e:
      self.log("Could not open sheet " + tab )
      self.log(e)
      return False

    tab_id = self.name_to_id(tab)
    self.log("Exracting tab to " + tab_id)
    self.tab_data[tab_id] = {'df' :df,'tables':{}}
    for col in df:
      matching_rows = df[col] == "Decision ID"
      sched_matching_rows = df[col] == "Schedule ID"
      
      if not isinstance(matching_rows,pd.Series) or not matching_rows.any():
        continue
      
      col_idx = df.columns.get_loc(col) 
      self.log("Found decision tables in column index " + str(col_idx) + " on  matched rows=", df[matching_rows])
      for row in df[matching_rows].iterrows():
        row_idx = row[0]
        self.log("Validating decision table on row= # " + str(row_idx) +  \
              "\n\t" +  '\t'.join(str(x) for x in row[1].values))
        decision_id = self.name_to_id(row[1][col_idx+1])
        if not isinstance(decision_id,str) or not decision_id:
          self.log("Could not find decision id to right of r,c:"+ row + "," + col)
          continue

        self.log("found decision id=" + decision_id)
        br_row = row_idx + 1
        if not isinstance(df[col][br_row],str) or not df[col][br_row] == "Business rule":
          self.log("Did not find Business Rule row of decision table " + decision_id)
          continue        
        br = df[col_idx + 1][br_row]
        if not isinstance(br,str) or not br:
          self.log("Did not find any Business Rule defined for decision table " + decision_id)
          continue

        trigger_row = row_idx + 2
        if not isinstance(df[col][trigger_row],str) or not df[col][trigger_row] == "Trigger":
          self.log("Did not find trigger row of decision table " + decision_id)
          continue
        trigger = df[col_idx + 1][trigger_row]
        if not isinstance(trigger,str) or not trigger:
          self.log("Did not find any trigger defined for decision table " + decision_id)
          continue

        input_row = row_idx + 3
        if not isinstance(df[col][input_row],str) or \
          ( not df[col][input_row] == "Inputs" and not df[col][input_row] == "Potential contraindications"):
          self.log("Did not find Inputs row of decision table " + decision_id)
          continue
        self.log("Found Inputs/Potential contraindications at " + str(col) + " / " + str(input_row))

        output_col = False
        guidance_col = False
        ref_col = False
        anno_col = False
        for c in df:
          if c <= col:
            continue
          if df[c][input_row] == "Output":
            output_col = c
          elif df[c][input_row] == "Guidance displayed to health worker":
            guidance_col = c
          elif df[c][input_row] == "Annotations":
            anno_col = c
          elif df[c][input_row] == "Reference(s)":
            ref_col = c
            
        if not output_col:
          self.log("Did not find Output column of decision table " + decision_id)
          continue

        if not guidance_col:
          self.log("Did not find Guidance column of decision table " + decision_id)
          b
        if not ref_col:
          self.log("Did not find Reference column of decision table " + decision_id)
                    
        self.log("Found decision table " + decision_id + " in " + tab + " at r,c:" + str(row_idx) + "," + str(col_idx) + ".  Saving in tab_id=" + tab_id + " with decision_id=" + decision_id)
        self.tab_data[tab_id]['tables'][decision_id] = {
          "row":row_idx,
          "col":col_idx,
          "trigger":trigger,
          "br":br,
          "input_row":input_row,
          "output_col":output_col,
          "guidance_col":guidance_col,
          "annotation_col":anno_col,
          "reference_col":ref_col,
          'used':False}        
    return True    


  def extract_activity_table(self,id:str,name:str,tab:str,dt_id:str,row):
    self.log("Looking for decision table ID=" + dt_id + " for activivity id /name (" + id + "/" + name + "): row=\n" + str(row))
    tab_id =self.name_to_id(tab)
    if dt_id not in self.tab_data[tab_id]['tables']:
      self.log("Could not find " + dt_id + " in sheet " + tab + " among found tables:" + ",".join(self.tab_data[tab_id]['tables'].keys()))
      return False
    data = self.tab_data[tab_id]['tables'][dt_id]
    df = self.tab_data[tab_id]["df"]
    
    ul_corner = df[data["col"]][data["row"]]
    is_contra_table = False
    is_regular_table = False
    is_schedule_table = False
    trigger = data["trigger"]
    br = data["br"]
    self.log("\n\n\nTT=" +       str(df[data["col"]][data["input_row"]]))
    if self.name_to_id(ul_corner) == self.name_to_id("Decision ID"):
      table_type = df[data["col"]][data["input_row"]]
      is_contra_table = table_type == "Potential contraindications"
      is_regular_table = table_type == "Inputs"      
    elif self.name_to_id(ul_corner) == self.name_to_id("Schedule ID"):
      table_type = ul_corner
      is_schedule_table = True
    else:
      self.log("Could not determine type of table from " + ul_corner + "/" + table_type )
      return False
        
    self.log("Using decision tab of type (" + table_type + ") " + dt_id + " in sheet " + tab + " at r,c:"  + str(data["row"]) +"," + str(data["col"])  )
    self.log("Tab data = \n\t" + pprint.pformat(data).replace("\n","\n\t"))



    in_table = True
    row_offset = 0
    pre_annotation = ""
    rule_dmns = []
    input_dmns = []
    output_dmns = []
    inputs = []
    
    if is_contra_table:
      contra_id = self.name_to_id(table_type)
      contra_dmn_id = "input." + contra_id
      contra_dmn = "<dmn:input id='" + contra_dmn_id + "' label='" + self.xml_escape(table_type) + "'></dmn:input>"
      self.log("rendereing contraindication input dmn for decision table ")
      input_dmns += [contra_dmn]

    if is_regular_table:
      output_name = "Care Plan"
      output_expr = "Produce a suggested Care Plan for consideration by health worker"
      output_dmns += [self.create_dmn_output_expression(dt_id, output_name , output_expr)]

      guidance_name = "Guidance displayed to health worker"
      guidance_expr = "Request to communicate guidance to the health worker"
      output_dmns += [self.create_dmn_output_expression(dt_id, guidance_name , guidance_expr)]

      annotation_name = "Annotations"
      annotation_expr = "Additional information for the health worker"
      output_dmns += [self.create_dmn_output_expression(dt_id, annotation_name , annotation_expr)]

      reference_name = "Reference(s)"
      reference_expr = "Reference for the source content (L1)"
      output_dmns += [self.create_dmn_output_expression(dt_id, reference_name , reference_expr)]


    fsh_plan =  "Profile: "  + dt_id + "\n"
    fsh_plan += "Parent: $SGDecisionTable\n"
    fsh_plan += "Title: " + dt_id + "\n"
    fsh_plan += 'Description: """' + self.escape(name) + '\n"""'
    fsh_plan += 'Usage: #definition\n'
    fsh_plan += '* ^abstract = true\n'
    vers = self.installer.get_ig_version() 
    fsh_plan += '* insert SGDecisionTable( ' + dt_id + "," + vers + ')\n'
    fsh_citations = set()
    fsh_rules = []

    found_definitions = False    
    while in_table:
      row_offset += 1      
      t_row = data["input_row"] + row_offset

      if not t_row in df[data["output_col"]]:
        in_table = False
        break
        
      first_val = df[data["col"]][t_row]
      self.log("scanning row=" + str(t_row) + " with first value=" + str( first_val ))

      found_definitions = len(inputs) > 0
      prev_inputs = inputs
      inputs = []
      trailing_nan_input = True
      trailing_blank_input = True
      i = 0
      vals = []
      for c in range(data["col"] ,data["output_col"]):
        val = df[c][t_row]
        vals += [val]
        self.log(' v='  + str(val) + "/" + str(i) + "/" + str(len(prev_inputs)))
        if self.is_nan(val)  and i < len(prev_inputs):
          self.log('  => setting to previous value')
          inputs += [prev_inputs[i]]
        else:
          inputs += [val]

        trailing_nan_input &=  ( i == 0 or self.is_nan(val) )
        trailing_blank_input &=  ( i==0 or self.is_blank(val))
        i += 1



      output = df[data["output_col"]][t_row]  if data["output_col"] else float('nan')
      guidance = df[data["guidance_col"]][t_row] if data["guidance_col"] else float('nan')
      reference = df[data["reference_col"]][t_row] if data["reference_col"] else float('nan')
      annotation = df[data["annotation_col"]][t_row] if data["annotation_col"] else float('nan')

      
      not_in_table = self.is_nan(first_val) and  trailing_nan_input  \
        and self.is_nan(output) and self.is_nan(guidance)  and self.is_nan(annotation)

      is_merged_line_annotation = isinstance(first_val,str) and first_val and trailing_nan_input \
        and self.is_blank(output) and self.is_blank(guidance) and self.is_blank(annotation)

      if not_in_table:
        self.log("Saw end of decision table starting at:" + str(t_row))
        in_table = False
        break

      if is_merged_line_annotation:
        self.log("Found pre-amble annotation=" + first_val)        
        pre_annotation += first_val + "\n"
        continue

      guidance = "" if self.is_nan(guidance) else str(guidance).strip()
      reference = "" if self.is_nan(reference) else str(reference).strip()
      annotation = "" if self.is_nan(annotation) else str(annotation).strip()
      output = "" if self.is_nan(output) else str(output).strip()
      
   
      debug = { 'tab_id' : tab_id,
                'dt_id': dt_id,
                'not_in_table' : not_in_table,
                'first_val' : first_val,
                'trailing_nan_input' : trailing_nan_input,
                'trailing_blank_input' : trailing_blank_input,
                'is_merged_line_annotation' : is_merged_line_annotation,
                'is_contra_table' : is_contra_table,
                'is_regular_table' : is_regular_table,
                'is_schedule_table' : is_schedule_table,
                'annotation' :  annotation, 
                'reference' : reference, 
                'output' : output, 
                'guidance' : guidance, 
                'vals' : vals, 
                'inputs' : inputs, 
                'prev_inputs' : prev_inputs
               }
      self.log(pprint.pp(debug))
            
      if pre_annotation:
        pre_annotation += "\n\n"
      
      if is_regular_table:
        self.log("Got input column")
        if not found_definitions:
          #it is a input variable definition
          self.log("rendeing dmn for decision table " )
          pre_annotation = "" #reset it
          input_dmns += self.process_input_definition_row(tab_id,dt_id,inputs)
          #we may hav had some extraneous/blank input definitions that we want to skip processing on in the future
          inputs = inputs[0:len(input_dmns)]
        else:
          #it is a rule
          rule_name = "dt." + dt_id + "." + str(row_offset)
          #we may hav had some extraneous/blank input definitions that we want to skip processing on in the future
          inputs = inputs[0:len(input_dmns)]
          rule_dmns += [self.process_input_row(tab_id,dt_id,rule_name,inputs,output,guidance,annotation,reference)]
          rule_dmns += [self.process_input_row(tab_id,dt_id,rule_name,inputs,output,guidance,annotation,reference)]
                    
          fsh_conditions = []
          for input in inputs:
            if self.is_blank(input) or self.is_dash(input):
              continue
            input_name = str(input).strip()
            parts = input_name.split("\n",1)
            if (len(parts) == 2):
              input_name = parts[0].strip()
            # indented as they are under '* action[+]'
            fsh_conditions += ['  * insert SGDecisionTableCondition("' + self.escape(input_name) + '")']
            
            
          output_name = str(output).strip()
          output_expr = output
          parts = output_name.split("\n",1)
          if (len(parts) == 2):
            output_name = parts[0].strip()            
            output_expr = parts[1].strip()
            
          fsh_rules.append('* insert SGDecisionTableOutput("' + self.escape( output_name) \
                          + '","' + self.escape(output_name) \
                          + '","' + self.escape(annotation) + ")")
          fsh_rules.extend(fsh_conditions)

          if not self.is_blank(guidance):
            fsh_rules.append('* insert SGDecisionTableGuidance("' + self.escape(guidance) + '")')
            fsh_rules.extend(fsh_conditions)

          if not self.is_blank(reference):
            fsh_citations.add('* insert SGDecisionTableCitation("' + self.escape(reference) + '")')
          
          pre_annotation = "" #reset it          
      elif is_contra_table:
        if self.is_blank(output):
          continue
        self.log("got contraindication")
        rule_name = "contra." + dt_id + "." + str(row_offset)        
        rule_dmns += [self.process_contra_indication_input_row(tab_id,dt_id,rule_name,inputs,output,guidance,annotation,reference)]
        pre_annotation = "" #reset it
      else:
        self.log("WARNING - UNKNOWN table type")
        return False

    self.log(fsh_rules)
    fsh_plan += "\n" + "\n".join(fsh_citations) +  "\n" + "\n".join(fsh_rules)
    self.installer.add_resource('plandefinitions',dt_id, fsh_plan)

    dt_dmn_id = self.prefix + "." + self.name_to_id(table_type) + "." + dt_id
    dt_dmn = "    <dmn:decisionTable >\n"
    for input_dmn in input_dmns:
      dt_dmn += "        " + input_dmn + "\n"
    for output_dmn in output_dmns:
      dt_dmn += "        " + output_dmn + "\n"
    for rule_dmn in rule_dmns:
      dt_dmn += "        " + rule_dmn + "\n"

    dt_dmn += "    </dmn:decisionTable>"
    

    trigger_parts = trigger.split(" ",1)
    if (len(trigger_parts) == 2):
      trigger_id = trigger_parts[0].strip()
      trigger_expr = trigger_parts[1].strip()
    else:
      trigger_id = trigger.strip()
      trigger_expr = trigger_id

    trigger_url =  self.installer.get_ig_canonical() + "/bpmn/" \
      + trigger_id + ".bpmn#" + urllib.parse.quote(trigger_expr)
    dt_dmn = "<dmn:question>" + self.xml_escape(br) + "</dmn:question>" \
      "<dmn:usingTask href='" + trigger_url + "'/>" \
      + dt_dmn
    self.installer.add_dmn_table(self.prefix + "-" + dt_id,dt_dmn)
    self.tab_data[tab_id]['tables'][dt_id]['used'] = True
    return True
  
  def process_contra_indication_input_row(self,tab_id:str,dt_id:str,rule_name:str,inputs,output:str,guidance:str,annotation:str,reference:str):
    rule_dmn_entries = []            
    for val in inputs:
      if self.is_blank(val) or self.is_dash(val) or self.is_nan(val):
        continue
      self.log("Adding contra '" + str(val) + "'")
      rule_dmn_entries.append(self.create_dmn_entry(tab_id,dt_id,rule_name,"input",str(val)))

    rule_dmn_entries.append(self.create_dmn_entry(tab_id,dt_id,rule_name,"output",output))

    if annotation:
      rule_dmn_entries.append(self.create_dmn_entry(tab_id,dt_id,rule_name,"annotation",annotation))
    if reference:
      rule_dmn_entries.append(self.create_dmn_entry(tab_id,dt_id,rule_name,"annotation",reference))          

    if guidance:
      rule_dmn_entries.append(self.create_dmn_entry(tab_id,dt_id,rule_name,"output",guidance))
    if annotation:
      rule_dmn_entries.append( self.create_dmn_entry(tab_id,dt_id,rule_name,"annotation",annotation))
    if reference:
      rule_dmn_entries.append(self.create_dmn_entry(tab_id,dt_id,rule_name,"annotation",reference))
    
    return self.create_dmn_rule(rule_name,rule_dmn_entries)

    
  def process_input_row(self,tab_id:str,dt_id:str,rule_name:str,inputs,output:str,guidance:str,annotation:str,reference:str):
    rule_dmn_entries = []            
    for val in inputs:
      self.log("Processing input defintion: " + str(val))
      rule_dmn_entries.append(self.create_dmn_entry(tab_id,dt_id,rule_name,"input",val))

    rule_dmn_entries.append(self.create_dmn_entry(tab_id,dt_id,rule_name,"output",output))

    if guidance:
      rule_dmn_entries.append(self.create_dmn_entry(tab_id,dt_id,rule_name,"output",guidance))
    if annotation:
      rule_dmn_entries.append(self.create_dmn_entry(tab_id,dt_id,rule_name,"annotation",annotation))
    if reference:
      rule_dmn_entries.append(self.create_dmn_entry(tab_id,dt_id,rule_name,"annotation",reference))
            
    return self.create_dmn_rule(rule_name,rule_dmn_entries)

  
  def process_input_definition_row(self,tab_id:str,dt_id:str,inputs):
    input_dmns = []
    for val in inputs:
      if self.is_blank(val) or self.is_dash(val) or self.is_nan(val):
        continue

      self.log("Processing input defintion: " + str(val))
      
      val_id = str(val).strip()
      parts = val_id.split("\n",1)
      if (len(parts) == 2):
        val_id = parts[0].strip()
        val_definition = parts[1].strip()
      else:
        val_definition = val_id

      val_id = self.escape_code(val_id)
      self.log("Found code(" + val_id + ")")
      if not tab_id in self.cql_definitions:
        self.cql_definitions[tab_id] = {}
      if not dt_id in self.cql_definitions[tab_id]:
        self.cql_definitions[tab_id][dt_id] = {}
      self.cql_definitions[tab_id][dt_id][val_id] = val_definition

      input_dmns.append(self.create_dmn_input_expression(dt_id,val_id,val_definition))
      self.log("Added CQL with:\n\tTAB_ID="  + tab_id + "\n\tDT_ID=" + dt_id + "\n\tNAME=" + val_id + "\n\tEXPR=" + val_definition)
    return input_dmns
              
  
  def create_dmn_rule(self,rule_name:str,rule_dmn_entries):
    rule_id = self.name_to_id(rule_name)
    rule_dmn_id = "rule." + rule_id
    rule_dmn = "<dmn:rule id='" + rule_dmn_id + "'>" + "\n".join(rule_dmn_entries)  + "</dmn:rule>"          
    return rule_dmn


  def create_dmn_entry(self,tab_id:str,dt_id:str,rule_name:str,type:str,name:str):
    expr = False
    if type == "input" or type == "output":
      name = str(name).strip()
      expr = name
      parts = name.split("\n",1)
      if (len(parts) == 2):
        name = parts[0].strip()
        expr = parts[1].strip()


      name = self.escape_code(name)
      self.log("Found entry code(" + name + ")")
      if not (self.is_dash(name) or self.is_blank(name) or self.is_nan(name)):
        if not tab_id in self.cql_definitions:
          self.cql_definitions[tab_id] = {}
        if not dt_id in self.cql_definitions[tab_id]:
          self.cql_definitions[tab_id][dt_id] = {}
        self.cql_definitions[tab_id][dt_id][name] = expr
        self.cql_definitions_by_type[type][name] = expr

        self.log("Added CQL via dmn with:\n\tTAB_ID="  + tab_id + "\n\tDT_ID=" + dt_id + "\n\tNAME=" + name + "\n\tEXPR=" + expr)

    id = self.name_to_id(rule_name + "." + str(name))
    dmn_id = type + "Entry."  + id
    #dmn = "<dmn:" + type  + "Entry id='" + dmn_id + "' expressionLanguage='http://smart.who.int'>"
    #dmn = "<dmn:" + type  + "Entry id='" + dmn_id + "'>"
    dmn = "<dmn:" + type  + "Entry>"
    if expr:
      dmn += "<dmn:description>" + self.xml_escape(expr) + "</dmn:description>"
    dmn += "<dmn:text>" + self.xml_escape(name) + "</dmn:text>" 
    dmn += "</dmn:" + type + "Entry>"
    return dmn


  def create_dmn_output_expression(self,dt_id:str,name:str,expr:str):
    type = "output"
    id = self.name_to_id(name)              
    dmn_id = type + "." +  dt_id + "." + id
    dmn_expr_id = type + "Expression." + dt_id + "." + id 
    dmn = "<dmn:" + type + " id='" + dmn_id + "' label='"+ self.xml_escape(name) + "'>"
    if expr:
      dmn += "<dmn:description >" + expr + "</dmn:description>" 
    dmn += "</dmn:" + type + ">"      
    return dmn

  def create_dmn_input_expression(self,dt_id:str,name:str, expr:str):
    type = "input"
    id = self.name_to_id(name)              
    dmn_id = type + "." +  dt_id + "." + id
    dmn_expr_id = type + "Expression." + dt_id + "." + id 
    dmn = "<dmn:" + type + " id='" + dmn_id + "' label='"+ self.xml_escape(name) + "'>"
    if expr:
      dmn += "<dmn:" + type + "Expression id='" + dmn_expr_id \
        + "' typeRef='string'><dmn:text>" + expr + "</dmn:text></dmn:" + type + "Expression>" 
    dmn += "</dmn:" + type + ">"      
    return dmn
