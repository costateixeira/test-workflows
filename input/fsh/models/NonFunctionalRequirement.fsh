Logical:       NonFunctionalRequirement
Title:	       "Non-Functional Requirement (DAK)"
Description:   "Logical Model for representing non-functional requirement from a DAK"

* ^status = #active
* id 1..1 id "Requirement ID" "An identifier or code for the requirement"
* requirement 1..1 string "Requirement" "Description of the required"
* category 0..1 Coding "Category" "Category of the non-functional requirement"
* classification 0..* Coding "Classification" "Classification or category of the requirement"
