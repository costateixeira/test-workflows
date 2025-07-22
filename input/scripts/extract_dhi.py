#!/usr/bin/env python3

import installer
import DHIExtractor
import logging

class extract_dhi:


    

    def usage():
        print("Usage: scans for source DAK L2 content for extraction ")
        print("OPTIONS:")
        print(" none")
        print("--help|h : print this information")
        sys.exit(2)


    def extract():
        try: 
            ins = installer()
            if not DHIExtractor(ins).extract():
                logging.getLogger(self.__class__.__name__).info(f"ERROR: Could not extract: {e}")
                return False
            return ins.install()
        except Exception as e:
            logging.getLogger(self.__class__.__name__).info(f"ERROR: Could not extract: {e}")
            return False

    def main():
        try:
            opts,args = getopt.getopt(sys.argv[1:], "h", ["help"])
        except getopt.GetoptError:
            usage()

        if not self.extract():
            sys.exit(1)
        return True
    

if __name__ == "__main__":
    extract_dhi().main()

