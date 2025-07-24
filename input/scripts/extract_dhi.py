#!/usr/bin/env python3
"""
Digital Health Intervention (DHI) Extraction CLI Script

This command-line script orchestrates the extraction of Digital Health
Intervention classifications from source data files. It serves as the
main entry point for processing DHI classification data and converting
it into FHIR resources for the SMART guidelines system.

The script integrates with the DHIExtractor to process system categories
and intervention hierarchies, generating appropriate CodeSystems and
ConceptMaps for use in clinical decision support implementations.

Usage:
    python extract_dhi.py

Author: SMART Guidelines Team
"""

import installer
import DHIExtractor
import logging
import getopt
import sys

class extract_dhi:
    """
    Command-line interface for DHI data extraction.
    
    This class provides the main interface for extracting Digital Health
    Intervention classifications from source files and converting them
    into FHIR resources through the installer system.
    """

    @property
    def logger(self):
        """Get logger instance for this class."""
        return logging.getLogger(self.__class__.__name__)

    def usage(self):
        """
        Display usage information for the DHI extraction script.
        
        Prints command-line usage instructions and available options
        before exiting the program.
        """
        print("Usage: scans for source DAK L2 content for extraction ")
        print("OPTIONS:")
        print(" none")
        print("--help|h : print this information")
        sys.exit(2)


    def extract(self):
        """
        Execute the DHI extraction process.
        
        Creates an installer instance, runs the DHI extractor, and
        processes the results through the installation system.
        
        Returns:
            True if extraction and installation successful, False otherwise
        """
        try: 
            ins = installer()
            if not DHIExtractor(ins).extract():
                self.logger.info(f"ERROR: Could not extract: {e}")
                return False
            return ins.install()
        except Exception as e:
            self.logger.info(f"ERROR: Could not extract: {e}")
            return False

    def main(self):
        """
        Main entry point for the DHI extraction script.
        
        Handles command-line argument processing and orchestrates
        the extraction workflow.
        
        Returns:
            True if successful, calls sys.exit(1) on failure
        """
        try:
            opts,args = getopt.getopt(sys.argv[1:], "h", ["help"])
        except getopt.GetoptError:
            self.usage()

        if not self.extract():
            sys.exit(1)
        return True
    

if __name__ == "__main__":
    extract_dhi().main()

