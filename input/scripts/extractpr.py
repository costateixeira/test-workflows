#!/usr/bin/env python3
"""
Personas Extractor for SMART Guidelines DAK Component 2

This module provides functionality to extract and process personas/actors
content from PDF files for the SMART guidelines system. It handles structured
persona definitions and converts them into FHIR ActorDefinition resources for
clinical workflow standardization and interoperability.

The extractor processes PDF files containing WHO SMART Guidelines documentation
to identify and extract Generic Personas tables and Related Personas tables,
typically found in section 2.1 of WHO guideline documents.

Target content includes:
- Generic Personas tables (Table 2)
- Related Personas tables (Table 3) 
- Actor definitions and descriptions
- Role-based healthcare personas

Author: SMART Guidelines Team
"""

from typing import List, Dict, Optional, Any, Tuple
import stringer
import sys
import glob as glob
import re
import pandas as pd
import logging
import pdfplumber
from extractor import extractor 
from installer import installer


class extractpr(extractor):
    """
    Extractor for personas/actors processing from PDF files.

    This extractor processes PDF files containing SMART Guidelines documentation
    to extract Generic Personas and Related Personas tables, converting them into
    appropriate FHIR ActorDefinition resources for standardized healthcare workflow
    implementations.
    
    The extractor looks for specific patterns in WHO guideline PDFs:
    - Section 2.1 "Generic Personas" or "Targeted Generic Personas"
    - Table 2 containing generic personas definitions
    - Table 3 containing related personas definitions
    """

    def __init__(self, installer: installer) -> None:
        """Initialize the personas extractor with installer instance."""
        super().__init__(installer)

    def get_aliases(self) -> List[str]:
        """
        Provide FHIR aliases specific to personas/actors processing.
        
        Returns:
            List of alias definitions for FHIR shortcuts used in personas processing
        """
        return [
            'Alias: $pubStatus = http://hl7.org/fhir/publication-status',
            'Alias: $actorType = http://hl7.org/fhir/examplescenario-actor-type', 
            'Alias: $SGActor = http://smart.who.int/base/StructureDefinition/SGActor',
            'Alias: $PersonaType = http://smart.who.int/base/CodeSystem/PersonaType'
        ]

    def find_files(self) -> List[str]:
        """
        Discover PDF files to be processed by this extractor.
        
        Searches for PDF files in the input/personas directory that contain
        SMART Guidelines documentation with personas/actors content.
        
        Returns:
            List of PDF file paths to process
        """
        return glob.glob("input/personas/*.pdf")

    def extract_file(self) -> None:
        """
        Process a single PDF file to extract personas/actors content.
        
        Main extraction logic that opens the PDF file and searches for
        personas tables using multiple strategies to handle different
        document formats and layouts.
        """
        try:
            self.logger.info(f"Processing PDF file: {self.inputfile_name}")
            self.extract_personas_from_pdf()
        except Exception as e:
            self.logger.error(f"Could not process PDF file {self.inputfile_name}: {e}")
            self.qa(f"Failed to extract personas from {self.inputfile_name}: {str(e)}")

    def extract_personas_from_pdf(self) -> None:
        """
        Extract personas/actors content from the current PDF file.
        
        Uses pdfplumber to parse PDF content and extract personas tables.
        Searches for Generic Personas and Related Personas sections and
        converts found data into FHIR ActorDefinition resources.
        """
        personas_data = []
        
        try:
            with pdfplumber.open(self.inputfile_name) as pdf:
                self.logger.info(f"Opened PDF with {len(pdf.pages)} pages")
                
                # Search through all pages for personas content
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text() if page.extract_text() else ""
                    
                    # Look for personas section indicators
                    if self._is_personas_page(page_text):
                        self.logger.info(f"Found personas content on page {page_num + 1}")
                        
                        # Extract tables from this page
                        tables = page.extract_tables()
                        if tables:
                            personas_data.extend(self._process_personas_tables(tables, page_num + 1))
                        
                        # Also try text-based extraction for cases where table extraction fails
                        text_personas = self._extract_personas_from_text(page_text, page_num + 1)
                        if text_personas:
                            personas_data.extend(text_personas)
            
            if personas_data:
                self.logger.info(f"Extracted {len(personas_data)} personas from PDF")
                self._create_fhir_resources(personas_data)
            else:
                self.logger.warning(f"No personas data found in {self.inputfile_name}")
                self.qa(f"No personas tables found in PDF: {self.inputfile_name}")
                
        except Exception as e:
            self.logger.error(f"Error processing PDF {self.inputfile_name}: {e}")
            raise

    def _is_personas_page(self, page_text: str) -> bool:
        """
        Determine if a page contains personas/actors content.
        
        Args:
            page_text: Text content of the PDF page
            
        Returns:
            True if the page appears to contain personas content
        """
        # Look for key indicators of personas content
        indicators = [
            r"generic\s+personas?",
            r"related\s+personas?", 
            r"targeted\s+generic\s+personas?",
            r"table\s+[23].*personas?",
            r"section\s+2\.1",
            r"actors?\s+and\s+personas?",
            r"healthcare\s+personas?"
        ]
        
        text_lower = page_text.lower()
        for indicator in indicators:
            if re.search(indicator, text_lower):
                self.logger.debug(f"Found personas indicator: {indicator}")
                return True
        return False

    def _process_personas_tables(self, tables: List[List[List[str]]], page_num: int) -> List[Dict[str, Any]]:
        """
        Process extracted tables to identify and parse personas data.
        
        Args:
            tables: List of tables extracted from the PDF page
            page_num: Page number for logging
            
        Returns:
            List of personas data dictionaries
        """
        personas_data = []
        
        for table_idx, table in enumerate(tables):
            if not table or len(table) < 2:  # Need at least header + 1 data row
                continue
                
            self.logger.debug(f"Processing table {table_idx + 1} on page {page_num}")
            
            # Try to identify the table structure
            header_row = table[0] if table else []
            if self._is_personas_table_header(header_row):
                self.logger.info(f"Found personas table on page {page_num}, table {table_idx + 1}")
                table_personas = self._parse_personas_table(table, page_num, table_idx + 1)
                personas_data.extend(table_personas)
        
        return personas_data

    def _is_personas_table_header(self, header_row: List[str]) -> bool:
        """
        Check if a table header row indicates a personas table.
        
        Args:
            header_row: First row of the table
            
        Returns:
            True if this appears to be a personas table header
        """
        if not header_row:
            return False
            
        # Join all header cells and check for personas-related terms
        header_text = " ".join([cell.lower() if cell else "" for cell in header_row])
        
        # Look for key header terms
        header_indicators = [
            "persona",
            "actor", 
            "role",
            "description",
            "responsibility",
            "user type",
            "healthcare provider",
            "clinical role"
        ]
        
        for indicator in header_indicators:
            if indicator in header_text:
                return True
        return False

    def _parse_personas_table(self, table: List[List[str]], page_num: int, table_num: int) -> List[Dict[str, Any]]:
        """
        Parse a personas table to extract structured data.
        
        Args:
            table: Table data as list of rows
            page_num: Page number for reference
            table_num: Table number on the page
            
        Returns:
            List of personas data dictionaries
        """
        personas = []
        
        if len(table) < 2:
            return personas
            
        header_row = table[0]
        data_rows = table[1:]
        
        # Map common column variations to standard names
        column_map = self._create_column_mapping(header_row)
        
        self.logger.debug(f"Column mapping: {column_map}")
        
        for row_idx, row in enumerate(data_rows):
            if not row or all(not cell or not cell.strip() for cell in row):
                continue  # Skip empty rows
                
            persona = self._extract_persona_from_row(row, column_map, page_num, table_num, row_idx + 2)
            if persona:
                personas.append(persona)
        
        return personas

    def _create_column_mapping(self, header_row: List[str]) -> Dict[str, int]:
        """
        Create a mapping from standard column names to table column indices.
        
        Args:
            header_row: List of header cell values
            
        Returns:
            Dictionary mapping standard names to column indices
        """
        column_map = {}
        
        for idx, header in enumerate(header_row):
            if not header:
                continue
                
            header_lower = header.lower().strip()
            
            # Map various header names to standard column types
            if any(term in header_lower for term in ["persona", "actor", "role", "name"]):
                column_map["name"] = idx
            elif any(term in header_lower for term in ["description", "desc", "definition", "details"]):
                column_map["description"] = idx
            elif any(term in header_lower for term in ["responsibility", "responsibilities", "duties"]):
                column_map["responsibilities"] = idx
            elif any(term in header_lower for term in ["type", "category", "classification"]):
                column_map["type"] = idx
            elif any(term in header_lower for term in ["example", "examples", "instances"]):
                column_map["examples"] = idx
        
        return column_map

    def _extract_persona_from_row(self, row: List[str], column_map: Dict[str, int], 
                                  page_num: int, table_num: int, row_num: int) -> Optional[Dict[str, Any]]:
        """
        Extract persona data from a single table row.
        
        Args:
            row: Table row data
            column_map: Mapping of column types to indices
            page_num: Page number for reference
            table_num: Table number for reference  
            row_num: Row number for reference
            
        Returns:
            Persona data dictionary or None if invalid
        """
        persona = {
            "source_location": f"Page {page_num}, Table {table_num}, Row {row_num}",
            "source_file": self.inputfile_name
        }
        
        # Extract data based on column mapping
        if "name" in column_map and column_map["name"] < len(row):
            name = row[column_map["name"]]
            if name and name.strip():
                persona["name"] = name.strip()
            else:
                return None  # Must have a name/persona identifier
        else:
            return None
            
        if "description" in column_map and column_map["description"] < len(row):
            desc = row[column_map["description"]]
            if desc and desc.strip():
                persona["description"] = desc.strip()
                
        if "responsibilities" in column_map and column_map["responsibilities"] < len(row):
            resp = row[column_map["responsibilities"]]
            if resp and resp.strip():
                persona["responsibilities"] = resp.strip()
                
        if "type" in column_map and column_map["type"] < len(row):
            ptype = row[column_map["type"]]
            if ptype and ptype.strip():
                persona["type"] = ptype.strip()
                
        if "examples" in column_map and column_map["examples"] < len(row):
            examples = row[column_map["examples"]]
            if examples and examples.strip():
                persona["examples"] = examples.strip()
        
        self.logger.debug(f"Extracted persona: {persona['name']}")
        return persona

    def _extract_personas_from_text(self, page_text: str, page_num: int) -> List[Dict[str, Any]]:
        """
        Fallback method to extract personas from plain text when table extraction fails.
        
        Args:
            page_text: Text content of the page
            page_num: Page number for reference
            
        Returns:
            List of personas data dictionaries
        """
        personas = []
        
        # Look for structured text patterns that might indicate personas
        # This is a fallback for when table extraction doesn't work
        lines = page_text.split('\n')
        
        current_persona = None
        for line_idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Look for persona name patterns (e.g., bullet points, numbered items)
            if re.match(r'^[•·\-\*]\s*(.+)', line) or re.match(r'^\d+\.\s*(.+)', line):
                # This might be a persona name
                if current_persona:
                    personas.append(current_persona)
                
                persona_name = re.sub(r'^[•·\-\*\d\.\s]+', '', line)
                current_persona = {
                    "name": persona_name,
                    "source_location": f"Page {page_num}, Line {line_idx + 1}",
                    "source_file": self.inputfile_name,
                    "description": ""
                }
            elif current_persona and line and not line.lower().startswith(('table', 'figure')):
                # This might be a description line
                if current_persona["description"]:
                    current_persona["description"] += " " + line
                else:
                    current_persona["description"] = line
        
        # Add the last persona if any
        if current_persona:
            personas.append(current_persona)
        
        if personas:
            self.logger.info(f"Extracted {len(personas)} personas from text on page {page_num}")
        
        return personas

    def _create_fhir_resources(self, personas_data: List[Dict[str, Any]]) -> None:
        """
        Create FHIR ActorDefinition resources from extracted personas data.
        
        Args:
            personas_data: List of personas data dictionaries
        """
        self.logger.info(f"Creating FHIR resources for {len(personas_data)} personas")
        
        # Create a CodeSystem for persona types if we have type information
        persona_types = set()
        for persona in personas_data:
            if "type" in persona and persona["type"]:
                persona_types.add(persona["type"])
        
        if persona_types:
            self._create_persona_types_codesystem(persona_types)
        
        # Create ActorDefinition resources for each persona
        for persona in personas_data:
            self._create_actor_definition(persona)

    def _create_persona_types_codesystem(self, persona_types: set) -> None:
        """
        Create a FHIR CodeSystem for persona types.
        
        Args:
            persona_types: Set of unique persona type strings
        """
        cs_id = "PersonaTypes"
        title = "SMART Guidelines Persona Types"
        
        # Create a dictionary for the codesystem manager
        types_dict = {}
        for ptype in persona_types:
            # Create a code from the type name
            code = stringer.name_to_id(ptype)
            types_dict[code] = ptype
        
        self.installer.get_codesystem_manager().add_cs_and_vs_from_dict(
            cs_id, title, types_dict
        )
        
        self.logger.info(f"Created CodeSystem {cs_id} with {len(types_dict)} persona types")

    def _create_actor_definition(self, persona: Dict[str, Any]) -> None:
        """
        Create a FHIR ActorDefinition resource for a single persona.
        
        Args:
            persona: Persona data dictionary
        """
        # Create a unique ID for this persona
        persona_id = stringer.name_to_id(persona["name"])
        
        # Build the FHIR ActorDefinition resource in FSH format
        fsh_content = self._generate_actor_definition_fsh(persona_id, persona)
        
        # Add the resource via the installer
        self.installer.add_resource('actors', persona_id, fsh_content)
        
        self.logger.info(f"Created ActorDefinition resource: {persona_id}")

    def _generate_actor_definition_fsh(self, persona_id: str, persona: Dict[str, Any]) -> str:
        """
        Generate FSH content for an ActorDefinition resource.
        
        Args:
            persona_id: Unique identifier for the persona
            persona: Persona data dictionary
            
        Returns:
            FSH formatted string for the ActorDefinition
        """
        fsh = f"Instance: {persona_id}\n"
        fsh += "InstanceOf: ActorDefinition\n"
        fsh += "Usage: #definition\n"
        fsh += f"* name = \"{stringer.escape_code(persona_id)}\"\n"
        fsh += f"* title = \"{stringer.escape(persona['name'])}\"\n"
        fsh += "* status = #active\n"
        fsh += "* experimental = false\n"
        fsh += "* type = #person\n"
        
        # Add description if available
        if "description" in persona and persona["description"]:
            description = persona["description"]
            # Clean up the description
            description = re.sub(r'\s+', ' ', description).strip()
            fsh += f"* description = \"{stringer.escape(description)}\"\n"
        
        # Add persona type if available
        if "type" in persona and persona["type"]:
            type_code = stringer.name_to_id(persona["type"])
            fsh += f"* topic.coding = $PersonaType#{type_code} \"{stringer.escape(persona['type'])}\"\n"
        
        # Add responsibilities as documentation if available
        if "responsibilities" in persona and persona["responsibilities"]:
            resp = persona["responsibilities"]
            resp = re.sub(r'\s+', ' ', resp).strip()
            fsh += f"* documentation = \"{stringer.escape(resp)}\"\n"
        
        # Add source information as a comment
        fsh += f"// Source: {persona['source_file']} - {persona['source_location']}\n"
        
        return fsh


if __name__ == "__main__":
    """
    Command-line interface for the personas extractor.
    """
    import sys
    from installer import installer
    
    try:
        ins = installer()
        extractor = extractpr(ins)
        
        if extractor.extract():
            print("Personas extraction completed successfully")
            if ins.install():
                print("Resources installed successfully")
            else:
                print("Error installing resources")
                sys.exit(1)
        else:
            print("Error during personas extraction")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)