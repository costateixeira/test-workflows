Logical:       Persona
Title:	       "Persona (DAK)"
Description:   "Logical Model for representing Personas from a DAK"

* ^status = #active
* id 1..1 id "Requirement ID" "An identifier or code for the requirement"
* name 1..1 string "Name" "Name"
* description 1..1 string "Description" "Description of the persona"
* ISCO 0..* CodeableConcept "ISCO Code" "ISCO Code"
* type 1..1 code "Type of Persona" "Persona Types: Key/Related/System/Hardware Device"
* type from SGPersonaTypesVS
* ISCO from urn:oid:2.16.840.1.113883.2.9.6.2.7
