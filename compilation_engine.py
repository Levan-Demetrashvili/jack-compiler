from variables import jack_compile_rules

index = 0

def compilation_engine(filepath,tokens):
  global index 
  index = 0
  with open(filepath,'w') as f:
    compile_class(f,tokens)
  return
    
def compile_class(f,tokens):
  f.write('<class>' + '\n')
  validate({'class'},tokens[index],f)
  validate({'identifier'}, tokens[index],f)
  validate({'{'}, tokens[index],f)
  while tokens[index][0] in jack_compile_rules["class_var_dec_keywords"]:
    compile_class_var_dec(f,tokens)
  while tokens[index][0] in jack_compile_rules["subroutines_dec_keywords"]:
    compile_subroutine_dec(f,tokens)
  validate({'}'}, tokens[index],f)
  f.write('</class>')
  return


def compile_class_var_dec(f,tokens):
  f.write(f'<classVarDec>\n')
  validate(jack_compile_rules["class_var_dec_keywords"], tokens[index],f)
  validate(jack_compile_rules["type"], tokens[index],f)
  validate({'identifier'}, tokens[index],f)
  while tokens[index][0]  == ',':
    validate({','}, tokens[index],f)
    validate({'identifier'}, tokens[index],f)
  validate({';'}, tokens[index],f)
  f.write(f'</classVarDec>\n')
  return

def compile_subroutine_dec(f,tokens):
  f.write(f'<subroutineDec>\n')
  validate(jack_compile_rules["subroutines_dec_keywords"], tokens[index],f)
  validate({'void',*jack_compile_rules["type"]}, tokens[index],f)
  validate({'identifier'}, tokens[index],f)
  validate({'('}, tokens[index],f)
  compile_parameter_list(f,tokens)
  validate({')'}, tokens[index],f)
  
  compile_subroutine_body(f,tokens)
  
  f.write(f'</subroutineDec>\n')

def compile_parameter_list(f,tokens):
  f.write(f'<parameterList>\n')
  if tokens[index][0] != ')':
    validate(jack_compile_rules["type"], tokens[index],f)
    validate({'identifier'}, tokens[index],f)
    while tokens[index][0]  == ',':
      validate({','}, tokens[index],f)
      validate(jack_compile_rules["type"], tokens[index],f)
      validate({'identifier'}, tokens[index],f)
    
  f.write(f'</parameterList>\n')

def compile_subroutine_body(f,tokens):
  f.write(f'<subroutineBody>\n')
  
  validate({'{'}, tokens[index],f)
  while tokens[index][0]  == 'var':
    compile_var_dec(f,tokens)
  
  compile_statements(f,tokens)
  validate({'}'}, tokens[index],f)
  
  f.write(f'</subroutineBody>\n')
 

def compile_var_dec(f,tokens):
  f.write(f'<varDec>\n')
  validate({'var'}, tokens[index],f)
  validate(jack_compile_rules["type"], tokens[index],f)
  validate({'identifier'}, tokens[index],f)
  while tokens[index][0]  == ',':  
    validate({','}, tokens[index],f)
    validate({'identifier'}, tokens[index],f)
  validate({';'}, tokens[index],f)
  f.write(f'</varDec>\n')
  
 
def compile_statements(f,tokens):
  f.write(f'<statements>\n')
  while tokens[index][0] in jack_compile_rules["statements_keywords"]:
    func_name = f"compile_{tokens[index][0]}"
    func = globals()[func_name] 
    func(f, tokens)
  f.write(f'</statements>\n')
  
  
def compile_let(f,tokens):
  f.write(f'<letStatement>\n')

  validate({'let'}, tokens[index],f)
  validate({'identifier'}, tokens[index],f)
  
  if tokens[index][0] == '[':
    validate({'['}, tokens[index],f)
    compile_expression(f,tokens)
    validate({']'}, tokens[index],f)
  
  validate({'='}, tokens[index],f)
  compile_expression(f,tokens)
  validate({';'}, tokens[index],f)
  
  f.write(f'</letStatement>\n')
  
def compile_if(f,tokens):
  f.write(f'<ifStatement>\n')

  validate({'if'}, tokens[index],f)
  validate({'('}, tokens[index],f)
  compile_expression(f,tokens)
  validate({')'}, tokens[index],f)
  
  validate({'{'}, tokens[index],f)
  compile_statements(f,tokens)
  validate({'}'}, tokens[index],f)
  
  if tokens[index][0] == 'else':
    validate({'else'}, tokens[index],f)
    validate({'{'}, tokens[index],f)
    compile_statements(f,tokens)
    validate({'}'}, tokens[index],f)
  
  f.write(f'</ifStatement>\n')

def compile_while(f,tokens):
  f.write(f'<whileStatement>\n')
  
  validate({'while'}, tokens[index],f)
  validate({'('}, tokens[index],f)
  compile_expression(f,tokens)
  validate({')'}, tokens[index],f)
  
  validate({'{'}, tokens[index],f)
  compile_statements(f,tokens)
  validate({'}'}, tokens[index],f)
    
  f.write(f'</whileStatement>\n')
  

def compile_do(f,tokens):
  f.write(f'<doStatement>\n')
  
  validate({'do'}, tokens[index],f)
  validate({'identifier'}, tokens[index],f)
  if tokens[index][0] == '.':
    validate({'.'}, tokens[index],f)
    validate({'identifier'}, tokens[index],f)
  
  validate({'('}, tokens[index],f)
  compile_expression_list(f,tokens)
  validate({')'}, tokens[index],f)
  validate({';'}, tokens[index],f)
    
  f.write(f'</doStatement>\n')

def compile_return(f,tokens):
  f.write(f'<returnStatement>\n')
  
  validate({'return'}, tokens[index],f)
  
  if tokens[index][0] != ';':
    compile_expression(f,tokens)
    
  validate({';'}, tokens[index],f)
  
  f.write(f'</returnStatement>\n')
  

def compile_expression(f,tokens):
  f.write(f'<expression>\n')
  compile_term(f,tokens)
  
  if tokens[index][0] in jack_compile_rules["op_symbols"]:
    validate(jack_compile_rules["op_symbols"], tokens[index],f)
    compile_term(f,tokens)
  
  f.write(f'</expression>\n')

def compile_term(f,tokens):
  f.write(f'<term>\n')
  previous_token = tokens[index][2]
  constants = {'stringConstant', 'integerConstant', '(' ,*jack_compile_rules["keyword_constants"],*jack_compile_rules["unary_op_symbols"]}  
  validate({'identifier', *constants}, tokens[index],f)
  if previous_token == '(':
    compile_expression(f,tokens)
    validate({')'}, tokens[index],f)
  elif previous_token == 'identifier':
    match tokens[index][2]:
      case '[':
        validate({'['}, tokens[index],f)
        compile_expression(f,tokens)
        validate({']'}, tokens[index],f)
      case '(':
        validate({'('}, tokens[index],f)
        compile_expression_list(f,tokens)
        validate({')'}, tokens[index],f)
      case '.':
        validate({'.'}, tokens[index],f)
        validate({'identifier'}, tokens[index],f)
        validate({'('}, tokens[index],f)
        compile_expression_list(f,tokens)
        validate({')'}, tokens[index],f)
  elif previous_token in jack_compile_rules["unary_op_symbols"]:  
    compile_term(f,tokens)
  f.write(f'</term>\n')

def compile_expression_list(f,tokens):
  f.write(f'<expressionList>\n')
  
  if tokens[index][0] != ')':
    compile_expression(f,tokens)
    while tokens[index][0] == ',':
      validate({','}, tokens[index],f)
      compile_expression(f,tokens)
    
  f.write(f'</expressionList>\n')
  

def validate(valid_values,current_token,f):
  global index 
  t,type_,check_value = current_token
  if check_value in valid_values:
    f.write(f"<{type_}> {t} </{type_}>\n")
    index += 1
    return
  else:
    raise SyntaxError(f"current token doesn't match {valid_values}")