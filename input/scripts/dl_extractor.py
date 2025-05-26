import pprint
import os
import glob as glob
import re
import pandas as pd
from extractor import extractor 
from installer import installer

class dl_extractor(extractor):
  tab_data : dict      

  # def usage():
  #   print("Usage: scans input/decision-logic for excel sheets ")
  #   print("where the referenced excel contains a decision logic gables.")
  #   print("produces CQL and DMN assets")
  #   print("OPTIONS:")
  #   print(" none")
  #   print("--help|h : print this information")
  #   sys.exit(2)

  def __init__(self,installer:installer):
    super().__init__(installer)

  def find_files(self):
    return glob.glob("input/decision-logic/*xlsx")
        
    
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
    self.tab_data = {}

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

      
      if "tab" in row and  isinstance(row["tab"], str) and row["tab"]:
        tab = row["tab"]
      has_non_empty |= bool(row["tab"])

      if not self.load_tab(tab):      
        self.log("Could not load tab data for "  + tab)
        continue

      if not "dt_id" in row  or not isinstance(row["dt_id"], str) or not row["dt_id"]:
        self.log("Could not load decision dt_id data", row)
        continue
      dt_id = self.name_to_id(row["dt_id"])

      data = {"tab":tab,"dt_id":dt_id,"description":row["description"],"source":row["sources"]}
      if not self.extract_activity_table(id,name,tab,dt_id,data):
        self.log("Could not extract decition table for id=" + id + " name=" + name + " data=" + str(data))

    self.log("Extracted from cover")
    return True

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
    #for col in df.columns.tolist():
    for col in df:
      #self.log("Looking for Decision ID values in column=" , df[col])
      matching_rows = df[col] == "Decision ID"
      sched_matching_rows = df[col] == "Schedule ID"
      
      if not isinstance(matching_rows,pd.Series) or not matching_rows.any():
        #self.log("no matching rows")
        continue
      #self.log("matched ",matching_rows)
      
      col_idx = df.columns.get_loc(col) 
#      decision_id_col = df.iloc[col_idx +1]
#      self.log("second column is =",decision_id_col)
      

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
          self.log("Did not find any business rule defined for decision table " + decision_id)
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
          
        if not ref_col:
          self.log("Did not find referene column of decision table " + decision_id)
                    
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
    

  def is_blank(self,v):
    return v == None \
      or (isinstance(v, float) and v != v) \
      or (isinstance(v, str) and not v)

  def is_nan(self,v):
    return (isinstance(v, float) and v != v)

      
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
      input_dmns.append(contra_dmn)

    if is_regular_table:
      output_name = "Care Plan"
      output_expr = "Produce a suggested  Care Plan for consideration by health worker"
      output_dmns.append(self.create_dmn_output_expression(dt_id, output_name + "\n"  + output_expr))

      guidance_name = "Guidance displayed to health worker"
      guidance_expr = "Request to communitcate guidance to the health worker"
      output_dmns.append(self.create_dmn_output_expression(dt_id, guidance_name + "\n"  + guidance_expr))
        
    while in_table:
      row_offset += 1
      t_row = data["input_row"] + row_offset
      if not t_row in df[data["output_col"]]:
        in_table = False
        break
        
      first_val = df[data["col"]][t_row]
      self.log("scanning row=" + str(t_row) + " with first value=" + str( first_val ))
      
      prev_inputs = inputs
      inputs = []
      trailing_nan_input = True
      trailing_blank_input = True
      i = 0
      for c in range(data["col"] ,data["output_col"]):
        val = df[c][t_row]
        if self.is_blank(val) and i < len(prev_inputs):
          inputs.append(prev_inputs[i])
        else:
          inputs.append(val)

        trailing_nan_input &=  ( self.is_nan(val) )
        trailing_blank_input &=  ( self.is_blank(val))
        i += 1


      output = df[data["output_col"]][t_row]  if data["output_col"] else ""
      guidance = df[data["guidance_col"]][t_row] if data["guidance_col"] else ""
      guidance = "" if self.is_nan(guidance) else guidance
      reference = df[data["reference_col"]][t_row] if data["reference_col"] else ""
      reference = "" if self.is_nan(reference) else reference
      annotation = df[data["annotation_col"]][t_row] if data["annotation_col"] else ""
      annotation = "" if self.is_nan(annotation) else annotation
      
      not_in_table = self.is_blank(first_val) and trailing_blank_input and self.is_blank(output) \
        and self.is_blank(guidance) and self.is_blank(annotation)

      if not_in_table:
        self.log("Saw end of decision table starting at:" + str(t_row))
        in_table = False
        break
      
      is_merged_line_annotation = isinstance(first_val,str) and first_val and trailing_nan_input \
        and self.is_nan(output) and self.is_nan(guidance) and self.is_nan(annotation)
      
      if (is_merged_line_annotation):
        self.log("Found pre-amble annotation=" + first_val)        
        pre_annotation += first_val + "\n"
        continue

      # if we made it to here we should have something in the inputs
      self.log("Found inputs: (" +  ",".join(str(input) for input in inputs) + ")")

      if pre_annotation:
        pre_annotation += "\n\n"
      
      if is_regular_table:
        self.log("Got input column")
        if ( self.is_blank(output) and self.is_blank(annotation)):
          #it is a input variable definition          
          for val in inputs:
            if self.is_blank(val) or (isinstance(val,str) and val == "-"):
              continue
            if isinstance(val,str) and val.count("\n") == 0:
              #hacky way to deal with an input variable without a definition
              val += "\n" + val
            input_dmns.append(self.create_dmn_input_expression(dt_id,val))            
          self.log("rendereing dmn for decision table " )
          pre_annotation = "" #reset it
        else:
          #it is a rule
          rule_name = "dt." + dt_id + "." + str(row_offset)
          rule_dmn_entries = []            
          for val in inputs:
            rule_dmn_entries.append(self.create_dmn_entry(rule_name,"input",val))
          rule_dmn_entries.append(self.create_dmn_entry(rule_name,"output",output))
          if guidance:
            rule_dmn_entries.append(self.create_dmn_entry(rule_name,"output",guidance))
          if annotation:
            rule_dmn_entries.append( self.create_dmn_entry(rule_name,"annotation",annotation))
          if reference:
            rule_dmn_entries.append(self.create_dmn_entry(rule_name,"annotation",reference))          
          rule_dmns.append(self.create_dmn_rule(rule_name,rule_dmn_entries))
          pre_annotation = "" #reset it          
      elif is_contra_table:
        self.log("got contraindication" + str(first_val))
        rule_name = "contra." + dt_id + "." + str(row_offset)
        rule_dmn_entries = [self.create_dmn_entry(rule_name,"input",first_val)]
        if annotation:
          rule_dmn_entries.append(self.create_dmn_entry(rule_name,"annotation",annotation))
        if reference:
          rule_dmn_entries.append(self.create_dmn_entry(rule_name,"annotation",reference))          
        rule_dmns.append(self.create_dmn_rule(rule_name,rule_dmn_entries))
        pre_annotation = "" #reset it
      else:
        self.log("WARNING - UNKNOWN table type")
        return False

    dt_dmn_id = "decisionTable." + self.name_to_id(table_type) + "." + dt_id 
    dt_dmn = "    <dmn:decisionTable >\n"
    for input_dmn in input_dmns:
      dt_dmn += "        " + input_dmn + "\n"
    for output_dmn in output_dmns:
      dt_dmn += "        " + output_dmn + "\n"
    for rule_dmn in rule_dmns:
      dt_dmn += "        " + rule_dmn + "\n"

    dt_dmn += "    </dmn:decisionTable>"

    tab_id = self.name_to_id(tab)
    self.installer.add_dmn_table(dt_id,dt_dmn)
    self.tab_data[tab_id]['tables'][dt_id]['used'] = True    
    return True
      
  def create_dmn_rule(self,rule_name:str,rule_dmn_entries):
    rule_id = self.name_to_id(rule_name)
    rule_dmn_id = "rule." + rule_id
    rule_dmn = "<dmn:rule id='" + rule_dmn_id + "'>" + "\n".join(rule_dmn_entries)  + "</dmn:rule>"          
    return rule_dmn

  def create_dmn_entry(self,rule_name:str,type:str,name:str):
    expr = False
    if type == "input" or type == "output":
      parts = str(name).split("\n",1)
      if (len(parts) == 2):
        name = parts[0].strip()
        expr = parts[1].strip()
        
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


  def create_dmn_output_expression(self,dt_id:str,val):
    type = "output"
    expr = False
    name = str(val)
    parts = str(val).split("\n",1)
    if (len(parts) == 2):
      name = parts[0].strip()
      expr = parts[1].strip()              
    id = self.name_to_id(name)              
    dmn_id = type + "." +  dt_id + "." + id
    dmn_expr_id = type + "Expression." + dt_id + "." + id 
    dmn = "<dmn:" + type + " id='" + dmn_id + "' label='"+ self.xml_escape(name) + "'>"
    if expr:
      dmn += "<dmn:description >" + expr + "</dmn:description>" 
    dmn += "</dmn:" + type + ">"      
    return dmn

  def create_dmn_input_expression(self,dt_id:str,val):
    type = "input"
    expr = False
    name = str(val)
    parts = str(val).split("\n",1)
    if (len(parts) == 2):
      name = parts[0].strip()
      expr = parts[1].strip()              
    id = self.name_to_id(name)              
    dmn_id = type + "." +  dt_id + "." + id
    dmn_expr_id = type + "Expression." + dt_id + "." + id 
    dmn = "<dmn:" + type + " id='" + dmn_id + "' label='"+ self.xml_escape(name) + "'>"
    if expr:
      dmn += "<dmn:" + type + "Expression id='" + dmn_expr_id \
        + "' typeRef='string'><dmn:text>" + expr + "</dmn:text></dmn:" + type + "Expression>" 
    dmn += "</dmn:" + type + ">"      
    return dmn
