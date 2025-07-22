import logging
import glob as glob
import os
from extractor import extractor 
from installer import installer

class svg_extractor(extractor):
    xslt_file  = "includes/svg2svg.xsl"
    namespaces = {'svg':'http://www.w3.org/2000/svg'}
    
    def __init__(self,installer:installer):
        super().__init__(installer)        
        self.installer.register_transformer("svg",self.xslt_file,self.namespaces)



    def find_files(self):
        return glob.glob("input/business-processes/*svg")
        

    def extract_file(self):
        with open(self.inputfile_name, 'r') as file:
            svg = str(file.read())
            outputfile_name = "input/images/" + os.path.basename(self.inputfile_name)
            if not self.installer.transform_xml("svg",svg,out_path=outputfile_name):
                logging.getLogger(self.__class__.__name__).info("Could not transform svg on " + self.inputfile_name)
                return False
        return True
            

    
