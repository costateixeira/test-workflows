#!/usr/bin/env python3
"""
Digital Health Interventions (DHI) Extraction Script

This script serves as the main entry point for extracting Digital Health
Interventions data from source files and generating FHIR resources.
It coordinates the DHI extraction process and manages the installation
of generated resources.

Usage:
    python extract_dhi.py

Author: WHO SMART Guidelines Team
"""

import getopt
import logging
import sys
from typing import List

from installer import installer
from DHIExtractor import DHIExtractor


class extract_dhi:
    """
    Main extraction coordinator for Digital Health Interventions.
    
    This class manages the end-to-end process of extracting DHI data
    from source files and installing the generated FHIR resources.
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
        Execute the DHI extraction process.
        
        Creates an installer instance, runs the DHI extractor, and
        installs the generated FHIR resources.
        
        Returns:
            True if extraction and installation succeeded, False otherwise
        """
        try:
            # Initialize installer and extractor
            ins = installer()
            dhi_extractor = DHIExtractor(ins)
            
            # Execute extraction
            if not dhi_extractor.extract():
                logging.getLogger(self.__class__.__name__).error("Could not extract DHI data")
                return False
            
            # Install generated resources
            return ins.install()
            
        except Exception as e:
            logging.getLogger(self.__class__.__name__).error(f"ERROR: Could not extract: {e}")
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
    extract_dhi().main()
