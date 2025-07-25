"""
Digital Health Intervention (DHI) Extractor Module

This module provides functionality to extract and process digital health intervention
classifications from text files. It handles both system categories and intervention
hierarchies, converting them into FHIR CodeSystems and ConceptMaps for the SMART
guidelines implementation.

The extractor processes two main types of files:
- system_categories.txt: Contains digital health system categories
- dhi_v1.txt: Contains digital health interventions with hierarchical codes

Author: SMART Guidelines Team
"""
from typing import List
from installer import installer
from extractor import extractor

class DHIExtractror(extractor):
    """
    Extractor for Digital Health Intervention (DHI) classifications.
    
    This class processes DHI classification files and converts them into FHIR
    resources including CodeSystems for the classifications and ConceptMaps
    for hierarchical relationships.
    
    Note: This class contains the original implementation with preserved structure
    for backward compatibility.
    
    Attributes:
        installer: The installer instance used for resource management
    """
    installer: installer = None
    def __init__(self, installer: installer) -> None:
        """
        Initialize the DHI extractor with an installer instance.
        
        Args:
            installer: The installer instance for managing FHIR resources
        """
        self.installer = installer

    
    def find_files(self) -> List[str]:
        """
        Locate the DHI classification files to be processed.
        
        Returns:
            List of file paths containing DHI classification data
        """
        return ['input/data/system_categories.txt','input/data/dhi_v1.txt']
        
    def extract_file(self) -> None:
        """
        Process the current input file based on its name and content type.
        
        Determines whether to extract system categories or intervention classifications
        based on the input file name.
        """
        if (self.inputfile_name == 'input/data/system_categories.txt'):
            self.extract_classifications()
        if (self.inputfile_name == 'input/data/dhi_v1.txt'):
            self.extract_categories()
        
        
    def extract_categories(self) -> None:
        """
        Extract digital health system categories from the input file.
        
        Processes system categories text file to create a FHIR CodeSystem
        containing the classification of digital health system categories.
        Each line contains a code and corresponding category description.
        """
        cdhi_id = 'CDHIv1'
        cdhsc_id = 'CDSCv1'
        cm_id = "CDHIv1Hierarchy"

        self.logger.info ("System Categories")
        interventions = {}
        for line in open(self.inputfile_name, 'r', encoding="utf-8"):
            parts = line.strip().split(' ',1)
            if (len(parts) < 2):
                continue
            code = parts[0].strip().rstrip(".")
            intervention = parts[1].strip()
            self.logger.info ("\t" + intervention + ' = ' + code)
            interventions[code] = intervention
        
        self.installer.get_codesystem_manager().add_cs_and_vs_from_dict(cdhsc_id, 'Classification of Digital Health System Categories v1', interventions)
        

    def extract_interventions(self) -> None:
        """
        Extract digital health interventions with hierarchical relationships.
        
        Processes intervention codes with dot notation to create both a FHIR CodeSystem
        for the interventions and a ConceptMap to represent the hierarchical
        relationships between parent and child interventions.
        """
        interventions = {}
        parent_map = {}

        for line in open(self.inputfile_name, 'r', encoding="utf-8"):
            parts = line.strip().split(' ',1)
            if (len(parts) < 2):
                continue
            codes = parts[0].strip().split('.')
            code = ".".join(codes)
            parent_code = ".".join(codes[:-1])
            intervention = parts[1].strip()
            self.logger.info ("\t" + intervention + ' = ' + code)
            interventions[code] = intervention
            if (parent_code):
                parent_map[code] = parent_code
        title = 'Classification of Digital Health Interventions v1'
        self.installer.get_codesystem_manager().add_cs_and_vs_from_dict(cdhi_id, title , interventions)


        if (len(parent_map) > 0): 
            title = "Hierarchy of the Classification of Digital Health Interventions v1"
            cm = "Instance:  " + escape(cm_id) + '\n'
            cm += "InstanceOf:   ConceptMap\n"
            cm += "Description:  \"Mapping to represent hierarchy within " + title + ".\"\n"
            cm += "Usage:        #definition\n"
            cm += "* name = \"" + escape(cm_id) + "\"\n"
            cm += "* title = \"" + escape(title) + "\"\n"
            cm += "* status = #active\n"
            cm += "* experimental = false\n"
            cm += "* sourceCanonical = Canonical(" + cdhi_id + ")\n"
            cm += "* targetCanonical = Canonical(" + cdhi_id + ")\n"
            cm += "* group[+]\n"
            cm += "  * source = Canonical(" + cdhi_id + ")\n"
            cm += "  * target = Canonical(" + cdhi_id + ")\n"
            for code,parent_code in parent_map.items():
                cm += "  * insert ElementMap( " +  code + ", " + parent_code + ", narrower)\n"
            self.installer.add_resource('conceptmaps',cm_id,cm)
    






    
    
