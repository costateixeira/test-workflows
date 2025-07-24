"""
Digital Health Interventions (DHI) Data Extractor

This module provides functionality to extract and process Digital Health Interventions 
data from text files and convert them into FHIR-compatible code systems and value sets.
The extractor handles both system categories and intervention classifications.

Author: WHO SMART Guidelines Team
"""

import logging
from typing import List
from installer import installer
from extractor import extractor
from stringer import escape


class DHIExtractor(extractor):
    """
    Extracts Digital Health Interventions (DHI) classifications and system categories
    from text files and creates FHIR CodeSystems, ValueSets, and ConceptMaps.
    
    This extractor processes two types of files:
    - System categories (input/data/system_categories.txt)
    - DHI version 1 classifications (input/data/dhi_v1.txt)
    
    Attributes:
        installer: The installer instance for managing FHIR resources
    """
    
    def __init__(self, installer: installer):
        """
        Initialize the DHI extractor.
        
        Args:
            installer: The installer instance for resource management
        """
        super().__init__(installer)
        self.installer = installer

    def find_files(self) -> List[str]:
        """
        Return the list of files to be processed by this extractor.
        
        Returns:
            List of file paths to process
        """
        return ['input/data/system_categories.txt', 'input/data/dhi_v1.txt']
    
    def extract_file(self) -> None:
        """
        Process the current input file based on its name.
        
        Routes to appropriate extraction method based on filename:
        - system_categories.txt -> extract_categories()
        - dhi_v1.txt -> extract_interventions()
        """
        if self.inputfile_name == 'input/data/system_categories.txt':
            self.extract_categories()
        elif self.inputfile_name == 'input/data/dhi_v1.txt':
            self.extract_interventions()
    
    def extract_categories(self) -> None:
        """
        Extract system categories from the system_categories.txt file.
        
        Creates a CodeSystem and ValueSet for Digital Health System Categories
        by parsing lines in format: "code description"
        
        The method:
        1. Parses each line to extract code and description
        2. Creates a dictionary mapping codes to descriptions
        3. Generates FHIR CodeSystem and ValueSet resources
        """
        cdhsc_id = 'CDSCv1'
        
        logging.getLogger(self.__class__.__name__).info("Processing System Categories")
        interventions = {}
        
        # Parse the input file line by line
        with open(self.inputfile_name, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split(' ', 1)
                if len(parts) < 2:
                    continue
                    
                # Extract code and intervention description
                code = parts[0].strip().rstrip(".")
                intervention = parts[1].strip()
                
                logging.getLogger(self.__class__.__name__).info(
                    f"\t{intervention} = {code}"
                )
                interventions[code] = intervention
        
        # Create CodeSystem and ValueSet
        self.installer.get_codesystem_manager().add_cs_and_vs_from_dict(
            cdhsc_id, 
            'Classification of Digital Health System Categories v1', 
            interventions
        )

    def extract_interventions(self) -> None:
        """
        Extract digital health interventions from the dhi_v1.txt file.
        
        Creates:
        1. CodeSystem and ValueSet for DHI classifications
        2. ConceptMap for hierarchy relationships (if hierarchical codes exist)
        
        The method processes hierarchical codes (e.g., "1.1.1") and creates
        parent-child relationships between codes.
        """
        cdhi_id = 'CDHIv1'
        cm_id = "CDHIv1Hierarchy"
        
        interventions = {}
        parent_map = {}

        # Parse the input file to extract interventions and hierarchy
        with open(self.inputfile_name, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split(' ', 1)
                if len(parts) < 2:
                    continue
                    
                # Parse hierarchical codes (e.g., "1.1.1" -> parent "1.1")
                codes = parts[0].strip().split('.')
                code = ".".join(codes)
                parent_code = ".".join(codes[:-1])
                intervention = parts[1].strip()
                
                logging.getLogger(self.__class__.__name__).info(
                    f"\t{intervention} = {code}"
                )
                
                interventions[code] = intervention
                
                # Track parent-child relationships for hierarchy
                if parent_code:
                    parent_map[code] = parent_code
        
        # Create CodeSystem and ValueSet for interventions
        title = 'Classification of Digital Health Interventions v1'
        self.installer.get_codesystem_manager().add_cs_and_vs_from_dict(
            cdhi_id, title, interventions
        )

        # Create ConceptMap for hierarchy if parent relationships exist
        if len(parent_map) > 0:
            self._create_hierarchy_concept_map(cdhi_id, cm_id, parent_map)
    
    def _create_hierarchy_concept_map(self, cdhi_id: str, cm_id: str, 
                                    parent_map: dict) -> None:
        """
        Create a ConceptMap to represent hierarchical relationships.
        
        Args:
            cdhi_id: The CodeSystem ID for digital health interventions
            cm_id: The ConceptMap instance ID
            parent_map: Dictionary mapping child codes to parent codes
        """
        title = "Hierarchy of the Classification of Digital Health Interventions v1"
        
        # Build ConceptMap FSH content
        cm = f"Instance: {escape(cm_id)}\n"
        cm += "InstanceOf: ConceptMap\n"
        cm += f'Description: "Mapping to represent hierarchy within {title}."\n'
        cm += "Usage: #definition\n"
        cm += f'* name = "{escape(cm_id)}"\n'
        cm += f'* title = "{escape(title)}"\n'
        cm += "* status = #active\n"
        cm += "* experimental = false\n"
        cm += f"* sourceCanonical = Canonical({cdhi_id})\n"
        cm += f"* targetCanonical = Canonical({cdhi_id})\n"
        cm += "* group[+]\n"
        cm += f"  * source = Canonical({cdhi_id})\n"
        cm += f"  * target = Canonical({cdhi_id})\n"
        
        # Add parent-child mappings
        for code, parent_code in parent_map.items():
            cm += f"  * insert ElementMap({code}, {parent_code}, narrower)\n"
        
        # Register the ConceptMap resource
        self.installer.add_resource('conceptmaps', cm_id, cm)