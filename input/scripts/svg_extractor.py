"""
SVG (Scalable Vector Graphics) File Extractor

This module processes SVG files from business process models and transforms them
for use in FHIR Implementation Guides. SVG files are typically used for diagrams,
flowcharts, and visual representations of clinical workflows.

Author: WHO SMART Guidelines Team
"""

import glob
import logging
import os
from typing import List

from extractor import extractor
from installer import installer


class svg_extractor(extractor):
    """
    Extractor for SVG (Scalable Vector Graphics) files.
    
    This extractor processes SVG files, typically containing diagrams and
    visual representations of clinical workflows, and transforms them for
    inclusion in FHIR Implementation Guides.
    
    SVG files are processed using XSLT transformations and copied to the
    appropriate output directory for inclusion in the generated IG.
    
    Attributes:
        xslt_file (str): Path to the XSLT transformation file for SVG processing
        namespaces (dict): XML namespaces used in SVG files
    """
    
    xslt_file: str = "includes/svg2svg.xsl"
    namespaces: dict = {'svg': 'http://www.w3.org/2000/svg'}
    
    def __init__(self, installer: installer):
        """
        Initialize the SVG extractor.
        
        Registers the SVG transformer with the installer to enable
        processing of SVG files using the specified XSLT and namespaces.
        
        Args:
            installer: The installer instance for resource management
        """
        super().__init__(installer)
        self.installer.register_transformer("svg", self.xslt_file, self.namespaces)

    def find_files(self) -> List[str]:
        """
        Find all SVG files in the business processes directory.
        
        Searches for files with .svg extension in the input/business-processes/
        directory.
        
        Returns:
            List of SVG file paths to process
        """
        return glob.glob("input/business-processes/*.svg")

    def extract_file(self) -> bool:
        """
        Process a single SVG file and transform it for IG inclusion.
        
        Reads the SVG file, applies XSLT transformation, and copies the
        result to the images directory for inclusion in the Implementation Guide.
        
        Returns:
            True if the transformation and copy was successful, False otherwise
        """
        try:
            with open(self.inputfile_name, 'r', encoding='utf-8') as file:
                svg_content = file.read()
                
                # Determine output path in images directory
                outputfile_name = "input/images/" + os.path.basename(self.inputfile_name)
                
                # Apply XSLT transformation and save to output directory
                if not self.installer.transform_xml("svg", svg_content, out_path=outputfile_name):
                    logging.getLogger(self.__class__.__name__).error(
                        f"Could not transform SVG file: {self.inputfile_name}"
                    )
                    return False
                
                logging.getLogger(self.__class__.__name__).info(
                    f"Successfully processed SVG file: {self.inputfile_name} -> {outputfile_name}"
                )
                return True
                
        except Exception as e:
            logging.getLogger(self.__class__.__name__).error(
                f"Error reading SVG file {self.inputfile_name}: {str(e)}"
            )
            return False
