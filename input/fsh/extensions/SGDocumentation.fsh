Extension: SGDocumentation
Description: "Smart Guidelines Documentation extension"
* extension contains $SGcode named code 1..1
* extension contains SGMarkdown named doc 1..1
* extension contains SGRequirementExt named requirements 0..


Extension: SGMarkdown 
Description: "Smart Guidelines markdown extension"
* value[x] only markdown
* valueMarkdown 1..1 MS


Extension: SGRequirementExt
Description: "Smart Guidelines Requirements extension"
* value[x] only Reference(SGRequirements)


