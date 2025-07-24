"""
Base Extractor Class for SMART Guidelines Data Processing

This module provides the foundational extractor class that serves as the base
for all specific data extractors in the SMART guidelines system. It defines
common functionality for file processing, data frame manipulation, and
integration with the installer system.

The extractor class handles:
- File discovery and processing workflows
- Excel/CSV data frame operations with flexible column mapping
- Logging and quality assurance integration
- Alias management for FHIR resources

All specific extractors (DHI, BPMN, SVG, etc.) inherit from this base class
to leverage common data processing patterns.

Author: SMART Guidelines Team
"""
import stringer
import re
import os
import pandas as pd
from installer import installer
import logging


class extractor(object):
  """
  Base class for all data extractors in the SMART guidelines system.
  
  This abstract base class provides common functionality for processing
  various types of input files and converting them into FHIR resources.
  Subclasses implement specific extraction logic for different file types
  and data formats.
  
  The extractor provides flexible data frame processing with intelligent
  column mapping, allowing for variations in input file structures while
  maintaining consistent output.
  
  Attributes:
      inputfile_name (str): Path to the currently processed input file
      class_cs (str): Default CodeSystem URL for generated resources
      installer: Instance of the installer for resource management
  """

  inputfile_name = ""
  class_cs = "http://smart.who.int/base/CodeSystem/CDHIv1"
  
  @property
  def logger(self):
    """Get logger instance for this class."""
    return self.logger

  def find_files(self):
    """
    Discover files to be processed by this extractor.
    
    Abstract method to be implemented by subclasses to return
    a list of file paths that should be processed.
    
    Returns:
        List of file paths to process
    """
    return []
  
  def extract(self):
    """
    Main extraction workflow that processes all discovered files.
    
    Iterates through all files returned by find_files() and
    processes each one using the extract_file() method.
    
    Returns:
        True if extraction completed successfully
    """
    for inputfile_name in self.find_files():
      self.logger.info('IF=' + inputfile_name)
      self.inputfile_name = inputfile_name
      self.extract_file()
    return True
    
  def get_aliases(self):
    """
    Provide additional aliases for FHIR resource generation.
    
    Subclasses can override this method to contribute specific
    aliases needed for their resource generation.
    
    Returns:
        List of alias definitions
    """
    return []

  
  def __init__(self,installer:installer):
    """
    Initialize the extractor with an installer instance.
    
    Sets up the extractor with access to the installer for resource
    management and configures any necessary aliases.
    
    Args:
        installer: The installer instance for managing FHIR resources
    """
    self.installer = installer
    aliases = self.installer.get_base_aliases()
    aliases.extend(self.get_aliases())
    self.logger.info("Aliases" + str(aliases))
    self.installer.add_aliases(aliases)


  def extract_file(self):
    """
    Process a single input file.
    
    Abstract method to be implemented by subclasses to define
    the specific extraction logic for their file type.
    """
    pass

    

  # see https://www.youtube.com/watch?v=EnSu9hHGq5o&t=1184s&ab_channel=NextDayVideo
  def generate_pairs_from_lists(self,lista,listb):
    """
    Generate all possible pairs from two lists.
    
    Utility method for creating cartesian product of two lists,
    commonly used for trying different combinations of parameters.
    
    Args:
        lista: First list of items
        listb: Second list of items
        
    Yields:
        Tuples containing one item from each list
    """
    for a in lista:
      for b in listb:
        yield a,b

  def generate_pairs_from_column_maps(self,column_maps:dict):
    """
    Generate column name pairs from mapping configuration.
    
    Creates pairs of desired column names and possible source column
    names for flexible data frame column matching.
    
    Args:
        column_maps: Dictionary mapping desired names to lists of possible names
        
    Yields:
        Tuples of (desired_name, possible_name)
    """
    for desired_column_name,possible_column_names in column_maps.items():
      for possible_column_name in possible_column_names:
        yield str(desired_column_name),str(possible_column_name)

  def retrieve_data_frame_by_headers(self,column_maps,sheet_names,header_offsets = [0,1,2]):
    """
    Intelligently load Excel data with flexible column and sheet matching.
    
    This method attempts to find the correct sheet and header row configuration
    in an Excel file by trying different combinations of sheet names and
    header row positions. It performs fuzzy matching of column names to
    handle variations in input file structure.
    
    Args:
        column_maps: Dictionary mapping desired column names to lists of
                    possible source column names for matching
        sheet_names: List of possible sheet names to try
        header_offsets: List of row indices to try as header rows
        
    Returns:
        Pandas DataFrame with standardized column names, or None if no
        suitable configuration is found
        
    Example:
        column_maps = {
            'reqid': ["Requirement ID", "Req ID"],
            'description': ["Description", "Desc"]
        }
        df = self.retrieve_data_frame_by_headers(
            column_maps, 
            ["Requirements", "Reqs"], 
            [0, 1]
        )
    """
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
    self.logger.info("Looking at sheets:" +  " ".join(sheet_names))
    for sheet_name, header_row in self.generate_pairs_from_lists(sheet_names,header_offsets):
      self.logger.info("Checking sheetname/header row #: " + sheet_name +  "/"+ str(header_row))
      try:
        data_frame = pd.read_excel(self.inputfile_name, sheet_name=sheet_name, header=header_row)
      except Exception as e:
        self.logger.info("Could not open sheet " + sheet_name + " on header row " + str( header_row))
        self.logger.info(e)
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
            self.logger.info("Matched input sheet column " + column_name + " with desired column " + desired_column_name)
            true_column_map[column_name] =  desired_column_name
                                  
        if not column_name in true_column_map:
          #we dont need this input/source data frame column
          #we get rid of it to help normalize for downstream processing
          data_frame.drop(column_name,axis='columns', inplace=True)
          self.logger.info("Dropped: " + str(column_name))
          continue
                                          
      self.logger.info("Mapping columns: " + str(true_column_map))
      data_frame = data_frame.rename(columns=true_column_map)
      if ( list(data_frame) != list(column_maps.keys()) ):
        continue
                                       
      self.logger.info("Found desired column headers at sheet name / header row: " + sheet_name + "/" + str(header_row))
      #we are happy, return the data frame with normalized column names
      return data_frame

    #we tried all combinations and failed.
    return None


  def log(self,*statements):
    """
    Enhanced logging with file context information.
    
    Provides structured logging that includes the extractor class name
    and current file being processed for better debugging and monitoring.
    
    Args:
        *statements: Variable number of statements to log
    """
    prefix = self.__class__.__name__ + "(" + os.path.basename(self.inputfile_name) + "):"
    for statement in statements:
      statement = str(statement).replace("\n","\n\t")
      self.installer.log( prefix + statement )
      prefix = "\t"

  def qa(self,msg):
    """
    Report quality assurance issues.
    
    Forwards QA messages to the installer's quality assurance system
    for centralized issue tracking and reporting.
    
    Args:
        msg: Quality assurance message to report
    """
    self.installer.qa(msg)


