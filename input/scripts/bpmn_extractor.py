
import sys
import pprint
import os
import glob as glob
import re
import pandas as pd
import urllib.parse
from extractor import extractor 
from installer import installer
from pathlib import Path

class bpmn_extractor(extractor):
    xslt_file  = "includes/bpmn2fhirfsh.xsl"
    namespaces = {'bpmn':"http://www.omg.org/spec/BPMN/20100524/MODEL"}
    
    def __init__(self,installer:installer):
        super().__init__(installer)        
        self.installer.register_transformer("bpmn",self.xslt_file,self.namespaces)



    def find_files(self):
        return glob.glob("input/business-processess/*bpmn")
        

    def extract_file(self):
        self.inputfile_name
        with open(self.inputfile_name, 'r') as file:
            bpmn = str(file.read())
            if not self.installer.transform_xml("bpmn",bpmn,process_multiline=True):
                return False
        return True
            

    
