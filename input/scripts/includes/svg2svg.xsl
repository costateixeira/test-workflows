<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
		xmlns:svg="http://www.w3.org/2000/svg"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		>

  

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="svg:text[ancestor::svg:g[@data-element-id != '']]">
    <xsl:variable name="id" select="ancestor::svg:g[@data-element-id != ''][1]/@data-element-id"/>
    <xsl:variable name="url"><xsl:text>DD.html#</xsl:text><xsl:value-of select="$id"/></xsl:variable>
    <svg:a >
      <xsl:attribute name="href"><xsl:value-of select="$url"/></xsl:attribute>
      <xsl:copy-of select="." />
    </svg:a>
  </xsl:template>

  
  <xsl:template match="/">
    <xsl:apply-templates select="node()" />
  </xsl:template>

  
</xsl:stylesheet>
