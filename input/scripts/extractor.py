import re
import os
import pandas as pd
from installer import installer

class extractor(object):

  inputfile_name = ""
  class_cs = "http://smart.who.int/base/CodeSystem/CDHIv1"


  def find_files(self):
    return []

  def extract(self):
    for inputfile_name in self.find_files():
      self.log('IF=' + inputfile_name)
      self.inputfile_name = inputfile_name
      self.extract_file()
    pass

  def get_aliases(self):
      return []

  
  def __init__(self,installer:installer):
    self.installer = installer
    aliases = self.get_aliases()
    self.log("Aliases",aliases)
    self.installer.add_aliases(aliases)


  def extract_file(self):
    pass

    

  # see https://www.youtube.com/watch?v=EnSu9hHGq5o&t=1184s&ab_channel=NextDayVideo
  def generate_pairs_from_lists(self,lista,listb):
    for a in lista:
        for b in listb:
            yield a,b

  def generate_pairs_from_column_maps(self,column_maps):
    for desired_column_name,possible_column_names in column_maps.items():
        for possible_column_name in possible_column_names:
            yield desired_column_name,possible_column_name

  def retrieve_data_frame_by_headers(self,column_maps,sheet_names,header_offsets = [0,1,2]):
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

    self.log("Seeking the following input data columns ", column_maps, header_offsets)
    for sheet_name, header_row in self.generate_pairs_from_lists(sheet_names,header_offsets):
        self.log("Checking sheetname/header row #: " + sheet_name +  "/"+ str(header_row))
        try:
            data_frame = pd.read_excel(self.inputfile_name, sheet_name=sheet_name, header=header_row)
        except Exception as e:
            self.log("Could not open sheet " + sheet_name + " on header row ", header_row)
            self.log(e)
            continue
        
#        self.log("Opened sheet " + sheet_name +  " on header_row " , header_row, "\nReading columns: ",list(data_frame))    

        true_column_map = {} #this is where we will map current column names to canonicalized/normalied column names        
        for column in list(data_frame):
            self.log("Looking at data frame column: ",column)                    
            column_id = self.name_to_lower_id(column)
#            self.log("Looking at data frame column id: ",column_id)                                
            #loop through potential names and try to match desired column
            for desired_column_name,possible_column_name in self.generate_pairs_from_column_maps(column_maps):
                possible_column_id = self.name_to_lower_id(possible_column_name)
                if (possible_column_id == column_id):
                    #we found what we needed
                    self.log("Matched input sheet column " + column + " with desired column " + desired_column_name)
                    self.log("Matched input sheet p_column_i " + str(possible_column_id) + " with  column_i " + str(column_id))
                    true_column_map[column] =  desired_column_name
                                  
            if not column in true_column_map:
                #we dont need this input/source data frame column
                #we get rid of it to help normalize for downstream processing
                data_frame.drop(column,axis='columns', inplace=True)
#                self.log("Dropped: ",column)
                continue
                                  
#        self.log("Mapping the following columns: ",true_column_map)
        #normalize column names
        data_frame = data_frame.rename(columns=true_column_map)
 #       self.log("Normalized Data frame Columns:" , list(data_frame))
        if ( list(data_frame) != list(column_maps.keys()) ):
#            self.log("Incorrect headers at ", header_row, " for data frame at " + sheet_name  + "." )
#            self.log("Received: ", list(data_frame))
            continue
                                       
        self.log("Found desired column headers at sheet name / header row: " + sheet_name + "/" + str(header_row))
        #we are happy, return the data frame with normalized column names
        return data_frame

    #we tried all combinations and failed.
    return None


  def log(self,*statements):
    prefix = self.__class__.__name__ + "(" + self.inputfile_name + "):"
    for statement in statements:
      statement = str(statement).replace("\n","\n\t")
      self.installer.log( prefix + statement )
      prefix = "\t"



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


  def xml_escape(self,input):
    if ( not (isinstance(input,str))):
      return ""
    # see https://stackoverflow.com/questions/1546717/escaping-strings-for-use-in-xml
    return input.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;").replace("'", "&apos;")



