#!/usr/bin/env python3


from installer import installer
from req_extractor import req_extractor 
from dl_extractor import dl_extractor 
import getopt
import sys

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

    ins = installer()

    req_extractor(ins).extract()    
    dl_extractor(ins).extract()
    ins.install()


main()
