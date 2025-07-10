#!/usr/bin/env python3

import installer
import DHIExtractor

def usage():
    print("Usage: scans for source DAK L2 content for extraction ")
    print("OPTIONS:")
    print(" none")
    print("--help|h : print this information")
    sys.exit(2)


def main():
    try:
        opts,args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.GetoptError:
        usage()

    resources = { 'codesystems' : {} , 'valuesets' : {}  , 'conceptmaps':{}}        
    DHIExtractor.extract(resources)
    installer.install(resources)
  
    return True
