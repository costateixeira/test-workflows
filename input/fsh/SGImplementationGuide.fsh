Profile: SGImplementationGuide
Parent: ImplementationGuide

* license = #CC-BY-SA-3.0-IGO





// Define the slicing
* definition.resource
  * ^slicing.discriminator.type = #pattern
  * ^slicing.discriminator.path = "reference.resolve()"
  * ^slicing.rules = #open


* definition.resource contains 
  LogicalModel 0..* 
//  Profile 0..* 

* definition.resource[LogicalModel].reference.type = #StructureDefinition
* definition.resource[LogicalModel].reference only Reference(SGLogicalModel)
//* definition.resource[Ppofile].reference only Reference(SGProfile)


