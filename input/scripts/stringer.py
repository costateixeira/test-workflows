"""
String Processing Utilities for FHIR Resource Generation

This module provides utility functions for string processing, escaping, and formatting
that are commonly used when generating FHIR resources from various input formats.
Includes functions for XML/HTML escaping, code normalization, and ID generation.

Author: WHO SMART Guidelines Team
"""

import hashlib
import logging
import re
from typing import Optional, Union


def to_hash(input: str, length: int) -> str:
    """
    Create a hash-based truncated string for long identifiers.
    
    When a string is too long, this function truncates it and appends a hash
    to ensure uniqueness while staying within length limits.
    
    Args:
        input: The input string to hash
        length: Maximum desired length of the result
        
    Returns:
        Truncated string with hash suffix to ensure uniqueness
    """
    return input[:length - 10] + str(hashlib.shake_256(input.encode()).hexdigest(5))


def xml_escape(input: Union[str, None]) -> str:
    """
    Escape a string for safe use in XML content.
    
    Replaces XML special characters with their entity equivalents:
    & -> &amp;, < -> &lt;, > -> &gt;, " -> &quot;, ' -> &apos;
    
    Args:
        input: String to escape, can be None
        
    Returns:
        XML-escaped string, empty string if input is not a string
    """
    if not isinstance(input, str):
        return ""
    # see https://stackoverflow.com/questions/1546717/escaping-strings-for-use-in-xml
    return input.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;").replace("'", "&apos;")


def escape(input: Union[str, None]) -> Optional[str]:
    """
    Escape double quotes in a string for safe use in FSH/JSON contexts.
    
    Args:
        input: String to escape, can be None
        
    Returns:
        String with escaped double quotes, None if input is not a string
    """
    if not isinstance(input, str):
        return None
    return input.replace('"', r'\"')


def escape_code(input: Union[str, None]) -> Optional[str]:
    """
    Normalize and escape a code string for use as FHIR identifiers or filenames.
    
    This function:
    1. Removes quotes and extra whitespace
    2. Truncates long codes and adds hash to ensure uniqueness
    3. Handles SUSHI processing limitations with special characters
    
    Args:
        input: The code string to normalize
        
    Returns:
        Normalized code string, None if input is not a string
    """
    original = input
    if not isinstance(input, str):
        return None
        
    input = input.strip()
    # Remove quotes to avoid SUSHI processing issues
    input = re.sub(r"['\"]", "", input)
    
    # SUSHI BUG on processing codes with double quote. sushi fails
    # Example \"Bivalent oral polio vaccine (bOPV)–inactivated polio vaccine (IPV)\" schedule...
    
    # Normalize whitespace
    input = re.sub(r"\s+", " ", input)
    
    if len(input) > 245:
        # max filename size is 255, leave space for extensions such as .fsh
        logging.getLogger(__name__).info("ERROR: name of id is too long.hashing: " + input)
        input = to_hash(input, 245)
        logging.getLogger(__name__).info("Escaping code " + original + " to " + input)
    
    return input


def markdown_escape(input: Union[str, None]) -> str:
    """
    Escape a string for safe use in Markdown content.
    
    Specifically handles triple quotes which can break Markdown formatting.
    
    Args:
        input: String to escape, can be None
        
    Returns:
        Markdown-escaped string, single space if input is not a string
    """
    if not isinstance(input, str):
        return " "
    input = input.replace('"""', '\\"\\"\\"')
    return input


def ruleset_escape(input: str) -> str:
    """
    Escape a string for use in FSH rulesets.
    
    Rulesets have specific formatting requirements that need special escaping.
    
    Args:
        input: String to escape for ruleset use
        
    Returns:
        Escaped string suitable for FSH rulesets
    """
    # strings in rulesets are handled poorly
    input = input.replace(",", "\\,")
    input = input.replace("'", "")
    input = input.replace("(", "")
    input = input.replace(")", "")
    input = input.replace("\n", "\\n")
    return input


def is_nan(v) -> bool:
    """
    Check if a value is NaN (Not a Number).
    
    Args:
        v: Value to check
        
    Returns:
        True if the value is NaN, False otherwise
    """
    return isinstance(v, float) and v != v


def is_blank(v) -> bool:
    """
    Check if a value is blank (None, NaN, or empty/whitespace string).
    
    Args:
        v: Value to check
        
    Returns:
        True if the value is considered blank, False otherwise
    """
    return v is None or is_nan(v) or (isinstance(v, str) and len(v.strip()) == 0)


def is_dash(v) -> bool:
    """
    Check if a value is a dash character (indicating no data).
    
    Args:
        v: Value to check
        
    Returns:
        True if the value is a dash character, False otherwise
    """
    if not isinstance(v, str):
        return False
    v = v.strip()
    return v == '-' or v == '–'


def name_to_lower_id(name: Union[str, None]) -> Optional[str]:
    """
    Convert a name to a lowercase identifier suitable for FHIR resources.
    
    Args:
        name: Name to convert, can be None
        
    Returns:
        Lowercase identifier string, None if input is not a string
    """
    if not isinstance(name, str):
        return None
    return name_to_id(name.lower())


def name_to_id(name: Union[str, None]) -> Optional[str]:
    """
    Convert a name to a valid FHIR identifier.
    
    This function:
    1. Removes invalid characters (keeps alphanumeric, hyphens, dots)
    2. Removes trailing periods to avoid Jekyll errors
    3. Truncates long IDs and adds hash for uniqueness
    
    Args:
        name: Name to convert to ID, can be None
        
    Returns:
        Valid FHIR identifier string, None if input is not a string
    """
    if not isinstance(name, str):
        return None
        
    # Remove invalid characters - keep only alphanumeric, hyphens, and dots
    id = re.sub('[^0-9a-zA-Z\\-\\.]+', '', name)
    
    # Remove trailing periods to work around jekyll errors
    id = id.rstrip('.')
    
    if len(id) > 55:
        # Maximum ID length is 64 characters, use hash for long names
        logging.getLogger(__name__).info("ERROR: name of id is too long. hashing.: " + id)
        id = to_hash(id, 55)
    
    return id