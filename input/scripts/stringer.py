import hashlib
import logging
import re


def to_hash(input:str,len:int):
  return input[:len -10] + str(hashlib.shake_256(input.encode()).hexdigest(5))

  



def xml_escape(input):
  if ( not (isinstance(input,str))):
    return ""
  # see https://stackoverflow.com/questions/1546717/escaping-strings-for-use-in-xml
  return input.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;").replace("'", "&apos;")    

def escape(input):
  if ( not (isinstance(input,str))):
    return None
  return input.replace('"', r'\"')


def escape_code(input):
  original = input
  if ( not (isinstance(input,str))):
    return None
  input = input.strip()
  input = re.sub(r"['\"]","",input)
  #SUSHI BUG on processing codes with double quote.  sushi fails
  #Example \"Bivalent oral polio vaccine (bOPV)–inactivated polio vaccine (IPV)\" schedule (in countries with high vaccination coverage [e.g. 90–95%] and low importation risk [where neighbouring countries and/or countries that share substantial population movement have a similarly high coverage])" 
        
  input = re.sub(r"\s+"," ",input)
  if len(input) > 245:
    # max filename size is 255, leave space for extensions such as .fsh
    logging.getLogger(__name__).info("ERROR: name of id is too long.hashing: " + input)        
    input = to_hash(input,245)
    logging.getLogger(__name__).info("Escaping code " + original + " to " + input )
  return input



      
def markdown_escape(input):
  if not isinstance(input,str):
    return " "
  input = input.replace('"""','\\"\\"\\"')
  return input

def ruleset_escape(input):
  # strings in rulesets are handled poorly
  input = input.replace(",","\\,")
  input = input.replace("'","")
  input = input.replace("(","")
  input = input.replace(")","")
  input = input.replace("\n","\\n")
  return input

def is_nan(v):
  return (isinstance(v, float) and v != v)

def is_blank(v):
  return v == None or is_nan(v) \
    or (isinstance(v, str) and len(v.strip()) == 0)

def is_dash(v):
  if not  isinstance(v,str):
    return False
  v = v.strip()
  return (v == '-' or v == '–')


def name_to_lower_id(name):
  if ( not (isinstance(name,str))):
    return None
  return name_to_id(name.lower())
  
def name_to_id(name):
  if ( not (isinstance(name,str))):
    return None
  id = re.sub('[^0-9a-zA-Z\\-\\.]+', '', name)
  # to work around jekyll error, make sure there are no trailing periods...
  id = id.rstrip('.')
  if len(id) > 55:
    # make length of an id is 64 characters
    #we need to make use of hashes
    logging.getLogger(__name__).info("ERROR: name of id is too long. hashing.: " + id)
    id = to_hash(id,55)
  return id



