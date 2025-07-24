"""
Base Extractor Class for FHIR Resource Generation

This module provides the abstract base class for all data extractors in the SMART
guidelines system. Extractors process various input formats (Excel, text files, etc.)
and convert them into FHIR-compatible resources.

The base extractor handles common functionality like file processing loops,
alias management, and data frame processing utilities.

Author: WHO SMART Guidelines Team
"""

import logging
import os
import re
from typing import Dict, List, Optional, Tuple, Any, Generator

import pandas as pd
import stringer
from installer import installer


class extractor(object):
    """
    Abstract base class for all data extractors.
    
    This class provides common functionality for processing input files and
    generating FHIR resources. Subclasses should implement specific extraction
    logic for their data formats.
    
    Attributes:
        inputfile_name (str): Currently processed input file name
        class_cs (str): Default CodeSystem URL for this extractor
        installer (installer): The installer instance for resource management
    """
    
    inputfile_name: str = ""
    class_cs: str = "http://smart.who.int/base/CodeSystem/CDHIv1"
    
    def __init__(self, installer: installer):
        """
        Initialize the extractor with an installer instance.
        
        Sets up aliases and logging for the extraction process.
        
        Args:
            installer: The installer instance for managing FHIR resources
        """
        self.installer = installer
        
        # Set up aliases for this extractor
        aliases = self.installer.get_base_aliases()
        aliases.extend(self.get_aliases())
        logging.getLogger(self.__class__.__name__).info("Aliases" + str(aliases))
        self.installer.add_aliases(aliases)

    def find_files(self) -> List[str]:
        """
        Return list of files to be processed by this extractor.
        
        This is an abstract method that should be overridden by subclasses
        to specify which files they can process.
        
        Returns:
            List of file paths to process
        """
        return []

    def extract(self) -> bool:
        """
        Main extraction method that processes all files found by find_files().
        
        Iterates through each file returned by find_files() and calls
        extract_file() for each one. Handles logging of file processing.
        
        Returns:
            True if extraction completed successfully
        """
        for inputfile_name in self.find_files():
            logging.getLogger(self.__class__.__name__).info('IF=' + inputfile_name)
            self.inputfile_name = inputfile_name
            self.extract_file()
        return True

    def extract_file(self) -> None:
        """
        Process a single input file.
        
        This is an abstract method that should be overridden by subclasses
        to implement specific file processing logic.
        """
        pass

    def get_aliases(self) -> List[str]:
        """
        Return list of FSH aliases specific to this extractor.
        
        Subclasses can override this to provide extractor-specific aliases
        that will be added to the base aliases.
        
        Returns:
            List of FSH alias definitions
        """
        return []

    def generate_pairs_from_lists(self, lista: List[Any], listb: List[Any]) -> Generator[Tuple[Any, Any], None, None]:
        """
        Generate all possible pairs from two lists using Cartesian product.
        
        This is a utility method for generating combinations when trying to
        match data across different potential values.
        
        Args:
            lista: First list of values
            listb: Second list of values
            
        Yields:
            Tuple pairs of (a, b) for all combinations
            
        Reference:
            https://www.youtube.com/watch?v=EnSu9hHGq5o&t=1184s&ab_channel=NextDayVideo
        """
        for a in lista:
            for b in listb:
                yield a, b

    def generate_pairs_from_column_maps(self, column_maps: Dict[str, List[str]]) -> Generator[Tuple[str, str], None, None]:
        """
        Generate pairs from column mapping dictionaries.
        
        Takes a dictionary where keys are desired column names and values are
        lists of possible column names, and generates all possible pairs.
        
        Args:
            column_maps: Dictionary mapping desired names to possible names
            
        Yields:
            Tuple pairs of (desired_name, possible_name)
        """
        for desired_column_name, possible_column_names in column_maps.items():
            for possible_column_name in possible_column_names:
                yield str(desired_column_name), str(possible_column_name)

    def retrieve_data_frame_by_headers(self, column_maps: Dict[str, List[str]], 
                                     sheet_names: List[str], 
                                     header_offsets: List[int] = [0, 1, 2]) -> Optional[pd.DataFrame]:
        """
        Retrieve a pandas DataFrame from Excel file by matching column headers.
        
        This method attempts to find the correct sheet and header row in an Excel
        file by matching expected column names (case-insensitive, normalized).
        
        Args:
            column_maps: Dictionary where keys are desired column names and values
                        are lists of possible matching column names
            sheet_names: List of potential Excel sheet names to search
            header_offsets: List of row numbers to try as header rows (default: [0,1,2])
            
        Returns:
            DataFrame with normalized column names if successful, None if no match found
            
        Example:
            column_maps = {
                'reqid': ["Requirement ID"],
                'activityid-and-name': ["Activity ID and name", "Activity ID and description"],
                'as-a': ["As a"],
                'i-want': ["I want", "I want to"],
                'so-that': ["So that"]
            }
        """
        logging.getLogger(self.__class__.__name__).info("Looking at sheets:" + " ".join(sheet_names))
        
        # Try all combinations of sheet names and header row positions
        for sheet_name, header_row in self.generate_pairs_from_lists(sheet_names, header_offsets):
            logging.getLogger(self.__class__.__name__).info(
                f"Checking sheetname/header row #: {sheet_name}/{header_row}"
            )
            
            try:
                data_frame = pd.read_excel(self.inputfile_name, sheet_name=sheet_name, header=header_row)
            except Exception as e:
                logging.getLogger(self.__class__.__name__).info(
                    f"Could not open sheet {sheet_name} on header row {header_row}"
                )
                logging.getLogger(self.__class__.__name__).info(str(e))
                continue

            # Map current column names to canonicalized/normalized column names
            true_column_map = {}
            
            for column_name in list(data_frame):
                if stringer.is_blank(column_name):
                    continue
                    
                column_id = stringer.name_to_lower_id(column_name)

                # Try to match this column with desired column names
                for desired_column_name, possible_column_name in self.generate_pairs_from_column_maps(column_maps):
                    possible_column_id = stringer.name_to_lower_id(possible_column_name)
                    if possible_column_id == column_id:
                        # Found a match
                        logging.getLogger(self.__class__.__name__).info(
                            f"Matched input sheet column {column_name} with desired column {desired_column_name}"
                        )
                        true_column_map[column_name] = desired_column_name
                        break
                        
                if column_name not in true_column_map:
                    # This column is not needed, drop it to normalize downstream processing
                    data_frame.drop(column_name, axis='columns', inplace=True)
                    logging.getLogger(self.__class__.__name__).info(f"Dropped: {column_name}")
                    continue

            logging.getLogger(self.__class__.__name__).info(f"Mapping columns: {true_column_map}")
            
            # Rename columns to normalized names
            data_frame = data_frame.rename(columns=true_column_map)
            
            # Check if we have all required columns
            if list(data_frame) != list(column_maps.keys()):
                continue

            logging.getLogger(self.__class__.__name__).info(
                f"Found desired column headers at sheet name / header row: {sheet_name}/{header_row}"
            )
            # Successfully found matching columns, return the normalized DataFrame
            return data_frame

        # Tried all combinations and failed to find a match
        return None

    def log(self, *statements) -> None:
        """
        Log statements with extractor context.
        
        Adds the extractor class name and current file being processed as a prefix
        to log messages for better traceability.
        
        Args:
            *statements: Variable number of statements to log
        """
        prefix = f"{self.__class__.__name__}({os.path.basename(self.inputfile_name)}):"
        
        for statement in statements:
            statement = str(statement).replace("\n", "\n\t")
            self.installer.log(prefix + statement)
            prefix = "\t"

    def qa(self, msg: str) -> None:
        """
        Log a quality assurance message.
        
        Delegates to the installer's QA logging functionality.
        
        Args:
            msg: QA message to log
        """
        self.installer.qa(msg)