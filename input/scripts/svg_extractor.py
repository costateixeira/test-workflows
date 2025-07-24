"""
SVG (Scalable Vector Graphics) Extractor

This module provides functionality to extract and transform SVG files for
integration with FHIR resources in the SMART guidelines system. SVG files
typically contain diagrams, flowcharts, and visual representations of
clinical processes and decision workflows.

The extractor processes SVG files using XSLT transformations and copies
them to the appropriate images directory for inclusion in the generated
FHIR implementation guide.

Author: SMART Guidelines Team
"""
from typing import List
import logging
import glob as glob
import os
from extractor import extractor 
from installer import installer

class svg_extractor(extractor):
    """
    Extractor for SVG (Scalable Vector Graphics) files.
    
    This extractor processes SVG files containing visual diagrams and
    illustrations, transforming them for inclusion in FHIR resources
    and implementation guides.
    
    SVG files are commonly used for clinical workflow diagrams,
    decision trees, and other visual documentation elements.
    
    Attributes:
        xslt_file (str): Path to the XSLT transformation file for SVG processing
        namespaces (dict): XML namespaces used in SVG files
    """
    xslt_file: str = "includes/svg2svg.xsl"
    namespaces: dict = {'svg':'http://www.w3.org/2000/svg'}
    
    def __init__(self, installer: installer) -> None:
        """
        Initialize the SVG extractor with transformer registration.
        
        Sets up the extractor and registers the SVG transformer with the
        installer for processing SVG files.
        
        Args:
            installer: The installer instance for managing FHIR resources
        """
        super().__init__(installer)        
        self.installer.register_transformer("svg",self.xslt_file,self.namespaces)



    def find_files(self) -> List[str]:
        """
        Find all SVG files in the business processes directory.
        
        Searches for files with .svg extension in the input/business-processes/
        directory.
        
        Returns:
            List of SVG file paths to process
        """
        return glob.glob("input/business-processes/*svg")
        

    def extract_file(self) -> bool:
        """
        Process a single SVG file through transformation and copy to images directory.
        
        Reads the SVG file content, applies the registered XSLT transformation,
        and saves the result to the input/images/ directory for inclusion
        in the generated implementation guide.
        
        Returns:
            True if transformation and copy successful, False otherwise
        """
        with open(self.inputfile_name, 'r') as file:
            svg = str(file.read())
            outputfile_name = "input/images/" + os.path.basename(self.inputfile_name)
            if not self.installer.transform_xml("svg",svg,out_path=outputfile_name):
                self.logger.info("Could not transform svg on " + self.inputfile_name)
                return False
        return True
            

    
