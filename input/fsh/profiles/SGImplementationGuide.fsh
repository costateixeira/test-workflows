Profile: SGImplementationGuide
Parent: ImplementationGuide

* license = #CC-BY-SA-3.0-IGO




* definition.resource
  * ^slicing.discriminator.type = #profile
  * ^slicing.discriminator.path = "reference.resolve()"
  * ^slicing.rules = #open

* definition.resource contains 
  LogicalModel 0..* and
  Extension 0..* and
  Profile 0..*

* definition.resource[LogicalModel].reference.type = #StructureDefinition
* definition.resource[LogicalModel].reference only Reference(SGLogicalModel)

