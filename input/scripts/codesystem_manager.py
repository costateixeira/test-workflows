"""
FHIR CodeSystem Management

This module provides comprehensive management functionality for FHIR CodeSystems
and ValueSets within the SMART guidelines system. It handles the creation,
validation, and organization of clinical terminologies and code classifications
used throughout the implementation.

The codesystem_manager maintains centralized control over:
- CodeSystem creation and population
- ValueSet generation from CodeSystems
- Code validation and hierarchy management
- Resource naming and identifier assignment

Author: SMART Guidelines Team
"""
import re
import pprint
import sys
import stringer
import logging

class codesystem_manager(object):
    """
    Central manager for FHIR CodeSystem and ValueSet resources.
    
    This class provides comprehensive functionality for creating, managing,
    and validating FHIR CodeSystems and their associated ValueSets. It
    ensures consistent resource generation and proper code organization
    across the SMART guidelines implementation.
    
    Attributes:
        codesystems (dict): Collection of managed CodeSystem resources
        codesystem_titles (dict): Mapping of CodeSystem IDs to display titles
        codesystem_properties (dict): Properties and metadata for CodeSystems
    """
    codesystems = {}
    codesystem_titles = {}
    codesystem_properties = {}

    publisher:str 
    version:str
    
    @property
    def logger(self):
        """Get logger instance for this class."""
        return logging.getLogger(self.__class__.__name__)
    
    def __init__(self,publisher = "Self Pubished",version = "0.1.0"):
        self.publisher = publisher
        self.version = version


    def register(self,codesystem_id:str,title:str):
        if self.has_codesystem(codesystem_id):
            self.logger.info("WARNING: reinitializing codesystem " + codesystem_id)
        self.codesystems[codesystem_id] = {}
        self.codesystem_titles[codesystem_id] = title
        self.codesystem_properties[codesystem_id] = {}
            # need to replace this type of logic with exception handling probably
        return True
    
    def has_codesystem(self,id:str):
        return id in self.codesystems and id in self.codesystem_titles

    def get_title(self,id:str):
        if not self.has_codesystem(id):
            return None
        return self.codesystem_titles[id]
    
    
    def get_properties(self,id:str):
        if not self.has_codesystem(id):
            return {}
        return self.codesystem_properties[id]


    def get_codes(self,id:str):
        if not self.has_codesystem(id):
            return {}
        return self.codesystems[id]
    
    def get_code(self,codesystem_id:str,code:str):
        if not self.has_code(codesystem_id,code):
            return None
        else:
            return self.codesystems[codesystem_id][code]

        
    def merge_code(self,codesystem_id,code:str,display:str,definition=None,designation=[],propertyString=[]):
        code_defn = {'display':display,
                    'definition':definition,
                    'designation':designation,
                    'propertyString': propertyString}
        return self.merge_code(codesystem_id,code,code_defn)
        
    def merge_code(self,codesystem_id,code:str,new_code:dict):
        if not self.has_codesystem(codesystem_id):
            self.logger.info("tyring to create code on non-registered code-system:" + codesystem_id)
            return False
        if not 'display' in new_code:
            self.logger.info("trying to create code with out display:" + code)
            return False
        if not 'definition' in new_code:
            new_code['defintion'] = None
        if not 'designation' in new_code:
            new_code['designation'] = []
        if not 'propertyString' in new_code:
            new_code['propertyString'] = []
        if not 'propertyCode' in new_code:
            new_code['propertyCode'] = []
        if not 'propertyCoding' in new_code:
            new_code['propertyCoding'] = []

        existing_code = self.get_code(codesystem_id,code)
        if existing_code:
            self.logger.info("Trying to create a code '" + code + "'when it already exists in " + codesystem_id)
            if not existing_code['display'] == display:
                self.logger.info("Mismatched display of code '" + code + "': '" + existing_code['display'] \
                        + "' !=  '" + new_code['display'] + "'")
            if not self.is_blank(existing_code['defintion']) and not self.is_blank(new_code['defintion']) \
               and not existing_code['definition'] == new_code['definition']:
                self.logger.info("Mismatched definitions of code '" + code + "': '" + existing_code['definition'] \
                        + "' !=  '" + new_code['definition'] + "'")
            new_code['designation'] += existing_code['designation']
            new_code['propertyString'] += existing_code['propertyString']
            new_code['propertyCode'] += existing_code['propertyCode']
        self.codesystems[codesystem_id][code] = new_code
        return True

    def add_properties(self,codesystem_id:str,vals:dict):
        for k,v in vals.items():
            self.add_property(codesystem_id,k,v)
      
    def add_property(self,codesystem_id:str,k:str,v):
        self.codesystem_properties[codesystem_id][k] = v

    def add_dict(self,codesystem_id:str,inputs:dict):
        result = True
        for code,expr in inputs.items():
            result &= self.merge_code(codesystem_id,code,expr)
        return result

    def has_code(self,codesystem_id:str,code:str):
        return codesystem_id in self.codesystems and code in self.codesystems[codesystem_id]


    def escape(input):
        return stringer.escape(input)
        
    def escape_code(self,input):  
        original = input
        if ( not (isinstance(input,str))):
            return None
        input = input.strip()
        input = re.sub(r"['\"]","",input)
        #SUSHI BUG on processing codes with double quote.  sushi fails
        #Example \"Bivalent oral polio vaccine (bOPV)–inactivated polio vaccine (IPV)\" schedule (in countries with high vaccination coverage [e.g. 90–95%] and low importation risk [where neighbouring countries and/or countries that share substantial population movement have a similarly high coverage])" 
        
        input = re.sub(r"\s+"," ",input)
        if len(input) > 245:
            # max filename size is 255, leave space for extensions such as .fsh
            self.logger.info("ERROR: name of id is too long.hashing: " + input)        
            input = stringer.to_hash(input,245)
            self.logger.info("Escaping code " + original + " to " + input )
        return input

    def render_valueset_allcodes(self,vs_id,title,cs_id):
        valueset = 'ValueSet: ' + stringer.escape(vs_id) + '\n'
        valueset += 'Title: "' + stringer.escape(title) + '"\n'
        valueset += 'Description:  "Value Set for ' + stringer.escape(title) + '. Autogenerated from DAK artifacts"\n'
        #valueset += 'Usage: #definition\n'
        #valueset += "* publisher = \"" + stringer.escape(self.publisher) + "\"\n" 
        #valueset += "* experimental = false\n"
        #valueset += "* version = \"" + self.version + "\"\n"
        valueset += '* ^status = #active\n'
        valueset += '* include codes from system ' + stringer.escape(cs_id) + '\n'
        return valueset

    def render_vs_from_list(self,id:str, codesystem_id:str, title:str, codes):
        
        valueset = 'ValueSet: ' + stringer.escape(id) + '\n'
        valueset += 'Title: "' + stringer.escape(title) + '"\n'
        valueset += 'Description:  "Value Set for ' + stringer.escape(title) + '. Autogenerated from DAK artifacts"\n'
        #valueset += "Usage: #definition\n"
        #valueset += "* publisher = \"" + stringer.escape(self.publisher) + "\"\n" 
        #valueset += "* experimental = false\n"
        #valueset += "* version = \"" + self.version + "\"\n"
        valueset += '* ^status = #active\n'
        for code in codes:
            valueset += '* include ' + stringer.escape(codesystem_id) + '#"' + stringer.escape_code(code) + '"\n'            
        return valueset

    def render_vs_from_dict(self,id:str, title:str, codelist:dict , properties:dict = {}):
        self.logger.info("trying to register codesystem " + id )
        if not self.register(id,title):
            self.logger.info("Skipping CS and VS for " + id + " could not register")
            return False
        if not self.add_dict(id,codelist):
            self.logger.info("Skipping CS and VS for " + id + " could not add dictionary")
            return False
        self.add_properties(id,properties)
        return self.render_valueset_allcodes(id,title,id)
    
    def render_codesystems(self):
        result = {}
        for id in self.codesystems.keys():
            result[id] =  self.render_codesystem(id)
        return result
    
    def render_codesystem(self,id:str):
        if not self.has_codesystem(id):
            self.logger.info("Trying to render absent codesystem " + id)
            return False
        title = self.get_title(id)
        codesystem = 'CodeSystem: ' + stringer.escape(id) + '\n'
        codesystem += 'Title: "' + stringer.escape(title) + '"\n'
        codesystem += 'Description:  "CodeSystem for ' + stringer.escape(title) + '. Autogenerated from DAK artifacts"\n'
        #codesystem += "* versiobn = \"" + self.version + "\"\n"
        #codesystem += "* publisher = \"" + stringer.escape(self.publisher) + "\"\n" 
        #codesystem += '* ^experimental = false\n'
        codesystem += '* ^caseSensitive = false\n'
        codesystem += '* ^status = #active\n'
        for code,vals in self.get_properties(id).items():
            codesystem += '* ^property[+].code = #"' + stringer.escape_code(code) + '"\n'
            for k,v in vals.items():
                codesystem += '* ^property[=].' + k + ' = ' + v + "\n" # user is responsible for content

        for code,val in self.get_codes(id).items():
            if isinstance(val,str):
                codesystem += '* #"' + stringer.escape_code(code) +  '" "' + stringer.escape(name) + '"\n'
            elif isinstance(val,dict)  and 'display' in val:
                codesystem += '* #"' + stringer.escape_code(code) +  '" "' + stringer.escape(val['display']) + '"\n'
                if 'definition' in val and not stringer.is_blank(val):
                    codesystem += '  * ^definition = """' + val['definition'] + '\n"""\n'
                if 'designation' in val and isinstance(val['designation'],list):
                    for d_val in val['designation']:
                        if not isinstance(d_val,dict) or not 'value' in d_val:
                            continue
                        codesystem += '  * ^designation[+].value = ' + d_val['value'] + "\n"
                        d_val.pop('value')
                        for k,v in d_val.items():
                            codesystem += '  * ^designation[=].' + k + " = " + v + "\n"

                if 'propertyString' in val and isinstance(val['propertyString'],list):
                    for p in val['propertyString']:
                        if not isinstance(p,dict) or not 'code' in p or not 'value' in p:
                            continue
                        codesystem += '  * ^property[+].code = #"' + stringer.escape_code(p['code']) +  '"\n'
                        codesystem += '  * ^property[=].valueString = "' + stringer.escape(p['value']) +  '"\n'

                if 'propertyCode' in val and isinstance(val['propertyCode'],list):
                    for p in val['propertyCode']:
                        if not isinstance(p,dict) or not 'code' in p or not 'value' in p:
                            continue
                        codesystem += '  * ^property[+].code = #"' + stringer.escape_code(p['code']) +  '"\n'
                        codesystem += '  * ^property[=].valueCode = "' + stringer.escape_code(p['value']) +  '"\n'

                if 'propertyCoding' in val and isinstance(val['propertyCoding'],list):
                    for p in val['propertyCode']:
                        if not isinstance(p,dict) or not 'code' in p or not 'value' in p \
                           or not isinstance(p['value'],dict):
                            continue
                        codesystem += '  * ^property[+].code = #"' + stringer.escape_code(p['code']) +  '"\n'
                        for coding_k,coding_v in p['value'].items():
                            codesystem += '  * ^property[=].valueCoding.' + coding_key + ' = '
                            if coding_key == 'code':
                                codesystem +=  '#' + stringer.escape_code(coding_value) +  '\n'
                            elif coding_key =='userSelected':
                                codesystem +=  coding_value +  '\n'
                            else:
                                codesystem +=  '"' + stringer.escape(coding_value) +  '\n'
            else:
                self.logger.info("  failed to add code (expected string or dict with 'display' property)" + str(code))
                self.logger.info(val)
        return codesystem

