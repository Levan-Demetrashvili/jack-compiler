import re
from trimmer import trimmer
from variables import jack_lexical_elements

def jack_tokenizer(filepath,file_stem):
  result = []
  # Read all source code lines and split it into VALID tokens
  with open(filepath, "r") as f:
    multi_line_comment = False
    # pattern to split line into tokens
    tokens = []
    tokens_pattern = r'"[^"\n]*"|[\w]+|[\{\}\(\)\[\]\.\,\;\+\-\*\/&\|\<\>\=\~]'
    for line in f:
      # remove comments and whitespaces
      trimmed_line,multi_line_comment = trimmer(line,multi_line_comment)
      if not trimmed_line:
        continue
      # make tokens
      tokens = [*tokens,*re.findall(tokens_pattern,trimmed_line)]
    # determine tokens type
    for token in tokens:
     result.append(token_type(token))
  # write output into xml file
  with open(filepath.replace('.jack','T.xml'),'w') as f:
    f.write('<tokens>' + '\n')
    for token,type_,_ in result:
      f.write(f"<{type_}> {token} </{type_}>\n")    
    f.write('</tokens>')
  return result
    

def token_type(token):
  t_type = None 
  t = token
  check_value = token
  if token in jack_lexical_elements["keywords"]:
    t_type = 'keyword'
  elif token in jack_lexical_elements["symbols"]:
    t_type = 'symbol'
    match token:
      case '<':
        t = '&lt;'
        
      case '>':
        t = '&gt;'
      case '&':
        t = '&amp;'
    
    check_value = t
        
  elif token.startswith('"'):
    t_type = 'stringConstant'
    check_value = 'stringConstant'
    t = "".join(token.split('"'))
  elif token[0].isdigit():
    t_type = 'integerConstant'
    check_value = 'integerConstant'
  else:
    t_type = 'identifier'
    check_value = 'identifier'
    
  return t,t_type,check_value

    