from variables import jack_compile_rules
from symbol_table import SymbolTable

index = None
f = None
tokens = []
class_table = SymbolTable()
subroutine_table = SymbolTable()

def compilation_engine(filepath,tokens_stream):
  global index,tokens,f
  index = 0
  class_table.start_subroutine()
  with open(filepath,'w') as file:
    f = file
    tokens = tokens_stream
    compile_class()  
  return
    
def compile_class():
  f.write('<class>' + '\n')
  validate({'class'})
  validate({'identifier'})
  validate({'{'})
  while tokens[index][0] in jack_compile_rules["class_var_dec_keywords"]:
    compile_class_var_dec()
  while tokens[index][0] in jack_compile_rules["subroutines_dec_keywords"]:
    compile_subroutine_dec()
  validate({'}'})
  f.write('</class>')
  return


def compile_class_var_dec():
  f.write(f'<classVarDec>\n')
  validate(jack_compile_rules["class_var_dec_keywords"])
  validate(jack_compile_rules["type"])
  validate({'identifier'})
  kind,type_,name = get_variable_info()
  class_table.define(name,type_,kind) 
  
  while tokens[index][0]  == ',':
    validate({','})
    validate({'identifier'})
    class_table.define(tokens[index - 1][0],type_,kind) 
  
  validate({';'})
  f.write(f'</classVarDec>\n')
  return


def compile_subroutine_dec():
  f.write(f'<subroutineDec>\n')
  subroutine_table.start_subroutine()
  validate(jack_compile_rules["subroutines_dec_keywords"])
  validate({'void',*jack_compile_rules["type"]})
  validate({'identifier'})
  validate({'('})
  compile_parameter_list()
  validate({')'})
  
  compile_subroutine_body()
  
  f.write(f'</subroutineDec>\n')
  

def compile_parameter_list():
  f.write(f'<parameterList>\n')
  if tokens[index][0] != ')':
    validate(jack_compile_rules["type"])
    validate({'identifier'})
    _,type_,name = get_variable_info()
    subroutine_table.define(name,type_,'argument')
    while tokens[index][0]  == ',':
      validate({','})
      validate(jack_compile_rules["type"])
      validate({'identifier'})
      _,type_,name = get_variable_info()
      subroutine_table.define(name,type_,'argument')
      
  
  f.write(f'</parameterList>\n')

def compile_subroutine_body():
  f.write(f'<subroutineBody>\n')
  
  validate({'{'})
  while tokens[index][0]  == 'var':
    compile_var_dec()
  
  compile_statements()
  validate({'}'})
  
  f.write(f'</subroutineBody>\n')
 

def compile_var_dec():
  f.write(f'<varDec>\n')
  validate({'var'})
  validate(jack_compile_rules["type"])
  validate({'identifier'})
  _,type_,name = get_variable_info()
  subroutine_table.define(name,type_,'local')
  while tokens[index][0]  == ',':  
    validate({','})
    validate({'identifier'})
    subroutine_table.define(tokens[index - 1][0],type_,'local')
  validate({';'})
  f.write(f'</varDec>\n')
  
 
def compile_statements():
  f.write(f'<statements>\n')
  while tokens[index][0] in jack_compile_rules["statements_keywords"]:
    func_name = f"compile_{tokens[index][0]}"
    func = globals()[func_name] 
    func()
  f.write(f'</statements>\n')
  
  
def compile_let():
  f.write(f'<letStatement>\n')

  validate({'let'})
  validate({'identifier'})
  
  if tokens[index][0] == '[':
    validate({'['})
    compile_expression()
    validate({']'})
  
  validate({'='})
  compile_expression()
  validate({';'})
  
  f.write(f'</letStatement>\n')
  
def compile_if():
  f.write(f'<ifStatement>\n')

  validate({'if'})
  validate({'('})
  compile_expression()
  validate({')'})
  
  validate({'{'})
  compile_statements()
  validate({'}'})
  
  if tokens[index][0] == 'else':
    validate({'else'})
    validate({'{'})
    compile_statements()
    validate({'}'})
  
  f.write(f'</ifStatement>\n')

def compile_while():
  f.write(f'<whileStatement>\n')
  
  validate({'while'})
  validate({'('})
  compile_expression()
  validate({')'})
  
  validate({'{'})
  compile_statements()
  validate({'}'})
    
  f.write(f'</whileStatement>\n')
  

def compile_do():
  f.write(f'<doStatement>\n')
  
  validate({'do'})
  validate({'identifier'})
  if tokens[index][0] == '.':
    validate({'.'})
    validate({'identifier'})
  
  validate({'('})
  compile_expression_list()
  validate({')'})
  validate({';'})
    
  f.write(f'</doStatement>\n')

def compile_return():
  f.write(f'<returnStatement>\n')
  
  validate({'return'})
  
  if tokens[index][0] != ';':
    compile_expression()
    
  validate({';'})
  
  f.write(f'</returnStatement>\n')
  

def compile_expression():
  f.write(f'<expression>\n')
  compile_term()
  
  if tokens[index][0] in jack_compile_rules["op_symbols"]:
    validate(jack_compile_rules["op_symbols"])
    compile_term()
  
  f.write(f'</expression>\n')

def compile_term():
  f.write(f'<term>\n')
  previous_token = tokens[index][2]
  constants = {'stringConstant', 'integerConstant', '(' ,*jack_compile_rules["keyword_constants"],*jack_compile_rules["unary_op_symbols"]}  
  validate({'identifier', *constants})
  if previous_token == '(':
    compile_expression()
    validate({')'})
  elif previous_token == 'identifier':
    match tokens[index][2]:
      case '[':
        validate({'['})
        compile_expression()
        validate({']'})
      case '(':
        validate({'('})
        compile_expression_list()
        validate({')'})
      case '.':
        validate({'.'})
        validate({'identifier'})
        validate({'('})
        compile_expression_list()
        validate({')'})
  elif previous_token in jack_compile_rules["unary_op_symbols"]:  
    compile_term()
  f.write(f'</term>\n')

def compile_expression_list():
  f.write(f'<expressionList>\n')
  
  if tokens[index][0] != ')':
    compile_expression()
    while tokens[index][0] == ',':
      validate({','})
      compile_expression()
    
  f.write(f'</expressionList>\n')
  

def validate(valid_values):
  global index 
  t,type_,check_value = tokens[index]
  if check_value in valid_values:
    f.write(f"<{type_}> {t} </{type_}>\n")
    index += 1
    return
  else:
    raise SyntaxError(f"current token doesn't match {valid_values}")
  

def get_variable_info():
  return tokens[index - 3][0], tokens[index - 2][0],tokens[index - 1][0]