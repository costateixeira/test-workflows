"""
BPMN (Business Process Model and Notation) File Extractor

This module processes BPMN files from business process models and converts them
into FHIR-compatible FSH (FHIR Shorthand) resources using XSLT transformations.
BPMN files define workflow processes that can be represented as FHIR resources.

Author: WHO SMART Guidelines Team
"""

import glob
import logging
from typing import List

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
    
    xslt_file: str = "includes/bpmn2fhirfsh.xsl"
    namespaces: dict = {'bpmn': "http://www.omg.org/spec/BPMN/20100524/MODEL"}
    
    def __init__(self, installer: installer):
        """
        Initialize the BPMN extractor.
        
        Registers the BPMN transformer with the installer so it can process
        BPMN XML content using the specified XSLT file and namespaces.
        
        Args:
            installer: The installer instance for resource management
        """
        super().__init__(installer)
        self.installer.register_transformer("bpmn", self.xslt_file, self.namespaces)

    def find_files(self) -> List[str]:
        """
        Find all BPMN files in the business processes directory.
        
        Searches for files with .bpmn extension in the input/business-processes/
        directory.
        
        Returns:
            List of BPMN file paths to process
        """
        return glob.glob("input/business-processes/*.bpmn")

    def extract_file(self) -> bool:
        """
        Process a single BPMN file and convert it to FHIR resources.
        
        Reads the BPMN XML file and applies the XSLT transformation to convert
        it into FSH (FHIR Shorthand) format. The transformation handles the
        conversion of BPMN process elements into appropriate FHIR resources.
        
        Returns:
            True if the transformation was successful, False otherwise
        """
        try:
            with open(self.inputfile_name, 'r', encoding='utf-8') as file:
                bpmn_content = file.read()
                
                # Apply XSLT transformation to convert BPMN to FSH
                if not self.installer.transform_xml("bpmn", bpmn_content, process_multiline=True):
                    logging.getLogger(self.__class__.__name__).error(
                        f"Could not transform BPMN file: {self.inputfile_name}"
                    )
                    return False
                    
                logging.getLogger(self.__class__.__name__).info(
                    f"Successfully processed BPMN file: {self.inputfile_name}"
                )
                return True
                
        except Exception as e:
            logging.getLogger(self.__class__.__name__).error(
                f"Error reading BPMN file {self.inputfile_name}: {str(e)}"
            )
            return False
