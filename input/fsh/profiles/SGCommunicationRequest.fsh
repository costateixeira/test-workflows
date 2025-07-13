Profile: SGCommunicationRequest
Parent: http://hl7.org/fhir/uv/cpg/StructureDefinition/cpg-communicationrequest
Title: "SGCommunicationRequest"
Description: "Provide communication"
* ^extension[+].url = "http://hl7.org/fhir/uv/cpg/StructureDefinition/cpg-knowledgeCapability"
* ^extension[=].valueCode = #computable
//* kind = #CommunicationRequest
//* intent = #proposal
* doNotPerform = false
* status = #active


Profile: SGDecisionTableGuidance
Parent: SGCommunicationRequest



