"""
BPMN (Business Process Model and Notation) Extractor

This module provides functionality to extract and transform BPMN files into
FHIR resources for the SMART guidelines system. BPMN files typically define
clinical workflows, decision trees, and other healthcare process flows.

The extractor processes BPMN XML files using XSLT transformations to convert
business process definitions into FHIR-compatible formats suitable for
implementation in clinical decision support systems.

Author: SMART Guidelines Team
"""
import logging
import sys
import glob as glob
from extractor import extractor 
from installer import installer

class bpmn_extractor(extractor):
    """
    Extractor for BPMN (Business Process Model and Notation) files.
    
    This extractor processes BPMN XML files that define business processes
    and workflows, converting them to FHIR resources using XSLT transformations.
    
    BPMN files are typically used to model clinical workflows, decision trees,
    and other process flows in healthcare applications.
    
    Attributes:
        xslt_file (str): Path to the XSLT transformation file for BPMN to FSH conversion
        namespaces (dict): XML namespaces used in BPMN files
    """
    xslt_file  = "includes/bpmn2fhirfsh.xsl"
    namespaces = {'bpmn':"http://www.omg.org/spec/BPMN/20100524/MODEL"}
    
    def __init__(self,installer:installer):
        """
        Initialize the BPMN extractor with transformer registration.
        
        Sets up the extractor and registers the BPMN transformer with the
        installer for processing BPMN files.
        
        Args:
            installer: The installer instance for managing FHIR resources
        """
        super().__init__(installer)        
        self.installer.register_transformer("bpmn",self.xslt_file,self.namespaces)



    def find_files(self):
        """
        Find all BPMN files in the business processes directory.
        
        Searches for files with .bpmn extension in the input/business-processes/
        directory.
        
        Returns:
            List of BPMN file paths to process
        """
        return glob.glob("input/business-processes/*bpmn")
        

    def extract_file(self):
        """
        Process a single BPMN file through XML transformation.
        
        Reads the BPMN file content and applies the registered XSLT transformation
        to convert it into FHIR resources.
        
        Returns:
            True if transformation successful, False otherwise
        """
        with open(self.inputfile_name, 'r') as file:
            bpmn = str(file.read())
            if not self.installer.transform_xml("bpmn",bpmn,process_multiline=True):
                logging.getLogger(self.__class__.__name__).info("Could not transform bpmn on " + self.inputfile_name)
                return False
        return True
            

    
