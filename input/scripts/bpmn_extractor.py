
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
class dt_extractor(extractor):

    def __init__(self,installer:installer):
        super().__init__(installer)

    def find_files(self):
        return glob.glob("input/business-processess/*bpmn")
        

    def extract_file(self):
        self.inputfile_name
        with open(self.inputfile_name, 'r') as file:
            bpmn = str(file.read())
            out_file_path = "input/fshactordefinitions/"actors.fsh
            if not self.installer.transform_xml("bpmn",bpmn,process_multiline=True):
                return False
        return True
            

    
