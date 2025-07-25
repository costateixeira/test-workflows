# DAK Extraction Scripts

## Overview

This directory contains Python scripts for extracting and processing Digital Adaptation Kit (DAK) content from WHO SMART Guidelines. These scripts form a comprehensive extraction pipeline that transforms various input formats (Excel files, BPMN diagrams, CQL logic, SVG images, etc.) into FHIR-compatible resources and Implementation Guide content.

The extraction pipeline is designed to process L2 (DAK) content and generate the structured artifacts needed for L3 (FHIR Implementation Guide) content, facilitating the creation of computable clinical guidelines.

## Quick Start

### Prerequisites
- Python 3.x with required dependencies (lxml, pandas, etc.)
- A WHO SMART Guideline FHIR IG repository structure

### Usage

To extract DAK content, run the main extraction script from the root of a WHO SMART Guideline FHIR IG repository:

```bash
python input/scripts/extract_dak.py
```

This will orchestrate the entire extraction pipeline, processing all available content types and generating FHIR resources in the appropriate directories.

## File Structure and Functionality

### Core Extraction Scripts

| File Name | Purpose | Input Sources | FHIR Outputs |
|-----------|---------|---------------|--------------|
| `extract_dak.py` | **Main orchestrator** - Coordinates all extraction processes in a unified pipeline | Command-line execution, coordinates all other extractors | Complete set of FHIR resources via installer |
| `installer.py` | **Resource manager** - Handles FHIR resource installation, file management, and XSLT transformations | FHIR resources, CQL content, pages, XSLT files | Organized files in `input/fsh/`, `input/cql/`, `input/pagecontent/` |
| `extractor.py` | **Base class** - Provides common functionality for all specialized extractors | Generic input processing, logging utilities | Foundation for specialized extractors |

### Specialized Content Extractors

| File Name | Purpose | Input Sources | FHIR Outputs |
|-----------|---------|---------------|--------------|
| `dd_extractor.py` | **Data Dictionary** - Extracts structured data definitions and terminology | Excel files from `input/dictionary/` | FHIR ValueSets linked to business processes |
| `req_extractor.py` | **Requirements** - Processes functional and non-functional system requirements | Excel files from `input/system-requirements/` | FHIR Requirement and ActorDefinition resources |
| `bpmn_extractor.py` | **Business Processes** - Transforms BPMN workflow diagrams into FHIR resources | BPMN files from `input/business-processes/` | FHIR SGRequirements, SGActor resources |
| `dt_extractor.py` | **Decision Tables** - Converts clinical decision logic into computable formats | Excel/CQL files from `input/decision-logic/`, `input/cql/` | FHIR ValueSets, PlanDefinitions, ActivityDefinitions, DMN |
| `svg_extractor.py` | **Graphics** - Processes SVG diagrams for IG compatibility | SVG files from `input/business-processes/` | Transformed SVG files in `input/images/` |
| `DHIExtractor.py` | **Digital Health Interventions** - Extracts DHI classifications and categories | Text files from `input/data/` | FHIR CodeSystems, ValueSets, ConceptMaps |

### Supporting Utilities

| File Name | Purpose | Function |
|-----------|---------|----------|
| `codesystem_manager.py` | **Terminology Management** - Manages FHIR CodeSystem and ValueSet resources | Registers, merges, and renders codes and properties for DAKs |
| `stringer.py` | **String Utilities** - Provides string manipulation functions | Escaping, hashing, ID normalization for FHIR resource generation |
| `multifile_processor.py` | **Git Integration** - Processes multifile XML and applies changes to repositories | Handles branching, committing, and pushing for automated workflows |

### XSLT Transformation Files

| File Name | Purpose | Input | Output |
|-----------|---------|--------|--------|
| `includes/bpmn2fhirfsh.xsl` | **BPMN to FHIR** - Transforms BPMN XML into FHIR FSH resources | BPMN XML from business processes | FHIR FSH resources (Requirements, Actors, Questionnaires) |
| `includes/dmn2html.xslt` | **DMN to HTML** - Creates decision table displays for IGs | DMN XML from decision tables | HTML files for `input/pagecontent/` |
| `includes/svg2svg.xsl` | **SVG Optimization** - Ensures SVG compatibility with FHIR IGs | SVG files from business processes | FHIR-compatible SVG files |

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
6. **Resource Installation** (`installer.py`): Coordinates final resource generation and file organization

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