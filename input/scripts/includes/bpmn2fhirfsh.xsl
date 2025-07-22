<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"

		xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
		xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
		xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
		xmlns:xalan="http://xml.apache.org/xslt"  
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		exclude-result-prefixes="bpmn">

  <xsl:variable name='prefix'><xsl:text>DT</xsl:text></xsl:variable>
  <xsl:variable name='newline'><xsl:text>&#xa;</xsl:text></xsl:variable>
      
  <xsl:variable name="collab" select="/bpmn:definitions/bpmn:collaboration[1]"/>

  <xsl:variable name="processes"
		select="( /bpmn:definitions//bpmn:process | /bpmn:definitions//bpmn:subProcess)[@name != '' and @id != '']" />


  <xsl:variable name="requirements"
		select="($processes//*[self::bpmn:businessRuleTask or self::bpmn:manualTask or self::bpmn:receiveTask or self::bpmn:scriptTask or self::bpmn:sendTask or self::bpmn:serviceTask or self::bpmn:task or self::bpmn:userTask ])[@name != '' and @id != '']"/>    

  
  <xsl:variable name="rules" select="$processes/bpmn:businessRuleTask[@id != '' and @name != '']"/> 

  
  <xsl:variable
      name="actors"
      select="$processes//bpmn:lane[@name != '' and @id != '']"/>

  <xsl:variable
      name="innerActors"
      select="$actors[not(child::bpmn:childLaneSet)]"/>  
  
  <xsl:key
      name="indexActorId"
      match="bpmn:lane[not(child::bpmn:childLaneSet)]"
      use="@id"/> 
  <xsl:variable
      name="uniqueActors"
      select="$innerActors[not(child::bpmn:childLaneSet)][ count(. | key('indexActorId',@id)[1]) = 1]"/>  

  <xsl:variable
      name="decisionTables"
      select="$processes/bpmn:businessRuleTask[@id != '' and @name != '']"/> 

  <xsl:variable
      name="questionnaires"
      select="$processes//bpmn:userTask[@name != '' and @id != '']"/>

  <xsl:key
      name="indexQuestionnaireId"
      match="bpmn:userTask"
      use="@id"/>
  <xsl:variable
      name="uniqueQuestionnaires"
      select="$questionnaires[ count(. | key('indexQuestionnaireId',@id)[1]) = 1]"/>  


  
  
  <xsl:output method="text" encoding="UTF-8"/>


  
  <!-- define some templates to use later -->


  <xsl:template name="requirementDescription">
    <xsl:variable name="requirementId" select="@id"/>
    <xsl:text>This is the requirement "</xsl:text><xsl:value-of select="@name"/><xsl:text>" as extracted from the Digital Adaptation Kit (DAK).</xsl:text><xsl:value-of select="$newline"/><xsl:value-of select="$newline"/>
    <!-- need to get element name as a code for the requirement-->
    
    <xsl:variable name="requirementActors"
		  select="$uniqueActors[ancestor::*[@id = $requirementId]]" />
    <xsl:if test="$requirementActors">
      <xsl:text>This requirement is fulfilled by the following actors:</xsl:text><xsl:value-of select="$newline"/>
      <xsl:for-each select="$requirementActors">
	<xsl:text>* [</xsl:text><xsl:value-of select="@name"/><xsl:text>](ActorDefinition-DD.</xsl:text><xsl:value-of select="@id"/><xsl:text>.html)</xsl:text><xsl:value-of select="$newline"/>
	<xsl:text>  (see [Concept Defintion](Codesystem-DD.html#</xsl:text><xsl:value-of select="@id"/><xsl:text>))</xsl:text><xsl:value-of select="$newline"/>
      </xsl:for-each>
    </xsl:if>
  </xsl:template>
  



  <xsl:template name="questionnaireActor">
    <xsl:variable name="questionnaireId" select="@id"/>
    <xsl:for-each select="$uniqueActors">
      <xsl:variable name="actorId" select="@id"/>
      <xsl:variable name="actorProcesses"
		  select="$processes[.//bpmn:lane[@id = $actorId]]" />
      <xsl:variable name="actorQuestionnaire"
		  select="$actorProcesses//bpmn:userTask[@name != '' and @id = $questionnaireId]"/>
      <xsl:if test="$actorQuestionnaire">
	<xsl:text>* extension[actor][+] = Reference(DD-</xsl:text><xsl:value-of select="$actorId"/><xsl:text>)</xsl:text>
	<xsl:value-of select="$newline"/>
      </xsl:if>
    </xsl:for-each>
  </xsl:template>
  

  
  <xsl:template name="actorDescription">
    <!-- fsh rendering of an actor -->
    <xsl:variable name="actorId" select="@id"/>
    <xsl:variable name="actorProcesses"
		  select="$processes[.//bpmn:lane[@id = $actorId]]" />
    <xsl:variable name="actorTaskRefs"
		  select="$actorProcesses//bpmn:lane[@id = $actorId]/bpmn:flowNodeRef/text()"/>    
    <xsl:for-each select="$actorTaskRefs">
      <xsl:text># TaskRef=</xsl:text><xsl:value-of select="."/>
    </xsl:for-each>
    <xsl:variable name="actorTasks"
		  select="($actorProcesses//*[self::bpmn:businessRuleTask or self::bpmn:manualTask or self::bpmn:receiveTask or self::bpmn:scriptTask or self::bpmn:sendTask or self::bpmn:serviceTask or self::bpmn:task or self::bpmn:userTask ])[@name != '' and @id = $actorTaskRefs]"/>

    <xsl:for-each select="$actorTasks">
      <xsl:text># Task=</xsl:text>
    </xsl:for-each>

    
    <xsl:text>This is the definition of the actor </xsl:text><xsl:value-of select="@name"/><xsl:text> as extracted from the Digital Adaptation Kit (DAK).</xsl:text><xsl:value-of select="$newline"/><xsl:value-of select="$newline"/>


    <xsl:variable name="actorRequirements"
		  select="($actorProcesses//*[self::bpmn:businessRuleTask or self::bpmn:manualTask or self::bpmn:receiveTask or self::bpmn:scriptTask or self::bpmn:sendTask or self::bpmn:serviceTask or self::bpmn:task or self::bpmn:userTask ])[@name != '' and @id != '']"/>    
    <xsl:if test="$actorRequirements">
      <xsl:text>The actor participates in the following requirements:</xsl:text>
      <xsl:value-of select="$newline"/>
      <xsl:for-each select="$actorRequirements">
	<xsl:text>* [</xsl:text><xsl:value-of select="@name"/><xsl:text>](Requirement-DD.</xsl:text><xsl:value-of select="@id"/><xsl:text>.html)</xsl:text><xsl:value-of select="$newline"/>
	<xsl:text>  (see [Concept Defintion](Codesystem-DD.html#</xsl:text><xsl:value-of select="@id"/><xsl:text>))</xsl:text><xsl:value-of select="$newline"/>
      </xsl:for-each>
    </xsl:if>
    
    <xsl:if test="$actorProcesses">
      <xsl:text>The actor participates in the following processes:</xsl:text>
      <xsl:value-of select="$newline"/>
      <xsl:for-each select="$actorProcesses">
	<xsl:text>* </xsl:text><xsl:value-of select="@name"/><xsl:text>(</xsl:text><xsl:value-of select="@name"/><xsl:text>)</xsl:text><xsl:value-of select="$newline"/>
	<xsl:text>  (see [Concept Defintion](Codesystem-DD.html#</xsl:text><xsl:value-of select="@id"/><xsl:text>))</xsl:text><xsl:value-of select="$newline"/>
	<xsl:variable name="actorQuestionnaires" select=".//bpmn:userTask"/>
	<xsl:if test="$actorQuestionnaires"> 
	  <xsl:text>  Under this process, the actor utilizes the following Questionnaires:</xsl:text>
	  <xsl:value-of select="$newline"/>
	  <xsl:for-each select="$actorQuestionnaires">
	    <!-- markdown link to questionnaire -->
	    <xsl:text>  * [</xsl:text><xsl:value-of select="@name"/><xsl:text>](StructureDefinition-DD.</xsl:text><xsl:value-of select="@id"/><xsl:text>.html)</xsl:text><xsl:value-of select="$newline"/>
	    <xsl:text>    (see [Concept Defintion](Codesystem-DD.html#</xsl:text><xsl:value-of select="@id"/><xsl:text>))</xsl:text><xsl:value-of select="$newline"/>
	  </xsl:for-each>
	</xsl:if>


	<xsl:variable name="actorDecisions" select=".//bpmn:businessRuleTask"/>	  	
	<xsl:if test="$actorDecisions">
	  <xsl:text>  Under this process, the actor utilizes the following Decisions Support Tables:</xsl:text>
	  <xsl:value-of select="$newline"/>
	  <xsl:for-each select="$actorDecisions">
	    <xsl:variable name="actorDecision" select="."/>
	    <!-- markdown link to plan defintiion -->
	    <xsl:text>  * [</xsl:text><xsl:value-of select="$actorDecision/@name"/><xsl:text>](PlanDefinition-DT.</xsl:text><xsl:value-of select="$actorDecision/@id"/><xsl:text>.html)</xsl:text><xsl:value-of select="$newline"/>
	    <xsl:text>    (see [Concept Defintion](Codesystem-DD.html#</xsl:text><xsl:value-of select="@id"/><xsl:text>))</xsl:text><xsl:value-of select="$newline"/>
	  </xsl:for-each>
	</xsl:if>
      </xsl:for-each>
    </xsl:if>
    
  </xsl:template>



  <!-- Root template: Produce a <files> bundle -->
  <xsl:template match="/bpmn:definitions">
    <files>
      <!-- Generate requirements from Tasks in bpmn -->
      <xsl:for-each select="$requirements"> <!-- a bpmn:lane -->
	<xsl:variable name="requirementCode" select="local-name()"/> <!-- use the element name as a code -->
        <file name="input/fsh/requirements/Requirement-DD.{@id}.fsh" mime-type="text/fsh">
Instance: DD.<xsl:value-of select="@id"/>
InstanceOf: Requirement
Title: "<xsl:value-of select="@name"/>"
Description """<xsl:call-template name="requirementDescription"/>
"""
Usage: #definition
* id = "DD.<xsl:value-of select="@id"/>"
* name = "<xsl:value-of select="@name"/>"
* type = #non-system
* status = #draft
* publisher = "World Health Organization (WHO)"
* experimental = false
* extension[coding][+] = $SGTasks#<xsl:value-of select="$requirementCode"/>
* contact[+]
  * telecom[+]
    * system = #url
    * value = "https://who.int"
        </file>
      </xsl:for-each>
      
      <!-- Generate ActorDefinition resources in FSH -->
      <xsl:for-each select="$uniqueActors"> <!-- a bpmn:lane -->
        <file name="input/fsh/ActorDefinition-DD.{@id}.fsh" mime-type="text/fsh">

Instance: DD.<xsl:value-of select="@id"/>
InstanceOf: ActorDefinition
Title: "<xsl:value-of select="@name"/>"
Description """<xsl:call-template name="actorDescription"/>
"""
Usage: #definition
* id = "DD.<xsl:value-of select="@id"/>"
* name = "<xsl:value-of select="@name"/>"
* type = #non-system
* status = #draft
* publisher = "World Health Organization (WHO)"
* experimental = false
* contact[+]
  * telecom[+]
    * system = #url
    * value = "https://who.int"
        </file>
      </xsl:for-each>

      <!-- Generate Questionnaire profile in FSH -->
      <xsl:for-each select="$questionnaires">
        <xsl:variable name="questionnaireId" select="@id"/>
        <xsl:variable name="questionnaireName" select="@name"/>
        <file name="input/fsh/profiles/{$questionnaireId}.fsh" mime-type="text/fsh">

Profile: DD.<xsl:value-of select="$questionnaireId"/>
Parent: $SGQuestionnaire
Title: "<xsl:value-of select="$questionnaireName"/>"
* id = DD."<xsl:value-of select="$questionnaireId"/>"
* name = "Questionnaire profile: <xsl:value-of select="$questionnaireName"/>"
<xsl:call-template name="questionnaireActor"/>
        </file>
      </xsl:for-each>


      <xsl:for-each select="$rules">
        <xsl:variable name="ruleId" select="@id"/>
        <xsl:variable name="ruleName" select="@name"/>
        <file name="input/fsh/profiles/{$ruleId}.fsh" mime-type="text/fsh">

Profile: DT.<xsl:value-of select="$ruleId"/>
Parent: $SGDecisionTable
Title: "<xsl:value-of select="$ruleName"/>"
* id = "DT.<xsl:value-of select="$ruleId"/>"
* name = "Decision Table profile: <xsl:value-of select="$ruleName"/>"
* contact[+]
  * telecom[+]
    * system = #url
    * value = "https://who.int"
        </file>
      </xsl:for-each>

    </files>
  </xsl:template>
</xsl:stylesheet>
    
    
<!--       <xsl:message># Looking at actors</xsl:message> -->

<!--       <entry> -->
<!-- 	<resource> -->
<!-- 	  <CodeSystem> -->
<!-- 	    <id><xsl:value-of select="$actors-CS-id"/></id> -->
<!-- 	    <url><xsl:value-of select="$actors-CS-url"/></url> -->
<!-- 	    <version><xsl:value-of select="$ig-version"/></version> -->
<!-- 	    <publisher><xsl:value-of select="$ig-publisher"/></publisher> -->
<!-- 	    <description><xsl:attribute name="value">Actors for <xsl:value-of select="$ig-name"/></xsl:attribute></description>	     -->
<!-- 	    <description value="Actors"/> -->
<!-- 	    <xsl:for-each select="$uniqueActors"> -->
<!-- 	      <xsl:variable name="actorCode" select="bpmn:extensionElements/zeebe:properties/zeebe:property[@name = 'ig-code']/@value[1]"/> -->
<!-- 	      <xsl:variable name="actorName" select="@name"/> -->
<!-- 	      <xsl:variable name="actorDescription" select="bpmn:documentation/text()"/> -->
<!-- 	      <concept> -->
<!-- 		<code><xsl:attribute name="value"><xsl:value-of select="$actorCode"/></xsl:attribute></code> -->
<!-- 		<display><xsl:attribute name="value"><xsl:value-of select="$actorName"/></xsl:attribute></display> -->
<!-- 		<definition><xsl:attribute name="value"><xsl:value-of select="$actorDescription"/></xsl:attribute></definition> -->
<!-- 	      </concept> -->
<!-- 	    </xsl:for-each>		 -->
<!-- 	  </CodeSystem> -->
<!-- 	</resource> -->
<!--       </entry> -->

<!--       <entry> -->
<!-- 	<resource> -->
<!-- 	  <ValueSet> -->
<!-- 	    <id><xsl:value-of select="$actors-CS-id"/></id> -->
<!-- 	    <version><xsl:value-of select="$ig-version"/></version> -->
<!-- 	    <publisher><xsl:value-of select="$ig-publisher"/></publisher> -->
<!-- 	    <description><xsl:attribute name="value">Actors for <xsl:value-of select="$ig-name"/></xsl:attribute></description> -->
<!-- 	    <compose> -->
<!-- 	      <include> -->
<!-- 		<system><xsl:attribute name="value"><xsl:value-of select="$actors-CS-url"/></xsl:attribute></system> -->
<!-- 	      </include> -->
<!-- 	    </compose> -->
<!-- 	  </ValueSet> -->
<!-- 	</resource> -->
<!--       </entry> -->


<!--       <entry> -->
<!-- 	<resource> -->
<!-- 	  <CodeSystem> -->
<!-- 	    <id><xsl:value-of select="$trans-CS-id"/></id> -->
<!-- 	    <url><xsl:value-of select="$trans-CS-url"/></url> -->
<!-- 	    <version><xsl:value-of select="$ig-version"/></version> -->
<!-- 	    <publisher><xsl:value-of select="$ig-publisher"/></publisher> -->
<!-- 	    <description><xsl:attribute name="value">Transactions for <xsl:value-of select="$ig-name"/></xsl:attribute></description> -->
<!-- 	    <xsl:for-each select="$uniqueArrows"> -->
<!-- 	      <xsl:variable name="transCode" select="bpmn:extensionElements/zeebe:properties/zeebe:property[@name = 'ig-code']/@value[1]"/> -->
<!-- 	      <xsl:variable name="transName" select="@name"/> -->
<!-- 	      <xsl:variable name="transDescription" select="bpmn:documentation/text()"/> -->
<!-- 	      <concept> -->
<!-- 		<code><xsl:attribute name="value"><xsl:value-of select="$transCode"/></xsl:attribute></code> -->
<!-- 		<display><xsl:attribute name="value"><xsl:value-of select="$transName"/></xsl:attribute></display> -->
<!-- 		<definition><xsl:attribute name="value"><xsl:value-of select="$transDescription"/></xsl:attribute></definition> -->
<!-- 	      </concept> -->
<!-- 	    </xsl:for-each>		 -->
<!-- 	  </CodeSystem> -->
<!-- 	</resource> -->
<!--       </entry> -->

<!--       <xsl:for-each select="$uniqueActors"> -->
<!-- 	<xsl:variable name="actor" select="."/> -->
<!-- 	<xsl:variable name="actorCode" select="bpmn:extensionElements/zeebe:properties/zeebe:property[@name = 'ig-code']/@value[1]"/> -->
<!-- 	<xsl:variable name="actorName" select="@name"/> -->
<!-- 	<xsl:variable name="actorDescription" select="bpmn:documentation/text()"/> -->
<!-- 	<xsl:variable name="actorType" select="bpmn:extensionElements/zeebe:properties/zeebe:property[@name='ig-actor-type'][1]/@value"/> -->
<!-- 	<xsl:variable name="actor-page-slug">actor-<xsl:value-of select="$actorCode"/></xsl:variable> -->
	
<!-- 	<xsl:message> -->
<!-- # Unique actor: <xsl:value-of select="$actorName"/> -->
<!-- #  Found actorType (<xsl:value-of select="$actorType"/>) for role (<xsl:value-of select="$actorName"/>) with code (<xsl:value-of select="$actorCode"/>)  -->

<!-- touch input/pagecontent/<xsl:value-of select="$actor-page-slug"/>.md  -->

<!-- cat &lt;&lt; EOF >> input/pagecontent/actors.md -->
<!-- ###  <xsl:value-of select="$actorName"/> {#<xsl:value-of select="$actorCode"/>} -->
<!-- Type: (<xsl:value-of select="$actorType"/>) -->


<!-- Description: <xsl:value-of select="$actorDescription"/> -->
<!-- {% include <xsl:value-of select="$actor-page-slug"/>.md %} -->
<!-- 	</xsl:message> -->


<!-- 	<xsl:message> -->

<!-- The <xsl:value-of select="$actorName"/> actor participates in the following transactions as a source:</xsl:message>	     -->
<!-- 	<xsl:for-each select="$collab/bpmn:participant"> -->
<!-- 	  <xsl:variable name="processId" select="@processRef"/> -->
<!-- 	  <xsl:variable name="process"  select="$processes[@id = $processId]"/> -->
<!-- 	  <xsl:for-each select="$actor/bpmn:flowNodeRef">  <!-\- this is a task ID.  we want check it is under actor's lane-\-> -->
<!-- 	    <xsl:variable name="arrowSrc" select="."/> -->
<!-- 	    <xsl:for-each select="($process/bpmn:sendTask)[@id = $arrowSrc]"> -->
<!-- 	      <xsl:for-each select="$arrows[@sourceRef = $arrowSrc]"> -->
<!-- 		<xsl:variable name="trans-name" select="@name"/> -->
<!-- 		<xsl:variable -->
<!-- 		    name="trans-code" -->
<!-- 		    select="bpmn:extensionElements/zeebe:properties/zeebe:property[@name='ig-code'][1]/@value"/> -->
<!-- 		<xsl:message>-  Transaction: &lt;a href="transaction-<xsl:value-of select="$trans-code"/>.hmtl"><xsl:value-of select="$trans-name"/> (<xsl:value-of select="$trans-code"/>)&lt;/a> </xsl:message> -->
<!-- 	      </xsl:for-each> -->
<!-- 	    </xsl:for-each> -->
<!-- 	    <xsl:message/> -->
<!-- 	  </xsl:for-each> -->
<!-- 	</xsl:for-each> -->

<!-- 	<xsl:message> -->

<!-- The <xsl:value-of select="$actorName"/> actor participates in the following transactions as a target:</xsl:message> -->

<!-- 	<xsl:for-each select="$collab/bpmn:participant"> -->
<!-- 	  <xsl:variable name="processId" select="@processRef"/> -->
<!-- 	  <xsl:variable name="process"  select="$processes[@id = $processId]"/> -->
<!-- 	  <xsl:for-each select="$actor/bpmn:flowNodeRef">  <!-\- this is a task ID.  we want check it is under actor's lane-\-> -->
<!-- 	    <xsl:variable name="arrowSrc" select="."/> -->
<!-- 	    <xsl:for-each select="($process/bpmn:receiveTask)[@id = $arrowSrc]"> -->
<!-- 	      <xsl:for-each select="$arrows[@sourceRef = $arrowSrc]"> -->
<!-- 		<xsl:variable name="trans-name" select="@name"/> -->
<!-- 		<xsl:variable -->
<!-- 		    name="trans-code" -->
<!-- 		    select="bpmn:extensionElements/zeebe:properties/zeebe:property[@name='ig-code'][1]/@value"/> -->
<!-- 		<xsl:message>-  Transaction: &lt;a href="transaction-<xsl:value-of select="$trans-code"/>.html"><xsl:value-of select="$trans-name"/> (<xsl:value-of select="$trans-code"/>)&lt;/a> </xsl:message> -->
<!-- 	      </xsl:for-each> -->
<!-- 	    </xsl:for-each> -->
<!-- 	    <xsl:message/> -->
<!-- 	  </xsl:for-each> -->
<!-- 	</xsl:for-each> -->
	

<!-- 	<xsl:message> -->

<!-- The <xsl:value-of select="$actorName"/> actor participates in the following questionnaires:</xsl:message> -->


<!-- 	<xsl:for-each select="$collab/bpmn:participant"> -->
<!-- 	  <xsl:variable name="processId" select="@processRef"/> -->
<!-- 	  <xsl:variable name="process"  select="$processes[@id = $processId]"/> -->
<!-- 	  <xsl:for-each select="$actor/bpmn:flowNodeRef">  <!-\- this is a task ID.  we want check it is under actor's lane-\-> -->
<!-- 	    <xsl:variable name="arrowSrc" select="."/> -->


<!-- 	    <xsl:for-each select="($process/bpmn:userTask)[@id = $arrowSrc]"> -->
<!-- 	      <xsl:variable -->
<!-- 		  name="task-code" -->
<!-- 		  select="bpmn:extensionElements/zeebe:properties/zeebe:property[@name='ig-code'][1]/@value"/> -->
<!-- 	      <xsl:variable name="task-name" select="@name"/> -->
<!-- 	      <xsl:message>-  Questionnaire: &lt;a href="Questionnaire-<xsl:value-of select="$task-code"/>.html"><xsl:value-of select="$task-name"/> (<xsl:value-of select="$task-code"/>)&lt;/a> </xsl:message> -->
	      
<!-- 	    </xsl:for-each> -->
<!-- 	  </xsl:for-each> -->
<!-- 	</xsl:for-each> -->
<!-- 	<xsl:message> -->
<!-- EOF -->
<!-- 	</xsl:message> -->

<!-- 	  <entry> -->

	    
<!-- 	    <resource> -->
<!-- 	      <ActorDefinition > -->
<!-- 		<id> -->
<!-- 		  <xsl:attribute name="value"><xsl:value-of select="$actorCode"/></xsl:attribute>  -->
<!-- 		</id> -->
<!-- 		<version><xsl:value-of select="$ig-version"/></version> -->
<!-- 		<publisher><xsl:value-of select="$ig-publisher"/></publisher> -->
<!-- 		<meta> -->
<!-- 		  <xsl:choose> -->
<!-- 		    <xsl:when test="$actorType!= 'system'"> -->
<!-- 		      <profile value="http://smart.who.int/base/StructureDefinition/SGPersona"/> -->
<!-- 		    </xsl:when> -->
<!-- 		    <xsl:otherwise> -->
<!-- 		      <profile value="http://smart.who.int/base/StructureDefinition/SGActor"/> -->
<!-- 		    </xsl:otherwise> -->
<!-- 		  </xsl:choose> -->
<!-- 		</meta> -->
<!-- 		<type><xsl:attribute name="value"><xsl:value-of select="$actorType"/></xsl:attribute></type> -->
<!-- 		<extension url="http://smart.who.int/base/StructureDefinition/Sgcode"> -->
<!-- 		  <valueCoding> -->
<!-- 		    <system><xsl:attribute name="value"><xsl:value-of select="$actors-CS-url"/></xsl:attribute></system> -->
<!-- 		    <code><xsl:attribute name="value"><xsl:value-of select="$actorCode"/></xsl:attribute></code> -->
<!-- 		  </valueCoding> -->
<!-- 		</extension> -->
<!-- 		<identifier> -->
<!-- 		  <value><xsl:attribute name="value"><xsl:value-of select="$actorCode"/></xsl:attribute></value> -->
<!-- 		</identifier> -->
<!-- 		<name><xsl:attribute name="value"><xsl:value-of select="$actorName"/></xsl:attribute></name> -->
<!-- 		<title><xsl:attribute name="value"><xsl:value-of select="$actorName"/></xsl:attribute></title> -->
<!-- 		<status value="draft"/> -->
<!-- 		<experimental value="false"/> -->
<!-- 		<description><xsl:attribute name="value"> -->
<!-- 		  <xsl:value-of select="$actorDescription"/> -->
<!-- 		  <p> -->
<!-- 		    More details of this transaction may be found on the  -->
<!-- 		    <a><xsl:attribute name="href">actors.html#<xsl:value-of select="$actorCode"/></xsl:attribute></a> -->
<!-- 		    page. -->
<!-- 		  </p> -->
<!-- 		</xsl:attribute> -->
<!-- 		</description> -->
<!-- 	      </ActorDefinition> -->
<!-- 	    </resource> -->
<!-- 	  </entry> -->
<!-- 	</xsl:for-each> -->

<!--   <xsl:template match="*"> -->
<!--     <xsl:copy> -->
<!--       <xsl:copy-of select="@*" /> -->
<!--       <xsl:apply-templates /> -->
<!--     </xsl:copy> -->
<!--   </xsl:template> -->
<!-- </xsl:stylesheet> -->
	
<!-- 	<xsl:for-each select="$collab/bpmn:participant"> -->
<!-- 	  <!-\- loop through all the process named in the collaboration and create a graph for each -\-> -->
<!-- 	  <xsl:variable name="processId" select="@processRef"/> -->
<!-- 	  <xsl:message># Processing collab process: <xsl:value-of select="$processId"/></xsl:message> -->




<!-- 	  <xsl:for-each select="$processes[@id = $processId]"> -->
<!-- 	    <xsl:variable name="processName" select="@name"/> -->
<!-- 	    <xsl:variable name="processCode" select="bpmn:extensionElements/zeebe:properties/zeebe:property[@name='ig-code'][1]/@value"/> -->
<!-- 	    <xsl:variable name="processDesc" select="bpmn:documentation/text()"/> -->
<!-- 	    <xsl:variable name="processActors" select=".//bpmn:lane"/> -->
<!-- 	    <xsl:variable name="userTasks" select="bpmn:userTask[bpmn:extensionElements/zeebe:properties/zeebe:property[@name='ig-code']/@value != '']"/> -->
<!-- 	    <xsl:variable name="rules" select="bpmn:businessRuleTask[bpmn:extensionElements/zeebe:properties/zeebe:property[@name='ig-code']/@value != '']"/> -->
<!-- 	    <xsl:variable name="sendTasks" select="bpmn:sendTask[bpmn:extensionElements/zeebe:properties/zeebe:property[@name='ig-code']/@value != '']"/> -->
<!-- 	    <xsl:variable name="receiveTasks" select="bpmn:receiveTask"/> -->
<!-- 	    <xsl:variable name="processArrows" select="bpmn:sequenceFlow[bpmn:extensionElements/zeebe:properties/zeebe:property[@name='ig-code']/@value != '']"/> -->
	    
<!-- 	    <xsl:message># Check process: (<xsl:value-of select="$processName"/>) - (<xsl:value-of select="$processId"/>)</xsl:message> -->
<!-- 	    <!-\- loop through the userTasks and stub out a SGQuestionnaire profile and associated activityDef'n (maybe) -\-> -->
<!-- 	    <xsl:for-each select="$userTasks"> -->
<!-- 	      <xsl:variable name="taskId" select="@id"/> -->
<!-- 	      <xsl:variable name="taskName" select="@name"/> -->
<!-- 	      <xsl:variable name="taskCode" select="bpmn:extensionElements/zeebe:properties/zeebe:property[@name='ig-code'][1]/@value"/> -->
<!-- 	      <xsl:variable name="formId" select="bpmn:extensionElements/zeebe:formDefinition/@formId"/> -->
<!-- 	      <xsl:variable name="qId" select="concat('SGQuestionaire-',$taskCode)"/> -->
	      
<!-- 	      <StructureDefinition> -->
<!-- 		<id><xsl:attribute name="value"><xsl:value-of select="$taskCode"/></xsl:attribute></id> -->
<!-- 		<version><xsl:value-of select="$ig-version"/></version> -->
<!-- 		<publisher><xsl:value-of select="$ig-publisher"/></publisher> -->
<!-- 		<extension url="http://hl7.org/fhir/StructureDefinition/structuredefinition-implements"> -->
<!-- 		  <valueUri value="http://hl7.org/fhir/StructureDefinition/CanonicalResource"/> -->
<!-- 		</extension> -->
<!-- 		<url><xsl:attribute name="value"><xsl:value-of select="concat($ig-url,'/StructureDefinition/',$qId)"/></xsl:attribute></url> -->
<!-- 		<version><xsl:attribute name="value"><xsl:value-of select="$ig-version"/></xsl:attribute></version> -->
<!-- 		<name><xsl:attribute name="value"><xsl:value-of select="$qId"/></xsl:attribute></name> -->
<!-- 		<status value="draft"/> -->
<!-- 		<publisher><xsl:attribute name="value"><xsl:value-of select="$ig-publisher"/></xsl:attribute></publisher> -->
<!-- 		<name><xsl:value-of select="$taskName"/></name> -->
<!-- 		<baseDefinition value="http://smart.who.int/base/StructureDefinition/SGGraphDefinition"/> -->
<!-- 		<derivation value="constraint"/> -->
<!-- 		<differential> -->
<!-- 		  <element id="Questionnaire"> -->
<!-- 		    <path value="Questionnaire"/> -->
<!-- 		  </element> -->
<!-- 		  <element id="Questionnaire.name"> -->
<!-- 		    <path value="Questionnaire.name"/> -->
<!-- 		    <patternCode><xsl:attribute name="value"><xsl:value-of select="$taskName"/></xsl:attribute></patternCode> -->
<!-- 		  </element> -->
<!-- 		  <element id="Questionnaire.code"> -->
<!-- 		    <path value="Questionnaire.code"/> -->
<!-- 		    <patternCoding> -->
<!-- 		      <xsl:attribute name="code"><xsl:value-of select="$taskCode"/></xsl:attribute> -->
<!-- 		      <xsl:attribute name="system"><xsl:value-of select="$quest-CS-url"/></xsl:attribute> -->
<!-- 		    </patternCoding> -->
<!-- 		  </element> -->
<!-- 		</differential> -->
<!-- 	      </StructureDefinition> -->
<!-- 	    </xsl:for-each> -->
	    

<!-- 	    <!-\- loop through arrows looking for sendTask receiveTask pairs to use for SGtransactions a-\-> -->
<!-- 	    <xsl:for-each select="$processArrows"> -->

<!-- 	      <xsl:variable name="linkSrc" select="@sourceRef"/> -->
<!-- 	      <xsl:variable name="linkTgt" select="@targetRef"/> -->
<!-- 	      <xsl:variable name="linkId" select="@id"/> -->
<!-- 	      <xsl:variable name="linkCode" select="bpmn:extensionElements/zeebe:properties/zeebe:property[@name='ig-code'][1]/@value"/> -->
<!-- 	      <xsl:variable name="linkName" select="@name"/> -->
<!-- 	      <xsl:variable name="linkDesc" select="bpmn:documentation/text()"/> -->
<!-- 	      <!-\- -->
<!-- 		  <xsl:variable name="linkTE" select="bpmn:extensionElements/zeebe:properties/zeebe:property[@name='triggerEvents'][1]/@value"/>	    	  -->
<!-- 		  <xsl:variable name="linkMS" select="bpmn:extensionElements/zeebe:properties/zeebe:property[@name='messageSemantics'][1]/@value"/> -->
<!-- 		  <xsl:variable name="linkEA" select="bpmn:extensionElements/zeebe:properties/zeebe:property[@name='expectedActions'][1]/@value"/> -->
<!-- 	      -\-> -->

              
              
<!-- 	      <!-\-only want to create a transaction between bpmn:sendTask and bpmn:receiveTask sequenceFlows -\-> -->
<!-- 	      <xsl:for-each  select="$sendTasks[@id=$linkSrc]"> -->
<!-- 		<xsl:variable name="sendTask" select="."/> -->
<!-- 		<xsl:for-each select="$receiveTasks[@id=$linkTgt]"> -->
<!-- 		  <xsl:variable name="receiveTask" select="."/> -->
<!-- 		  <xsl:message># Send/Receive task pairs: (<xsl:value-of select="$sendTask/@id"/>)->(<xsl:value-of select="$receiveTask/@id"/>) </xsl:message> -->
<!-- 		  <xsl:message># Send/Receive task pairs: (<xsl:value-of select="$linkSrc"/>)->(<xsl:value-of select="$linkTgt"/>) </xsl:message> -->
<!-- 		  <!-\- now we know the source(send) and target(receive) tasks.  we now need to get the lane that they are in -\-> -->
<!-- 		  <xsl:for-each  select="$innerActors"> -->
<!-- 		    <xsl:message># Checking if <xsl:value-of select="./bpmn:flowNodeRef"/> = <xsl:value-of select="$linkSrc"/></xsl:message> -->
<!-- 		  </xsl:for-each> -->
<!-- 		  <xsl:for-each  select="$innerActors[./bpmn:flowNodeRef = $linkSrc][1]"> -->
<!-- 		    <xsl:variable name="actorSrc" select="."/> -->
<!-- 		    <xsl:variable name="actorSrcId" select="$actorSrc/@id"/> -->
<!-- 		    <xsl:variable name="actorSrcCode" select="bpmn:extensionElements/zeebe:properties/zeebe:property[@name='ig-code'][1]/@value"/> -->
<!-- 		    <xsl:variable name="actorSrcDesc" select="bpmn:documentation/text()"/> -->
		    
<!-- 		    <xsl:message># Got source actor: <xsl:value-of select="$actorSrcId"/></xsl:message> -->
<!-- 		    <xsl:for-each  select="$innerActors[./bpmn:flowNodeRef = $linkTgt][1]"> -->
<!-- 		      <xsl:variable name="actorTgt" select="."/> -->
<!-- 		      <xsl:variable name="actorTgtId" select="$actorTgt/@id"/> -->
<!-- 		      <xsl:variable name="actorTgtCode" select="bpmn:extensionElements/zeebe:properties/zeebe:property[@name='ig-code'][1]/@value"/> -->
<!-- 		      <xsl:variable name="actorTgtDesc" select="bpmn:documentation/text()"/> -->
		      
<!-- 		      <xsl:message># Got target actor: <xsl:value-of select="$actorTgtId"/></xsl:message> -->
<!-- 		      <entry> -->

<!-- 			<resource> -->
<!-- 			  <GraphDefinition> -->
<!-- 			    <id><xsl:attribute name="value"><xsl:value-of select="$linkCode"/></xsl:attribute></id> -->
<!-- 			    <version><xsl:value-of select="$ig-version"/></version> -->
<!-- 			    <publisher><xsl:value-of select="$ig-publisher"/></publisher> -->
			    
<!-- 			    <meta> -->
<!-- 	      		      <profile value="http://smart.who.int/base/StructureDefinition/SGTransaction"/> -->
<!-- 			    </meta> -->
			    
<!-- 			    <name><xsl:attribute name="value"><xsl:value-of select="$linkName"/></xsl:attribute></name> -->
<!-- 			    <description> -->
<!-- 			      <xsl:attribute name="value"> -->
<!-- 				<xsl:value-of select="$linkDesc"/> -->
<!-- 				<p> -->
<!-- 				  More details of this transaction may be found on the  -->
<!-- 				  <a><xsl:attribute name="href">transactions.html#<xsl:value-of select="$linkCode"/></xsl:attribute></a> -->
<!-- 				  page. -->
<!-- 				</p> -->
<!-- 			      </xsl:attribute> -->
<!-- 			    </description> -->
<!-- 			    <status value="active"/> -->

<!-- 			    <xsl:variable name="link-page-slug">transaction-<xsl:value-of select="$linkCode"/></xsl:variable> -->
<!-- 			    <xsl:message> -->
<!-- # -->
<!-- # Creating tranasaction page slugs for <xsl:value-of select="$linkCode"/>} -->
<!-- # -->
<!-- touch input/pagecontent/<xsl:value-of select="$link-page-slug"/>-preamble.md  -->
<!-- touch input/pagecontent/<xsl:value-of select="$link-page-slug"/>-trigger-events.md  -->
<!-- touch input/pagecontent/<xsl:value-of select="$link-page-slug"/>-message-semantics.md  -->
<!-- touch input/pagecontent/<xsl:value-of select="$link-page-slug"/>-expected-actions-semantics.md  -->

<!-- cat &lt;&lt; EOF >> input/pagecontent/transactions.md -->
<!-- ###  <xsl:value-of select="$linkName"/> {#<xsl:value-of select="$linkCode"/>} -->

<!-- (<xsl:value-of select="$linkName"/>) -->
<!-- <xsl:value-of select="$linkDesc"/> -->

<!-- {% include <xsl:value-of select="$link-page-slug"/>-preamble.md %} -->
<!-- #### Trigger Events -->
<!-- {% include <xsl:value-of select="$link-page-slug"/>-trigger-events.md %} -->
<!-- #### Message Semantics -->
<!-- {% include <xsl:value-of select="$link-page-slug"/>-message-semantics.md %} -->
<!-- #### Expected Actions -->
<!-- {% include <xsl:value-of select="$link-page-slug"/>-expected-actions-semantics.md %} -->

<!-- EOF -->

<!-- 			    </xsl:message> -->


			  
<!-- 			    <experimental value="false"/> -->
<!-- 			    <node> -->
<!-- 			      <nodeId><xsl:value-of select="$actorSrcCode"/></nodeId> -->
<!-- 			      <type>ActorDefinition</type> -->
<!-- 			      <extension url="http://smart.who.int/base/StructureDefinition/Sgactor"> -->
<!-- 				<valueCoding> -->
<!-- 				  <system><xsl:attribute name="value"><xsl:value-of select="$actors-CS-url"/></xsl:attribute></system> -->
<!-- 				  <code><xsl:attribute name="value"><xsl:value-of select="$actorSrcCode"/></xsl:attribute></code> -->
<!-- 				</valueCoding> -->
<!-- 			      </extension> -->
<!-- 			    </node> -->
<!-- 			    <node> -->
<!-- 			      <nodeId><xsl:value-of select="$actorTgtCode"/></nodeId> -->
<!-- 			      <type>ActorDefinition</type> -->
<!-- 			      <extension url="http://smart.who.int/base/StructureDefinition/Sgactor"> -->
<!-- 				<valueCoding> -->
<!-- 				  <system><xsl:attribute name="value"><xsl:value-of select="$actors-CS-url"/></xsl:attribute></system> -->
<!-- 				  <code><xsl:attribute name="value"><xsl:value-of select="$actorTgtCode"/></xsl:attribute></code> -->
<!-- 				</valueCoding> -->
<!-- 			      </extension> -->
<!-- 			    </node> -->

<!-- 			    <link> -->
<!-- 			      <sourceId><xsl:value-of select="$actorSrcCode"/></sourceId> -->
<!-- 			      <targetId><xsl:value-of select="$actorTgtCode"/></targetId> -->

<!-- 			      <extension url="http://smart.who.int/base/StructureDefinition/Sgcode"> -->
<!-- 				<valueCoding> -->
<!-- 				  <system><xsl:attribute name="value"><xsl:value-of select="$trans-CS-url"/></xsl:attribute></system> -->
<!-- 				  <code><xsl:attribute name="value"><xsl:value-of select="$linkCode"/></xsl:attribute></code> -->
<!-- 				</valueCoding> -->
<!-- 			      </extension> -->
<!-- 			      <!-\- <extension url="http://smart.who.int/base/StructureDefinition/Markdown"> -\-> -->
<!-- 			      <!-\-   <valueMarkdown><xsl:attribute name="value"><xsl:value-of select="$linkTE"/></xsl:attribute></valueMarkdown> -\-> -->
<!-- 			      <!-\- </extension> -\-> -->
<!-- 			      <!-\- <extension url="http://smart.who.int/base/StructureDefinition/Markdown"> -\-> -->
<!-- 			      <!-\-   <valueMarkdown><xsl:attribute name="value"><xsl:value-of select="$linkMS"/></xsl:attribute></valueMarkdown> -\-> -->
<!-- 			      <!-\- </extension> -\-> -->
<!-- 			      <!-\- <extension url="http://smart.who.int/base/StructureDefinition/Markdown"> -\-> -->
<!-- 			      <!-\-   <valueMarkdown><xsl:attribute name="value"><xsl:value-of select="$linkEA"/></xsl:attribute></valueMarkdown> -\-> -->
<!-- 			      <!-\- </extension>		   -\-> -->
<!-- 			    </link> -->
<!-- 			  </GraphDefinition> -->
<!-- 			</resource> -->
<!-- 		      </entry> -->
<!-- 		    </xsl:for-each> -->
<!-- 		  </xsl:for-each> -->
<!-- 		</xsl:for-each> -->
<!-- 	      </xsl:for-each> -->
<!-- 	    </xsl:for-each> -->
<!-- 	  </xsl:for-each> -->
	  <!-- <Html> -->
	  <!--   <body> -->
	  <!-- 	<h2>My CD Collection</h2> -->
	  <!-- 	<table border="1"> -->
	  <!-- 	  <tr bgcolor="#9acd32"> -->
	  <!--         <th>Title</th> -->
	  <!--         <th>Artist</th> -->
	  <!-- 	  </tr> -->
	  <!-- 	  <xsl:for-each select="catalog/cd"> -->
	  <!-- 	    <tr> -->
	  <!--           <td><xsl:value-of select="title" /></td> -->
	  <!--           <td><xsl:value-of select="artist" /></td> -->
	  <!-- 	    </tr> -->
	  <!-- 	  </xsl:for-each> -->
	  <!-- 	</table> -->
	  <!--   </body> -->
	  <!-- </html> -->
  <!-- 	</xsl:for-each> -->

  <!--   </Bundle> -->
    
  <!-- </xsl:template> -->

  
  <!-- pretty print output -->

