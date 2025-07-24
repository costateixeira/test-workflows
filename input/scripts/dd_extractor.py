"""
Data Dictionary Extractor for SMART Guidelines

This module provides functionality to extract and process data dictionary
definitions for the SMART guidelines system. It handles structured data
definitions and converts them into FHIR resources for clinical data
standardization and interoperability.

The extractor processes data dictionary files to ensure consistent data
element definitions across the SMART guidelines implementation.

Author: SMART Guidelines Team
"""
import stringer
import sys
import glob as glob
import re
import pandas as pd
import logging
from extractor import extractor 
from installer import installer

class dd_extractor(extractor):
    """
    Extractor for data dictionary processing.

    This extractor processes data dictionary files containing structured
    definitions of clinical data elements, converting them into appropriate
    FHIR resources for standardized data exchange.
    """
    xslt_file  = "includes/bpmn2fhirfsh.xsl"
    dictionaries = {}

    def __init__(self,installer:installer):
        super().__init__(installer)        



    def find_files(self):
        return glob.glob("input/dictionary/*xlsx")


    def extract_file(self):
        cover_column_maps = {
            'tab':["Tabs"],
            'description': ["Description"],
        }
        sheet_names = ['COVER']
        cover_sheet = self.retrieve_data_frame_by_headers(cover_column_maps,sheet_names,range(0,20))

        if (not  self.extract_dictionaries(cover_sheet)):

            self.logger.info("Could not extract data dicionaries in: " + self.inputfile_name)
            return False        
        return True



    def extract_dictionaries(self,cover_sheet:pd.DataFrame):
        if cover_sheet is None:
            self.logger.info("Could not load cover sheet")      
            return False
        descriptions = {}
        result = True            
        for index, row in cover_sheet.iterrows():
            has_non_empty = (isinstance(row["tab"],str) and bool(row["tab"]) )  \
                or (isinstance(row["description"],str) and bool(row["description"])  )

            if not has_non_empty:
                self.logger.info("Reached end of cover index table")
                break
            result &= self.extract_dictionary(row['tab'],row["description"])

        return result




    def extract_dictionary(self,tab:str,definition:str):        
        parts = tab.split(" ",1)
        if (len(parts) != 2):
            self.logger.info("Skipping data dicionary name: " + tab)
            return False
        process_id = parts[0].strip()
        process_name = parts[1].strip()
        process_code = process_id.split(".")[-1]

        dd_column_maps = {
            'code': ["Data element ID"],
            'display': ["Data element label"],
            'definition': ["Data element description","Description", "Description and definition","Definition"\
                        ,"Data element definition"],
            'dts': ["Linkages to decision-support tables","Linkages to decision tables"],
        'indicators': ["Linkages to aggregate indicators","Linkages to indicators"],
            'comment' :['Annotations','Comment','Comments','Annonation']
        }
        if not process_code == 'BP':            
            dd_column_maps['tasks']=["Activity ID"]

        try:
            dd_sheet = self.retrieve_data_frame_by_headers(dd_column_maps,[tab],range(0,2))
            if not dd_sheet:
                self.logger.info("Could not retrieve data dictionary by headers: " + str(cover_column_maps))                     
                return False            
        except Exception as e:
            self.logger.info("Could not open sheet " + tab )
            self.logger.info(e)
            return False

        csm = self.installer.get_codesystem_manager()
        vs_id = self.installer.dd_prefix + "." + tab_id
        vs_description = f"Data Dictionary ValueSet {tab} auto-extrated from Digital Adaptation Kit.\n\n{definition}"
        vs_codes = []        
        for row in dd_sheet.iterrows():
            if stringer.is_blank(row['code']) or stringer.is_blank(row['display']):
                continue            
            code = row['code']
            vs_codes += [code]

            display = row['display']
            definition = row['definition']
            code_definition = {'display':display
                        ,'definition':definition
                        ,'propertyString':[]
                        ,'propertyCode':[]
                        ,'propertyCoding':[]}
            code_definition_extra = ""
            if not self.is_blank(row['comment']):
                code_definition['propertyString']+= [{'code':'comment','value':row['comment'] }]

            if process_code == 'BP': #we are in the Businnes Process Overview sheet
                self.process_code_overview(code,row,code_definition)
            else:
                # this is not the business process overview data dictionary
                self.process_code_regular(code,row,code_definition)
            csm.merge_code_with_params(self.installer.dd_prefix,code, code_definition)

        valueset = csm.render_vs_from_list(vs_id,self.installer.dd_prefix,code,vs_description,vs_codes)
        if not valueset:
            self.logger.info("Could not generate VS from list")
            return False
        self.installer.add_resource('valuesets',vs_id,valueset)
        return True



    def process_code_overview(self,code,row,code_definition:dict):
        code_parts = code.strip().split(".")
        if (len(code_parts) != 2):
            self.logger.info("Skipping data element as could not get well formed code of form <DAK-PREFIX>.<PROCESS> : " + code)
            return False
        prefix = code_parts[0]
        code_process = code_parts[1]
        if not re.search(r'\d', code_process):
            #this is a code for a business process                 
            link_base = self.installer.get_ig_canonical()
            link_svg = f"{link_base}/{display}.svg"
            link_bpmn = f"{link_base}/{display}.bpmn"
            code_definition['defintion'] += f"\n\nSee Business Process {display}:" \
                + f" [SVG]({link_svg}) [BPMN]({link_bpmn})\n"
            img_alt = stringer.xml_escape(display)
            code_definition['defintion'] +=  f"<img src='{link_svg}' class='bpmn' alt='{img_alt}'/>\n"
        return True

    def process_code_regular(self,code,row,code_definition:dict):

        tasks =  row['tasks'].split(",") if not self.is_blank(row['tasks'])  else []
        if len(tasks) > 0:
            task_descriptions = []
            for task in tasks.split("OR"):
                task = task.strip()
                if stringer.is_blank(task) or stringer.is_dash(task):
                    continue
                task_parts = task.split(" ",1)
                if (len(task_parts) != 2):
                    self.logger.info("Skipping data element task as could not get task id and name: " + task)
                    continue
                task_id = task_parts[0].strip()
                task_name = task_parts[1].strip()
                task_url = 'ValueSet-' + self.installer.dd_prefix + "." + task_id + '.html'
                task_descriptions += [f"* Used in task [{task_name}]({task_url})\n"]

                task_coding = {'code':task_id,'system':self.installer.dd_prefix}
                code_definition['propertyCoding'] += [{'code':'task-code','value':task_coding}]
            if len(task_descriptions) > 0:
                code_definition['definition'] += "\n\nUsed in the following tasks:\n" + "\n".join(task_descriptions)


        dts =  row['dts'].split(",") if not self.is_blank(row['dts'])  else []
        if len(dts) > 0:
            dt_descriptions = []
            for dt in dts:
                dt = dt.strip()
                if stringer.is_blank(dt):
                    continue
                dt_id = dt
                dt_profile_url = f"StructureDefinition-{dt_id}.html"
                dt_descriptions += [f"Decision Table profile: [{dt_id}]({dt_url})\n"]
                #really we need to check to see if there are any decision tables, but we won't know that until we process the DT
                #but thats much later.  at least the profile should show any instantiations
                # dt_plandefinition_url = f"PlanDefinitionSt-{dt_id}.html"
                # dt_descriptions += [f"Decision Table instance: [{dt_id}]({dt_plandefinition_url})\n"]
                dt_coding = {'code':dt_id,'system':self.installer.dd_prefix}
                code_definition['propertyCoding'] += [{'code':'decision-table-code','value':dt_coding}]
                code_definition['propertyString'] += [{'code':'decision-table','value':dt_description}]
            if len(dt_descriptions) > 0:
                code_definition['definition'] += "\n\nUsed in the following decision tables:\n" + "\n".join(dt_descriptions)


        indicators =  row['indicators'].split(",") if not self.is_blank(row['indicators']) else []
        if len(indicators) > 0:
            indicators_description = "Used in decision tables: "
            for indicator in indicators:
                indicator = indicator.strip()
                if stringer.is_blank(indicator):
                    continue
                indicator_id = indicator
                indicator_url = f"Measure-{indicator_id}.html"
                indicator_descriptions += [f"[{indicator_id}]({indicator_url})\n"]
                indicator_coding = {'code':indicator_id,'system':self.installer.dd_prefix}
                code_definition['propertyCoding'] += [{'code':'decision-table-code','value':indicator_coding}]
            if len(indicator_descriptions) > 0:
                code_definition['definition'] += "\n\nUsed in the following indicators:\n" + "\n".join(indicator_descriptions)
        return True
