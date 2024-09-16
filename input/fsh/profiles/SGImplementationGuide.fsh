Profile: SGImplementationGuide
Parent: http://hl7.org/fhir/uv/crmi/StructureDefinition/crmi-shareableimplementationguide
Title: "SMART Guidelines ImplementationGuide"
Description: "Defines the minimum expectations for ImplementationGuide resources used in SMART Guidelines"
* name 1..1
* publisher 1..1

* license = #CC-BY-SA-3.0-IGO

* definition.resource
  * ^slicing.discriminator.type = #profile
  * ^slicing.discriminator.path = "reference.resolve()"
  * ^slicing.rules = #open

* definition.resource contains 
  ActivityDefinition 0..* and
  CodeSystem 0..* and
  ConceptMap 0..* and
  Extension 0..* and
  Library 0..* and
  LogicalModel 0..* and
  Measure 0..* and
  Profile 0..* and
  Questionnaire 0..* and
  StructureMap 0..* and
  ValueSet 0..*

* definition.resource[ActivityDefinition].reference.type = #ActivityDefinition
* definition.resource[ActivityDefinition].reference only Reference(SGActivityDefinition)
* definition.resource[CodeSystem].reference.type = #CodeSystem
* definition.resource[CodeSystem].reference only Reference(SGCodeSystem)
* definition.resource[ConceptMap].reference.type = #ConceptMap
* definition.resource[ConceptMap].reference only Reference(SGConceptMap)
* definition.resource[Library].reference.type = #Library
* definition.resource[Library].reference only Reference(SGLibrary)
* definition.resource[LogicalModel].reference.type = #StructureDefinition
* definition.resource[LogicalModel].reference only Reference(SGLogicalModel)
* definition.resource[Measure].reference.type = #Measure
* definition.resource[Measure].reference only Reference(SGMeasure)
* definition.resource[Profile].reference.type = #StructureDefinition
* definition.resource[Profile].reference only Reference(SGStructureDefinition)
* definition.resource[Questionnaire].reference.type = #Questionnaire
* definition.resource[Questionnaire].reference only Reference(SGQuestionnaire)
* definition.resource[StructureMap].reference.type = #StructureMap
* definition.resource[StructureMap].reference only Reference(SGStructureMap)
* definition.resource[ValueSet].reference.type = #ValueSet
* definition.resource[ValueSet].reference only Reference(SGValueSet)

