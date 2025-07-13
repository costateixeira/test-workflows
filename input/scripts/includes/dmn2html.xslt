<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:dmn="https://www.omg.org/spec/DMN/20240513/MODEL/"
    exclude-result-prefixes="dmn">

  <xsl:output
      method="xml"
      indent="yes"
      encoding="UTF-8"
      doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
      doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
      omit-xml-declaration="yes"/>

  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <title>
          <xsl:value-of select="//dmn:decision/@name"/>
        </title>
        <link rel="stylesheet" type="text/css" href="dmn.css"/>
      </head>
      <body>
        <xsl:apply-templates select="//dmn:decision"/>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="dmn:decision">
    <table class="decision">
      <!-- First row: Decision ID and name -->
      <tr class="decision-header">
        <td class="row-label">Decision ID</td>
        <td colspan="{count(dmn:decisionTable/dmn:input) + count(dmn:decisionTable/dmn:output) + count(dmn:decisionTable/dmn:annotation)}">
          <span class="decision-id">
            <xsl:value-of select="@id"/>
          </span>
	  <xsl:if test="@id != @name">
            <span class="decision-name">
              <xsl:value-of select="@name"/>
            </span>
	  </xsl:if>
        </td>
      </tr>
      <!-- 2nd row: Business Rule -->
      <xsl:if test="dmn:question">
	<tr class="decision-header">
	  <td class="row-label">Business Rule</td>
	  <td colspan="{count(dmn:decisionTable/dmn:input) + count(dmn:decisionTable/dmn:output) + count(dmn:decisionTable/dmn:annotation)}">
            <span class="decision-id">
              <xsl:value-of select="dmn:question"/>
            </span>
          </td>
	</tr>
      </xsl:if>

      <!-- 3rd row: Business Rule -->
      <xsl:if test="dmn:usingTask">
	<tr class="decision-header">
	  <td class="row-label">Trigger</td>
	  <td colspan="{count(dmn:decisionTable/dmn:input) + count(dmn:decisionTable/dmn:output) + count(dmn:decisionTable/dmn:annotation)}">
            <span class="decision-id">
	      <a href="{dmn:usingTask/@href}"><xsl:value-of select="dmn:usingTask/@href"/></a>
            </span>
          </td>
	</tr>
      </xsl:if>

      <tr class="decision-header">
	<td class="input"/>
	<td colspan="{count(dmn:decisionTable/dmn:input)}">Inputs</td>
	<td colspan="{count(dmn:decisionTable/dmn:output)}">Ouputs</td>
      </tr>
      
      <!-- Fourth row: Inputs and outputs -->
      <tr class="io-row">
        <td class="row-label">Inputs/Outputs</td>
        <xsl:for-each select=".//dmn:input">	  
          <td class="input" style="vertical-align: top;">
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
          </td>
        </xsl:for-each>
        <xsl:for-each select=".//dmn:output">
          <td class="output">
            <xsl:value-of select="@label"/>
          </td>
        </xsl:for-each>
        <xsl:for-each select=".//dmn:annotation">
          <td class="annotation">
            <xsl:value-of select="@label"/>
          </td>
        </xsl:for-each>
      </tr>
      <!-- Rule rows -->
      <xsl:for-each select=".//dmn:rule">
        <tr class="rule">
          <td class="row-label">
            <xsl:variable name="ruleId" select="@id"/>
            <xsl:value-of select="substring-after($ruleId, 'row-')"/>
          </td>
	  <xsl:for-each select="dmn:inputEntry">
            <td style="vertical-align: top;">
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
            </td>
	  </xsl:for-each>
          <xsl:for-each select="dmn:outputEntry">
            <td class="outputEntry">
              <xsl:value-of select="."/>
            </td>
          </xsl:for-each>
          <xsl:for-each select="dmn:annotationEntry">
            <td class="annotationEntry">
              <xsl:value-of select="."/>
            </td>
          </xsl:for-each>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>
</xsl:stylesheet>
