#!/usr/bin/env python3
"""
Data and Knowledge (DAK) Extraction Script

This script serves as the main entry point for extracting Data and Knowledge
content from various source files and generating FHIR resources. It coordinates
multiple extractors to process different types of input files.

The script handles:
- Data dictionary extraction (dd_extractor)
- Requirements extraction (req_extractor)
- BPMN business process extraction (bpmn_extractor)
- Data type extraction (dt_extractor)
- SVG diagram extraction (svg_extractor)

Usage:
    python extract_dak.py

Author: WHO SMART Guidelines Team
"""

import getopt
import logging
import sys
from typing import List

from bpmn_extractor import bpmn_extractor
from codesystem_manager import codesystem_manager
from dd_extractor import dd_extractor
from dt_extractor import dt_extractor
from installer import installer
from req_extractor import req_extractor
from svg_extractor import svg_extractor
import stringer


class extract_dak:
    """
    Main extraction coordinator for Data and Knowledge (DAK) content.
    
    This class manages the end-to-end process of extracting various types
    of DAK content from source files and installing the generated FHIR resources.
    It coordinates multiple specialized extractors to handle different input formats.
    """

    @staticmethod
    def usage():
        """
        Print usage information and exit.
        
        Displays command-line usage instructions for the extraction script.
        """
        print("Usage: scans for source DAK L2 content for extraction")
        print("OPTIONS:")
        print(" none")
        print("--help|h : print this information")
        sys.exit(2)

    def extract(self) -> bool:
        """
        Execute the DAK extraction process with all registered extractors.
        
        Initializes the installer and runs each extractor in sequence:
        1. Data Dictionary (dd_extractor)
        2. BPMN Business Processes (bpmn_extractor)
        3. SVG Diagrams (svg_extractor)
        4. Requirements (req_extractor)
        5. Data Types (dt_extractor)
        
        Returns:
            True if all extractions and installation succeeded, False otherwise
        """
        try:
            # Initialize installer
            ins = installer()
            
            # Define extraction pipeline - order matters for dependencies
            extractors = [
                dd_extractor,      # Data dictionary definitions
                bpmn_extractor,    # Business process models
                svg_extractor,     # SVG diagrams and visuals
                req_extractor,     # Requirements specifications
                dt_extractor       # Data type definitions
            ]
            
            # Execute each extractor in sequence
            for extractor_class in extractors:
                extractor_name = extractor_class.__name__
                logging.getLogger(self.__class__.__name__).info(f"Initializing extractor {extractor_name}")
                
                # Create extractor instance and run extraction
                extractor = extractor_class(ins)
                if not extractor.extract():
                    logging.getLogger(self.__class__.__name__).error(f"ERROR: Could not extract on {extractor_name}")
                    return False
                    
                logging.getLogger(self.__class__.__name__).info(f"Successfully completed {extractor_name}")
            
            # Install all generated resources
            logging.getLogger(self.__class__.__name__).info("Installing generated resources and artifacts")
            return ins.install()
            
        except Exception as e:
            logging.getLogger(self.__class__.__name__).exception(f"ERROR: Could not extract: {e}")
            return False

    def main(self) -> bool:
        """
        Main entry point for the extraction script.
        
        Parses command-line arguments and executes the extraction process.
        
        Returns:
            True if successful, exits with code 1 on failure
        """
        try:
            opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
        except getopt.GetoptError:
            self.usage()

        # Process command-line options
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                self.usage()

        # Execute extraction
        if not self.extract():
            sys.exit(1)
        return True


if __name__ == "__main__":
    extract_dak().main()
