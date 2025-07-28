# DAK Extraction Scripts

## Overview

This directory contains Python scripts for extracting and processing Digital Adaptation Kit (DAK) content from WHO SMART Guidelines. These scripts form a comprehensive extraction pipeline that transforms various input formats (Excel files, BPMN diagrams, CQL logic, SVG images, etc.) into FHIR-compatible resources and Implementation Guide content.

The extraction pipeline is designed to process L2 (DAK) content and generate the structured artifacts needed for L3 (FHIR Implementation Guide) content, facilitating the creation of computable clinical guidelines.

## Quick Start

### Prerequisites
- Python 3.x
- Required Python dependencies (see installation below)
- A WHO SMART Guideline FHIR IG repository structure

### Installation

Before running the extraction scripts, install the required Python dependencies:

```bash
# From the root of any SMART Guideline repository
pip install -r ../smart-base/input/scripts/requirements.txt
```

Or if running from within the same repository:

```bash
pip install -r input/scripts/requirements.txt
```

### Usage

To extract DAK content from any WHO SMART Guideline repository, run the main extraction script from the root of the target guideline repository:

```bash
# Example: Extract DAK content from smart-immunizations
gh repo clone WorldHealthOrganization/smart-base
gh repo clone WorldHealthOrganization/smart-immunizations
cd smart-immunizations

# Install dependencies
pip install -r ../smart-base/input/scripts/requirements.txt

# Run the extraction
python ../smart-base/input/scripts/extract_dak.py
```

The script will orchestrate the entire extraction pipeline, processing all available content types and generating FHIR resources in the appropriate directories of the current working directory (the target guideline repository).

#### Running Against Different Guidelines

The `extract_dak.py` script can be run against any WHO SMART Guideline repository. Simply:

1. Clone the smart-base repository (contains the extraction scripts)
2. Clone or navigate to your target guideline repository 
3. Install the dependencies from smart-base
4. Run the extraction script from the target repository, pointing to the smart-base scripts

```bash
# Example with different guideline repositories:
# For smart-malaria:
cd smart-malaria
python ../smart-base/input/scripts/extract_dak.py

# For smart-hiv:
cd smart-hiv  
python ../smart-base/input/scripts/extract_dak.py
```

The extraction will process DAK content from the current directory and generate FHIR resources appropriate for that specific guideline.

## File Structure and Functionality

### Detailed File Reference

| File Name                | Goal                                                                 | Inputs                                                                 | Outputs                                                                 |
|--------------------------|----------------------------------------------------------------------|------------------------------------------------------------------------|-------------------------------------------------------------------------|
| `codesystem_manager.py`  | Manages FHIR CodeSystem and ValueSet resources by registering, merging, and rendering codes and properties for DAKs. | Code system IDs, titles, codes, display names, definitions, designations, properties; uses `stringer` for escaping/hashing. | FHIR CodeSystem and ValueSet FSH representations stored in dictionaries or rendered for implementation guides. |
| `bpmn_extractor.py`      | Extracts business process data from BPMN files and transforms them into FHIR FSH format using `bpmn2fhirfsh.xsl`. | BPMN files (`*.bpmn`) from `input/business-processes/`, `bpmn2fhirfsh.xsl`, `installer` object. | FHIR FSH resources (e.g., `SGRequirements`, `SGActor`) stored via `installer.add_resource`, logs transformation success/failure. |
| `dd_extractor.py`        | Extracts data dictionary entries from Excel files, generating FHIR ValueSets linked to business processes, tasks, decision tables, and indicators. | Excel files (`*.xlsx`) from `input/dictionary/`, cover sheet with tab names/descriptions, `installer` object. | FHIR ValueSet FSH representations stored via `installer.add_resource`, logs extraction details. |
| `DHIExtractor.py`        | Extracts digital health intervention (DHI) classifications and categories from text files, creating FHIR CodeSystems, ValueSets, and ConceptMaps. | Text files (`system_categories.txt`, `dhi_v1.txt`) from `input/data/`, `installer` object. | FHIR CodeSystem, ValueSet, ConceptMap FSH representations stored via `installer.add_resource`, logs extraction details. |
| `extractor.py`           | Base class for extracting data from various sources (e.g., Excel, BPMN), providing utility functions for data frame processing and logging. | Input file paths, column mappings, sheet names, `installer` object; subclasses define specific inputs. | Processed data frames with normalized columns, logs, resources stored via `installer` (specific to subclasses). |
| `extract_dhi.py`         | Orchestrates extraction of DHI data using `DHIExtractor`, coordinating with `installer` to process and store results. | Command-line arguments (optional, e.g., `--help`), text files via `DHIExtractor`. | Installed FHIR resources via `installer.install()`, logs success/failure, exits with status code. |
| `dt_extractor.py`        | Extracts decision table logic from Excel and CQL files, generating FHIR ValueSets, PlanDefinitions, ActivityDefinitions, and DMN representations. | Excel files (`*.xlsx`) from `input/decision-logic/`, CQL files (`*.cql`) from `input/cql/`, `dmn2html.xslt`, `installer` object. | FHIR ValueSet, PlanDefinition, ActivityDefinition FSH, DMN XML, markdown pages stored via `installer.add_resource`/`add_page`, logs details. |
| `extract_dak.py`         | Orchestrates extraction of DAK content by coordinating multiple extractors (data dictionary, BPMN, SVG, requirements, decision tables, personas). | Command-line arguments (optional, e.g., `--help`), files processed by extractors (`dd_extractor`, etc.). | Installed FHIR resources via `installer.install()`, logs success/failure, exits with status code. |
| `installer.py`           | Manages installation of FHIR resources, pages, CQL files, and DMN tables, handling transformations (e.g., via `bpmn2fhirfsh.xsl`, `dmn2html.xslt`, `svg2svg.xsl`) and storage. | FHIR resources, CQL content, markdown pages, DMN XML, XSLT files, `sushi-config.yaml`, `multifile.xsd`, aliases. | Installed files in `input/fsh/`, `input/cql/`, `input/dmn/`, `input/pagecontent/`, logs installation success/failure. |
| `req_extractor.py`       | Extracts functional and non-functional requirements from Excel files, generating FHIR Requirement and ActorDefinition resources. | Excel files (`*.xlsx`) from `input/system-requirements/`, functional/non-functional sheet column mappings, `installer` object. | FHIR Requirement, ActorDefinition FSH stored via `installer.add_resource`, CodeSystem/ValueSet for categories, logs extraction details. |
| `svg_extractor.py`       | Extracts and transforms SVG files from business processes into FHIR-compatible formats using `svg2svg.xsl`. | SVG files (`*.svg`) from `input/business-processes/`, `svg2svg.xsl`, `installer` object. | Transformed SVG files stored in `input/images/`, logs transformation success/failure. |
| `stringer.py`            | Provides utility functions for string manipulation, including escaping, hashing, and ID normalization for FHIR resource generation. | Strings for escaping (XML, markdown, code, rulesets), names for ID conversion, inputs for blank/dash checks. | Escaped strings, hashed IDs, normalized IDs, logs for long ID hashing or errors. |
| `multifile_processor.py` | Processes multifile XML to apply file changes to a Git repository, handling branching, committing, and pushing. | Multifile XML (`<path_to_multifile.xml>`) with file paths, content, diff formats, Git repository context. | Updated files in repository, Git commits/pushes, logs for parsing and Git operation success/failure. |
| `extractpr.py`           | Extracts personas/actors content from PDF files containing SMART Guidelines documentation, focusing on Generic Personas and Related Personas tables. | PDF files (`*.pdf`) from `input/personas/`, `installer` object. | FHIR ActorDefinition FSH resources stored via `installer.add_resource`, CodeSystem for persona types, logs extraction details. |
| `includes/bpmn2fhirfsh.xsl` | Transforms BPMN XML into FHIR FSH, generating resources like Requirements, Actors, Questionnaires, and Decision Tables for business processes. | BPMN XML from `input/business-processes/*.bpmn`, processed via `installer.transform_xml`. | FHIR FSH resources (e.g., `SGRequirements`, `SGActor`) stored via `installer.add_resource`, with links to CodeSystems and StructureDefinitions. |
| `includes/dmn2html.xslt` | Transforms DMN XML into HTML for displaying decision tables in implementation guides, including decision IDs, rules, triggers, inputs, and outputs. | DMN XML from `installer.add_dmn_table`, processed via `installer.transform_xml`. | HTML files in `input/pagecontent/` (e.g., `<id>.xml`), with links to FHIR CodeSystems, logs transformation details. |
| `includes/svg2svg.xsl`   | Transforms SVG files to ensure compatibility with FHIR implementation guides, likely preserving or modifying business process visualizations. | SVG XML content from `input/business-processes/*.svg`, processed via `installer.transform_xml`. | Transformed SVG files stored in `input/images/`, compatible with FHIR rendering. |

### Script Categories

#### Core Extraction Scripts
- `extract_dak.py` - Main orchestrator coordinating all extraction processes
- `installer.py` - Resource manager handling FHIR installation and transformations  
- `extractor.py` - Base class providing common functionality for specialized extractors

#### Specialized Content Extractors
- `dd_extractor.py` - Data Dictionary extraction from Excel files
- `req_extractor.py` - Requirements processing for functional/non-functional specs
- `bpmn_extractor.py` - Business Process transformation from BPMN to FHIR
- `dt_extractor.py` - Decision Tables conversion to computable formats
- `svg_extractor.py` - Graphics processing for IG compatibility
- `DHIExtractor.py` - Digital Health Interventions classification extraction
- `extractpr.py` - Personas extraction from PDF documents

#### Supporting Utilities
- `codesystem_manager.py` - Terminology management for CodeSystems and ValueSets
- `stringer.py` - String manipulation utilities for FHIR resource generation
- `multifile_processor.py` - Git integration for automated repository workflows

### Schema and Validation Files

| Directory/File | Purpose |
|----------------|---------|
| `xsd/` | Contains XSD schema files for DMN and other XML validation |
| `includes/multifile.xsd` | Schema for multifile XML processing |

## Content Processing Flow

1. **Data Dictionary Processing** (`dd_extractor.py`): Extracts terminology and value sets from Excel files
2. **Requirements Processing** (`req_extractor.py`): Converts functional requirements into FHIR resources  
3. **Business Process Processing** (`bpmn_extractor.py`): Transforms BPMN workflows into FHIR actors and requirements
4. **Decision Logic Processing** (`dt_extractor.py`): Converts decision tables and CQL into executable FHIR resources
5. **Visual Content Processing** (`svg_extractor.py`): Optimizes diagrams for IG presentation
6. **Personas Processing** (`extractpr.py`): Extracts actor definitions from PDF documentation
7. **Resource Installation** (`installer.py`): Coordinates final resource generation and file organization

## Output Structure

The extraction process generates content in the following directories:
- `input/fsh/` - FHIR Shorthand (FSH) resource definitions
- `input/cql/` - Clinical Quality Language files
- `input/pagecontent/` - Markdown pages and HTML content
- `input/images/` - Processed SVG diagrams
- `input/dmn/` - Decision Model and Notation files

## Future Plans

**Note**: These DAK extraction scripts are currently hosted in this repository as a convenience. They will be migrated to their own dedicated repository in the future to better separate the core FHIR profiles from the extraction tooling.

## Additional Utilities

### Individual Extractor Scripts

- `extract_dhi.py` - Standalone script for Digital Health Intervention extraction
- `check_pages.sh` - Shell script for page validation

For questions or issues with the DAK extraction scripts, please refer to the main repository documentation or submit an issue.
