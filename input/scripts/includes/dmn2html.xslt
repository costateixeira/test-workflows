<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.1"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:dmn="https://www.omg.org/spec/DMN/20240513/MODEL/"
    xmlns:xhtml="http://www.w3.org/1999/xhtml"
    exclude-result-prefixes="dmn">

  <xsl:output
      method="html"
      indent="yes"
      encoding="UTF-8"
      
      doctype-public="-//W3C//DTD HTML 4.01//EN"
      doctype-system="http://www.w3.org/TR/html4/strict.dtd"
      omit-xml-declaration="yes"/>

  <xsl:template match="/">
    <xhtml:div class="decision-table">
      <xsl:apply-templates select="//dmn:decision"/>
    </xhtml:div>
  </xsl:template>

  <xsl:template match="dmn:decision">
    <xhtml:table class="decision">
      <!-- First row: Decision ID and name -->
      <xhtml:tr class="decision-header">
        <xhtml:td class="row-label">Decision ID</xhtml:td>
        <xhtml:td colspan="{count(dmn:decisionTable/dmn:input) + count(dmn:decisionTable/dmn:output) + count(dmn:decisionTable/dmn:annotation)}">
          <span class="decision-id">
            <xsl:value-of select="@id"/>
          </span>
	  <xsl:if test="@id != @name">
            <span class="decision-name">
              <xsl:value-of select="@name"/>
            </span>
	  </xsl:if>
        </xhtml:td>
      </xhtml:tr>
      <!-- 2nd row: Business Rule -->
      <xsl:if test="dmn:question">
	<xhtml:tr class="decision-header">
	  <xhtml:td class="row-label">Business Rule</xhtml:td>
	  <xhtml:td colspan="{count(dmn:decisionTable/dmn:input) + count(dmn:decisionTable/dmn:output) + count(dmn:decisionTable/dmn:annotation)}">
            <span class="decision-id">
              <xsl:value-of select="dmn:question"/>
            </span>
          </xhtml:td>
	</xhtml:tr>
      </xsl:if>

      <!-- 3rd row: Business Rule -->
      <xsl:if test="dmn:usingTask">
	<xhtml:tr class="decision-header">
	  <xhtml:td class="row-label">Trigger</xhtml:td>
	  <xhtml:td colspan="{count(dmn:decisionTable/dmn:input) + count(dmn:decisionTable/dmn:output) + count(dmn:decisionTable/dmn:annotation)}">
            <span class="decision-id">
	      <a href="{dmn:usingTask/@href}"><xsl:value-of select="dmn:usingTask/@href"/></a>
            </span>
          </xhtml:td>
	</xhtml:tr>
      </xsl:if>

      <xhtml:tr class="decision-header">
	<xhtml:td class="input"/>
	<xhtml:td colspan="{count(dmn:decisionTable/dmn:input)}">Inputs</xhtml:td>
	<xhtml:td colspan="{count(dmn:decisionTable/dmn:output)}">Ouputs</xhtml:td>
      </xhtml:tr>
      
      <!-- Fourth row: Inputs and outputs -->
      <xhtml:tr class="io-row">
        <xhtml:td class="row-label">Inputs/Outputs</xhtml:td>
        <xsl:for-each select=".//dmn:input">	  
          <xhtml:td class="input" style="vertical-align: top;">
	    <!-- <xsl:variable name="inputPos" select="position()" /> -->
            <!-- <xsl:variable name="inputDef" select="../../dmn:input[position() = $inputPos]" /> -->
	    <xsl:variable name="inputDef" select="." />
            <strong>
	      <xsl:variable name="csURL">CodeSystem-DT.html#:~:text=<xsl:value-of select="$inputDef/@label"/></xsl:variable>
	      <xsl:element name="a">
		<xsl:attribute name="href">
		  <xsl:value-of select="$csURL"/>
		</xsl:attribute>
		<xsl:value-of select="$inputDef/@label"/>
	      </xsl:element>
            </strong>
            <xsl:if test="$inputDef/dmn:inputExpression/dmn:text">
	      <span style="font-weight:normal;vertical-align: center;">
		<xsl:text> </xsl:text>s
		<xsl:value-of select="$inputDef/dmn:inputExpression/dmn:text"/>
	      </span>
            </xsl:if>
          </xhtml:td>
        </xsl:for-each>
        <xsl:for-each select=".//dmn:output">
          <xhtml:td class="output"  style="vertical-align: top;">
	    <xsl:variable name="outputDef" select="." />
	    <strong>
	      <xsl:variable name="csURL">CodeSystem-DT.html#:~:text=<xsl:value-of select="$outputDef/@label"/></xsl:variable>
	      <xsl:element name="a">
		<xsl:attribute name="href">
		  <xsl:value-of select="$csURL"/>
		</xsl:attribute>
		<xsl:value-of select="$outputDef/@label"/>
	      </xsl:element>
	    </strong>
          </xhtml:td>
        </xsl:for-each>
        <xsl:for-each select=".//dmn:annotation">
          <xhtml:td class="annotation">
            <xsl:value-of select="@label"/>
          </xhtml:td>
        </xsl:for-each>
      </xhtml:tr>
      <!-- Rule rows -->
      <xsl:for-each select=".//dmn:rule">
        <xhtml:tr class="rule">
          <xhtml:td class="row-label">
            <xsl:variable name="ruleId" select="@id"/>
            <xsl:value-of select="substring-after($ruleId, 'row-')"/>
          </xhtml:td>
	  <xsl:for-each select="dmn:inputEntry">
            <xhtml:td style="vertical-align: top;">
	      <!--<xsl:variable name="inputEntryPos" select="position()" />-->
	      <!-- <xsl:variable name="inputEntryDef" select="../../dmn:inputEntry[position() = $inputEntryPos]" />-->
	      <xsl:variable name="inputEntryDef" select="." />
              <strong >
		<xsl:variable name="csURL">CodeSystem-DT.html#:~:text=<xsl:value-of select="$inputEntryDef/dmn:text"/></xsl:variable>
		<xsl:element name="a">
		  <xsl:attribute name="href">
		    <xsl:value-of select="$csURL"/>
		  </xsl:attribute>
		  <xsl:value-of select="$inputEntryDef/dmn:text"/>
		</xsl:element>
              </strong>
              <xsl:if test="$inputEntryDef/dmn:description">
		<span style="font-weight:normal;">
		  <xsl:text> </xsl:text>
		  <xsl:value-of select="$inputEntryDef/dmn:description"/>
		</span>
              </xsl:if>
              <xsl:if test="normalize-space(.)">
		<xsl:text>: </xsl:text>
		<xsl:value-of select="."/>
              </xsl:if>
            </xhtml:td>
	  </xsl:for-each>
          <xsl:for-each select="dmn:outputEntry">
            <xhtml:td class="outputEntry">
              <xsl:value-of select="."/>
            </xhtml:td>
          </xsl:for-each>
          <xsl:for-each select="dmn:annotationEntry">
            <xhtml:td class="annotationEntry">
              <xsl:value-of select="."/>
            </xhtml:td>
          </xsl:for-each>
        </xhtml:tr>
      </xsl:for-each>
    </xhtml:table>
  </xsl:template>
</xsl:stylesheet>
