Profile: SGDecisionTable
Parent: SGPlanDefinition
Title: "SMART Guidelines Decision Table"
Description: "Defines the minimum expectations for PlanDefinition resources used in SMART Guidelines which are derived from DAK Decision Tables "
* library 1..

// Start slicing action
* action ^slicing.discriminator.type = #pattern
* action ^slicing.discriminator.path = "code"
* action ^slicing.rules = #open
* action ^slicing.ordered = false
* action ^slicing.description = "Slice based on code and resource type for output, guidance, annotation actions."

// output slice: required, must reference SGActivityDefinition
* action contains
    output 1..1 and
    guidance 0..1 and
    annotation 0..1

* action[output].definitionCanonical 1..1
// * action[output].definitionCanonical only Canonical(SGActivityDefinition) 
* action[output].code = $DecisionTableActions#output (exactly)
* action[output].description = "Output action referencing an SGActivityDefinition instance."



// guidance: optional, must reference CommunicationRequest
* action[guidance].definitionCanonical 1..1
//* action[guidance].definitionCanonical only Reference(CommunicationRequest)
* action[guidance].code = $DecisionTableActions#guidance (exactly)
* action[guidance].description = "Guidance action referencing a CommunicationRequest instance."

// annotation: optional, must reference CommunicationRequest
//* action[annotation].definitionCanonical 1..1
//* action[annotation].definitionCanonical only Reference(CommunicationRequest)
//* action[annotation].code = $DecisionTableActions#annotation (exactly)
//* action[annotation].description = "Annotation action referencing a CommunicationRequest instance."
