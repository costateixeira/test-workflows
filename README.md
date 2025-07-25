[![License: CC BY-IGO 3.0](https://licensebuttons.net/l/by-nc/3.0/igo/80x15.png)](https://creativecommons.org/licenses/by/3.0/igo)
![CI Build](https://img.shields.io/github/actions/workflow/status/WorldHealthOrganization/smart-base/ghbuild.yml)  
  

![QA errors](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fworldhealthorganization.github.io%2Fsmart-base%2Fqa.json&query=%24.errs&logoColor=red&label=QA%20errors&color=yellow)
![QA warnings](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fworldhealthorganization.github.io%2Fsmart-base%2Fqa.json&query=%24.warnings&logoColor=orange&label=QA%20warnings&color=yellow)
![QA hints](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fworldhealthorganization.github.io%2Fsmart-base%2Fqa.json&query=%24.hints&logoColor=yellow&label=QA%20hints&color=yellow)


[https://build.fhir.org/ig/WorldHealthOrganization/smart-base](https://build.fhir.org/ig/WorldHealthOrganization/smart-base)

# WHO SMART GUIDELINES - Base IG

## Overview

This repository contains the **core FHIR profiles** that define the common knowledge representation artifacts used by WHO SMART Guidelines. It serves as the foundational Implementation Guide for the WHO SMART Guidelines ecosystem, providing base profiles and common dependencies to assist in the creation of SMART Implementation Guides.

The repository includes both:
- **L2 (DAK) Content**: Digital Adaptation Kit artifacts that provide the structured knowledge representation
- **L3 (FHIR IG) Content**: FHIR Implementation Guide profiles, extensions, and resources that enable computable clinical guidelines

## Repository Contents

### Core FHIR Profiles and Extensions
This ImplementationGuide contains base profiles, extensions, and common dependencies that serve as the foundation for all WHO SMART Guidelines Implementation Guides. These artifacts define the standardized approach for representing clinical knowledge in a computable format.

### DAK Extraction Tools
As a convenience, this repository currently includes a comprehensive set of Digital Adaptation Kit (DAK) extraction Python scripts under `input/scripts/`. These tools process various input formats (Excel files, BPMN diagrams, CQL logic, etc.) and transform them into FHIR-compatible resources.

**Note**: The DAK extraction scripts will be migrated to their own dedicated repository in the future to better separate the core FHIR profiles from the extraction tooling.

For detailed documentation on the DAK extraction functionality, see [input/scripts/README.md](input/scripts/README.md). 

## Publication
Continuous Build: __http://WorldHealthOrganization.github.io/smart-base/index.html__  
Canonical / permanent URL: 
<br> </br>


This framework is published under a Creative Commons - IGO [license](LICENSE.md).

## Changes and feedback

Feedback and issues about this empty framework can be submitted via the [issues](issues) page, and will be incorporated into subsequent releases.

