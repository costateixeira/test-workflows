# Personas Extractor (extractpr.py) Documentation

## Overview

The `extractpr.py` script extracts SMART Guidelines DAK Component 2 (personas/actors) content from PDF files containing WHO SMART Guidelines documentation. It processes Generic Personas and Related Personas tables, converting them into FHIR ActorDefinition resources.

## Usage

### Standalone Usage

```bash
cd /path/to/smart-base
python3 input/scripts/extractpr.py
```

### As part of DAK extraction pipeline

The personas extractor is automatically included when running the full DAK extraction:

```bash
cd /path/to/smart-base  
python3 input/scripts/extract_dak.py
```

## Input Requirements

### PDF File Location
- Place PDF files in the `input/personas/` directory
- The script will process all `*.pdf` files found in this directory

### Expected PDF Content
The extractor looks for the following content patterns in PDF files:

1. **Section indicators:**
   - "2.1 Generic Personas" 
   - "Targeted Generic Personas"
   - References to "Generic Personas" or "Related Personas"

2. **Table structures:**
   - **Table 2: Generic Personas** - typically contains columns like:
     - Persona/Actor/Role name
     - Description/Definition  
     - Responsibilities/Duties
   - **Table 3: Related Personas** - typically contains columns like:
     - Persona/Actor name
     - Type/Category
     - Examples/Instances

3. **Text-based personas** - fallback for bullet points or numbered lists when table extraction fails

## Example PDF Content

Based on WHO SMART Guidelines documents such as:
- [ANC Guidelines](https://iris.who.int/bitstream/handle/10665/380303/9789240099456-eng.pdf?sequence=1) - Section 2.1, pages 18-19
- [TB Guidelines](https://iris.who.int/bitstream/handle/10665/360991/9789240054424-eng.pdf?sequence=1) - Section 2.1, page 16

Expected table format:
```
| Persona              | Description                      | Responsibilities                    |
|---------------------|----------------------------------|-------------------------------------|
| Healthcare Provider | Clinical staff providing care    | Diagnose, prescribe, monitor        |
| Community Health Worker | Community-based health providers | Provide basic care, education, referrals |
```

## Output

### FHIR Resources Generated

1. **ActorDefinition resources** - One for each extracted persona:
   ```fsh
   Instance: HealthcareProvider
   InstanceOf: ActorDefinition
   Usage: #definition
   * name = "HealthcareProvider"
   * title = "Healthcare Provider"
   * status = #active
   * type = #person
   * description = "Clinical staff providing direct patient care"
   ```

2. **CodeSystem for persona types** (if type information is available):
   ```fsh
   CodeSystem: PersonaTypes
   Title: "SMART Guidelines Persona Types"
   ```

### File Locations
- Generated FSH files: `input/fsh/actordefinitions/`
- Log files: `temp/extractpr.py.log`

## Extraction Process

1. **PDF Discovery** - Scans `input/personas/` for PDF files
2. **Content Analysis** - Searches each page for personas-related content
3. **Table Extraction** - Uses pdfplumber to extract structured tables
4. **Data Parsing** - Maps table columns to standard persona attributes
5. **Text Fallback** - Extracts from bullet points if table extraction fails
6. **FHIR Generation** - Creates ActorDefinition resources
7. **Installation** - Stores resources via the installer framework

## Troubleshooting

### Common Issues

1. **No personas found:**
   - Verify PDF contains the expected table structures
   - Check that section headings match expected patterns
   - Review the log file for detailed extraction attempts

2. **Table extraction failures:**
   - The script includes text-based fallback extraction
   - Complex table layouts may require manual review
   - Consider preprocessing PDFs to improve table structure

3. **Installation errors:**
   - Ensure you run from the correct directory (smart-base root)
   - Check that sushi-config.yaml is properly formatted
   - Verify all dependencies are installed

### Dependencies

Required Python packages:
- `pandas` - Data frame processing
- `pdfplumber` - PDF text and table extraction  
- `lxml` - XML processing for FHIR generation

Install dependencies:
```bash
pip install pandas pdfplumber lxml
```

## Integration with SMART Guidelines

The extracted personas become part of the SMART Guidelines FHIR implementation guide and can be:
- Referenced in clinical workflows
- Used in questionnaire design
- Integrated with other DAK components
- Utilized for implementation planning

The ActorDefinition resources follow FHIR R4 specifications and include appropriate metadata for use in healthcare implementation guides.