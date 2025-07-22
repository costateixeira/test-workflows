#!/usr/bin/env python3

import stringer
import logging
from codesystem_manager import codesystem_manager
from installer import installer
from dd_extractor import dd_extractor
from req_extractor import req_extractor 
from bpmn_extractor import bpmn_extractor
from dt_extractor import dt_extractor 
import getopt
import sys


class extract_dak:
    
    def usage():
        print("Usage: scans for source DAK L2 content for extraction ")
        print("OPTIONS:")
        print(" none")
        print("--help|h : print this information")
        sys.exit(2)

    def extract(self):
        try:
            ins = installer()
            extractors = [dd_extractor,bpmn_extractor,req_extractor,dt_extractor]
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
