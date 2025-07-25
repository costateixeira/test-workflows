Logical:       Persona
Title:	       "Persona (DAK)"
Description:   "Logical Model for representing Personas from a DAK"

* ^status = #active
* id 1..1 id "Requirement ID" "An identifier or code for the requirement"
* name 1..1 string "Name" "Name"
* description 1..1 string "Description" "Description of the persona"
* ISCO 1..1 CodeableConcept "ISCO Code" "ISCO Code"
* type 1..1 code "Type of Persona" "Persona Types: Key/Related/System/Hardware Device"
* type from SGPersonaTypesVS
//* ISCO from Canonical(http://www.fhir.org/guides/stats2/ValueSet/isco-codes)
