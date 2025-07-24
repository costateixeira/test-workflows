#!/usr/bin/env python3
"""
Data and Knowledge (DAK) Multi-Extractor Pipeline

This command-line script orchestrates the extraction of multiple types of
data and knowledge assets for the SMART guidelines system. It coordinates
various specialized extractors to process different file formats and data
sources in a unified workflow.

The script integrates multiple extractors including:
- Data Dictionary (DD) extractor for structured data definitions
- Requirements extractor for functional specifications  
- BPMN extractor for business process models
- Decision Table (DT) extractor for clinical decision logic
- SVG extractor for visual diagrams and illustrations

This provides a comprehensive pipeline for processing all DAK L2 content
into FHIR-compatible resources.

Usage:
    python extract_dak.py

Author: SMART Guidelines Team
"""

import stringer
import logging
from codesystem_manager import codesystem_manager
from installer import installer
from dd_extractor import dd_extractor
from req_extractor import req_extractor 
from bpmn_extractor import bpmn_extractor
from dt_extractor import dt_extractor
from svg_extractor import svg_extractor
import getopt
import sys


class extract_dak:
    """
    Multi-extractor pipeline for comprehensive DAK content processing.
    
    This class coordinates multiple specialized extractors to process
    various types of data and knowledge assets in a single workflow,
    ensuring consistent resource generation and proper integration
    between different content types.
    """
    
    def usage():
        print("Usage: scans for source DAK L2 content for extraction ")
        print("OPTIONS:")
        print(" none")
        print("--help|h : print this information")
        sys.exit(2)

    def extract(self):
        try:
            ins = installer()
            extractors = [dd_extractor,bpmn_extractor,svg_extractor,req_extractor,dt_extractor]
            for extractor in extractors:
                logging.getLogger(self.__class__.__name__).info("Initializing extractor " + extractor.__name__)
                ext = extractor(ins)
                if not ext.extract():
                    classname = extractor.__name__
                    logging.getLogger(self.__class__.__name__).info(f"ERROR: Could not extract on {classname}")
                    return False
            logging.getLogger(self.__class__.__name__).info("Installing generated resources and such")
            return ins.install()
        except Exception as e:            
            logging.getLogger(self.__class__.__name__).exception(f"ERROR: Could not extract: {e}")
            return False

    def main(self):
        try:
            opts,args = getopt.getopt(sys.argv[1:], "h", ["help"])
        except getopt.GetoptError:
            usage()

        if not self.extract():
            sys.exit(1)
        return True
    

if __name__ == "__main__":
    extract_dak().main()
