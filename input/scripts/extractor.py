import stringer
import re
import os
import pandas as pd
from installer import installer
import logging


class extractor(object):

  inputfile_name = ""
  class_cs = "http://smart.who.int/base/CodeSystem/CDHIv1"
  
  
  def find_files(self):
    return []
  
  def extract(self):
    for inputfile_name in self.find_files():
      logging.getLogger(self.__class__.__name__).info('IF=' + inputfile_name)
      self.inputfile_name = inputfile_name
      self.extract_file()
    return True
    
  def get_aliases(self):
    return []

  
  def __init__(self,installer:installer):
    self.installer = installer
    aliases = self.installer.get_base_aliases()
    aliases.extend(self.get_aliases())
    logging.getLogger(self.__class__.__name__).info("Aliases" + str(aliases))
    self.installer.add_aliases(aliases)


  def extract_file(self):
    pass

    

  # see https://www.youtube.com/watch?v=EnSu9hHGq5o&t=1184s&ab_channel=NextDayVideo
  def generate_pairs_from_lists(self,lista,listb):
    for a in lista:
      for b in listb:
        yield a,b

  def generate_pairs_from_column_maps(self,column_maps:dict):
    for desired_column_name,possible_column_names in column_maps.items():
      for possible_column_name in possible_column_names:
        yield str(desired_column_name),str(possible_column_name)

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
    logging.getLogger(self.__class__.__name__).info("Looking at sheets:" +  " ".join(sheet_names))
    for sheet_name, header_row in self.generate_pairs_from_lists(sheet_names,header_offsets):
      logging.getLogger(self.__class__.__name__).info("Checking sheetname/header row #: " + sheet_name +  "/"+ str(header_row))
      try:
        data_frame = pd.read_excel(self.inputfile_name, sheet_name=sheet_name, header=header_row)
      except Exception as e:
        logging.getLogger(self.__class__.__name__).info("Could not open sheet " + sheet_name + " on header row " + str( header_row))
        logging.getLogger(self.__class__.__name__).info(e)
        continue

      true_column_map = {} #this is where we will map current column names to canonicalized/normalied column names
      for column_name in list(data_frame):
        if stringer.is_blank(column_name):
          continue
        column_id = stringer.name_to_lower_id(column_name)

        for desired_column_name,possible_column_name in self.generate_pairs_from_column_maps(column_maps):          
          possible_column_id = stringer.name_to_lower_id(possible_column_name)
          if (possible_column_id == column_id):
            #we found what we needed
            logging.getLogger(self.__class__.__name__).info("Matched input sheet column " + column_name + " with desired column " + desired_column_name)
            true_column_map[column_name] =  desired_column_name
                                  
        if not column_name in true_column_map:
          #we dont need this input/source data frame column
          #we get rid of it to help normalize for downstream processing
          data_frame.drop(column_name,axis='columns', inplace=True)
          logging.getLogger(self.__class__.__name__).info("Dropped: " + str(column_name))
          continue
                                          
      logging.getLogger(self.__class__.__name__).info("Mapping columns: " + str(true_column_map))
      data_frame = data_frame.rename(columns=true_column_map)
      if ( list(data_frame) != list(column_maps.keys()) ):
        continue
                                       
      logging.getLogger(self.__class__.__name__).info("Found desired column headers at sheet name / header row: " + sheet_name + "/" + str(header_row))
      #we are happy, return the data frame with normalized column names
      return data_frame

    #we tried all combinations and failed.
    return None


  def log(self,*statements):
    prefix = self.__class__.__name__ + "(" + os.path.basename(self.inputfile_name) + "):"
    for statement in statements:
      statement = str(statement).replace("\n","\n\t")
      self.installer.log( prefix + statement )
      prefix = "\t"

  def qa(self,msg):
    self.installer.qa(msg)


