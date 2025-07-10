<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:dmn="https://www.omg.org/spec/DMN/20240513/MODEL/"
    exclude-result-prefixes="dmn">

  <xsl:output method="html" indent="yes" encoding="UTF-8"/>

  <xsl:template match="/">
    <html>
      <head>
        <title>
          <xsl:value-of select="//dmn:decision/@name"/>
        </title>
        <link rel="stylesheet" type="text/css" href="includes/dmn.css"/>
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
        <td colspan="100">
          <span class="decision-id">
            <xsl:value-of select="@id"/>
          </span>
          <span class="decision-name">
            <xsl:value-of select="@name"/>
          </span>
        </td>
      </tr>
      <!-- Second row: Inputs and outputs -->
      <tr class="io-row">
        <td class="row-label">Inputs/Outputs</td>
        <xsl:for-each select=".//dmn:input">
          <td class="input">
            <xsl:value-of select="@label"/>
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
            <td class="inputEntry">
              <xsl:value-of select="."/>
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
