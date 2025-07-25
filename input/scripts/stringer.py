"""
String Utility Functions for SMART Guidelines Processing

This module provides various string manipulation and escaping utilities used
throughout the SMART guidelines generation process. It includes functions for
XML escaping, markdown processing, identifier generation, and hash-based
truncation for long strings.

The module handles various escaping scenarios required for:
- XML/HTML content generation
- FHIR resource identifiers
- Markdown documentation
- Code system processing

Author: SMART Guidelines Team
"""
from typing import Optional, Union
import hashlib
import logging
import re


def to_hash(input: str, len: int) -> str:
    """
    Generate a truncated string with hash suffix for long identifiers.

    Creates a shortened version of the input string by keeping the beginning
    and appending a hash-based suffix to ensure uniqueness while maintaining
    readability.

    Args:
        input: The string to be hashed and truncated
        len: Maximum length of the resulting string

    Returns:
        Truncated string with hash suffix
    """
    return input[:len - 10] + \
        str(hashlib.shake_256(input.encode()).hexdigest(5))


def xml_escape(input: str) -> str:
    """
    Escape special characters for XML/HTML content.

    Converts characters that have special meaning in XML to their
    corresponding entity references for safe inclusion in XML documents.

    Args:
        input: String to be XML-escaped

    Returns:
        XML-safe string with escaped characters
    """
    if (not (isinstance(input, str))):
        return ""
    # see
    # https://stackoverflow.com/questions/1546717/escaping-strings-for-use-in-xml
    return input.replace(
        "&",
        "&amp;").replace(
        "<",
        "&lt;").replace(
            ">",
            "&gt;").replace(
                "\"",
                "&quot;").replace(
                    "'",
        "&apos;")


def escape(input: str) -> Optional[str]:
    """
    Escape double quotes in strings for code generation.

    Prepares strings for use in generated code by escaping double quote
    characters that could interfere with string literals.

    Args:
        input: String to be escaped

    Returns:
        String with escaped double quotes, or None if input is not a string
    """
    if (not (isinstance(input, str))):
        return None
    return input.replace('"', r'\"')


def escape_code(input: str) -> Optional[str]:
    """
    Generate safe file and code identifiers from strings.

    Processes input strings to create valid identifiers suitable for use
    as filenames and code references. Handles length limits, removes problematic
    characters, and applies hashing for very long identifiers.

    Args:
        input: String to be converted to a safe code identifier

    Returns:
        Safe identifier string, or None if input is not a string
    """
    original = input
    if (not (isinstance(input, str))):
        return None
    input = input.strip()
    input = re.sub(r"['\"]", "", input)
    # SUSHI BUG on processing codes with double quote.  sushi fails
    # Example \"Bivalent oral polio vaccine (bOPV)–inactivated polio vaccine
    # (IPV)\" schedule (in countries with high vaccination coverage [e.g.
    # 90–95%] and low importation risk [where neighbouring countries and/or
    # countries that share substantial population movement have a similarly
    # high coverage])"

    input = re.sub(r"\s+", " ", input)
    if len(input) > 245:
        # max filename size is 255, leave space for extensions such as .fsh
        logging.getLogger(__name__).info(
            "ERROR: name of id is too long.hashing: " + input)
        input = to_hash(input, 245)
        logging.getLogger(__name__).info(
            "Escaping code " + original + " to " + input)
    return input


def markdown_escape(input: str) -> str:
    """
    Escape strings for safe inclusion in markdown content.

    Handles special markdown characters that could interfere with
    document formatting or processing.

    Args:
        input: String to be markdown-escaped

    Returns:
        Markdown-safe string
    """
    if not isinstance(input, str):
        return " "
    input = input.replace('"""', '\\"\\"\\"')
    return input


def ruleset_escape(input: str) -> str:
    """
    Escape strings for use in ruleset definitions.

    Prepares strings for inclusion in ruleset files by escaping
    characters that have special meaning in ruleset syntax.

    Args:
        input: String to be escaped for ruleset use

    Returns:
        Ruleset-safe string
    """
    # strings in rulesets are handled poorly
    input = input.replace(",", "\\,")
    input = input.replace("'", "")
    input = input.replace("(", "")
    input = input.replace(")", "")
    input = input.replace("\n", "\\n")
    return input


def is_nan(v: Union[float, str, None]) -> bool:
    """
    Check if a value is NaN (Not a Number).

    Args:
        v: Value to check

    Returns:
        True if the value is NaN, False otherwise
    """
    return (isinstance(v, float) and v != v)


def is_blank(v: Union[str, float, None]) -> bool:
    """
    Check if a value is blank, empty, or None.

    Tests for various forms of empty values including None,
    NaN, and empty strings.

    Args:
        v: Value to check

    Returns:
        True if the value is considered blank, False otherwise
    """
    return v is None or is_nan(v) \
        or (isinstance(v, str) and len(v.strip()) == 0)


def is_dash(v: Union[str, None]) -> bool:
    """
    Check if a string represents a dash character.

    Tests for various dash representations commonly used
    to indicate empty or null values.

    Args:
        v: Value to check

    Returns:
        True if the value is a dash character, False otherwise
    """
    if not isinstance(v, str):
        return False
    v = v.strip()
    return (v == '-' or v == '–')


def name_to_lower_id(name: str) -> Optional[str]:
    """
    Convert a name to a lowercase identifier.

    Processes a human-readable name into a valid lowercase identifier
    suitable for use in code and file references.

    Args:
        name: Name string to convert

    Returns:
        Lowercase identifier string, or None if input is not a string
    """
    if (not (isinstance(name, str))):
        return None
    return name_to_id(name.lower())


def name_to_id(name: str) -> Optional[str]:
    """
    Convert a name to a valid identifier.

    Transforms human-readable names into valid identifiers by removing
    invalid characters and applying length limits with hash-based truncation
    when necessary.

    Args:
        name: Name string to convert

    Returns:
        Valid identifier string, or None if input is not a string
    """
    if (not (isinstance(name, str))):
        return None
    id = re.sub('[^0-9a-zA-Z\\-\\.]+', '', name)
    # to work around jekyll error, make sure there are no trailing periods...
    id = id.rstrip('.')
    if len(id) > 55:
        # make length of an id is 64 characters
        # we need to make use of hashes
        logging.getLogger(__name__).info(
            "ERROR: name of id is too long. hashing.: " + id)
        id = to_hash(id, 55)
    return id
