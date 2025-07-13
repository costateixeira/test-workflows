Profile: SGCommunicationRequest
Parent: http://hl7.org/fhir/uv/cpg/StructureDefinition/cpg-communicationrequest
Title: "SMART Guidelines Communication Request"
Description: "Provide communication"
* ^extension[+].url = "http://hl7.org/fhir/uv/cpg/StructureDefinition/cpg-knowledgeCapability"
* ^extension[=].valueCode = #computable
//* kind = #CommunicationRequest
//* intent = #proposal
* doNotPerform = false
* status = #active


Profile: SGDecisionTableGuidance
Parent: SGCommunicationRequest
Title: "SMART Guidelines Decision Table Guidance"
Description: """Guidance to health worker coming from a DAK Decision Table"""


