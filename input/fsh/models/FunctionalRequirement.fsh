Logical:       FunctionalRequirement
Title:	       "Functional Requirement (DAK)"
Description:   "Logical Model for representing functional requirement from a DAK"

* ^status = #active
* id 1..1 id "Requirement ID" "An identifier or code for the requirement"
* activity 1..1 string "Activity" "Description of the activity being performed"
* actor 0..* Reference(SGActor) "Actor" "The actor(s) that should fulfill the requirement"
* capability[x] 0..1 string or Coding "Capability" "Capability achieved by an actor fulfilling the requirement (I want)"
* benefit[x] 0..1 string or Coding "Benefit" "Benefit to an actor fulfilling the requirement (so that)"
* classification 0..* Coding "Classification" "Classification of the identifier"
