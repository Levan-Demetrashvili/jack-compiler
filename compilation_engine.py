import re
from variables import jack_compile_rules,jack_to_vm_op,jack_to_vm_unary
from symbol_table import SymbolTable
from vm_writer import VMWriter
import utilis

index = None
f = None
tokens = []
class_name = None
class_table = SymbolTable()
subroutine_table = SymbolTable()
vm_writer = None
expression = []

def compilation_engine(filepath,tokens_stream):
  global index,tokens,vm_writer
  index = 0
  class_table.start_subroutine()
  tokens = tokens_stream
  vm_writer = VMWriter(filepath)
  compile_class()
  return
    
def compile_class():
  global class_name
  validate({'class'})
  validate({'identifier'})
  class_name = tokens[index - 1][0]
  validate({'{'})
  while tokens[index][0] in jack_compile_rules["class_var_dec_keywords"]:
    compile_class_var_dec()
  while tokens[index][0] in jack_compile_rules["subroutines_dec_keywords"]:
    compile_subroutine_dec()
  validate({'}'})
  return


def compile_class_var_dec():
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


def compile_subroutine_dec():
  subroutine_table.start_subroutine()
  validate(jack_compile_rules["subroutines_dec_keywords"])
  validate({'void',*jack_compile_rules["type"]})
  validate({'identifier'})
  function_name = tokens[index - 1][0]
  validate({'('})
  compile_parameter_list()
  validate({')'})
  
  compile_subroutine_body(function_name)
  
  

def compile_parameter_list():
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
      
  

def compile_subroutine_body(function_name):
  n_locals = 0
  validate({'{'})
  while tokens[index][0]  == 'var':
    n_locals += 1
    n_locals = compile_var_dec(n_locals)
  vm_writer.write_function(f"{class_name}.{function_name}",n_locals)
  compile_statements()
  validate({'}'})
  
 

def compile_var_dec(n_locals):
  validate({'var'})
  validate(jack_compile_rules["type"])
  validate({'identifier'})
  _,type_,name = get_variable_info()
  subroutine_table.define(name,type_,'local')
  while tokens[index][0]  == ',':  
    validate({','})
    validate({'identifier'})
    subroutine_table.define(tokens[index - 1][0],type_,'local')
    n_locals += 1
    
  validate({';'})
  return n_locals
  
 
def compile_statements():
  while tokens[index][0] in jack_compile_rules["statements_keywords"]:
    func_name = f"compile_{tokens[index][0]}"
    func = globals()[func_name] 
    func()
  
  
def compile_let():

  validate({'let'})
  validate({'identifier'})
  variable_name = tokens[index - 1][0]
  if tokens[index][0] == '[':
    validate({'['})
    compile_expression()
    code_write("".join(expression))
    clear_expression()
    validate({']'})
  
  validate({'='})
  compile_expression()
  
  code_write("".join(expression))
  clear_expression()
  
  variable = utilis.lookup_symbol(subroutine_table,class_table,variable_name)
  vm_writer.write_pop(variable["kind"],variable["index"])
  
  validate({';'})
  
  
def compile_if():

  validate({'if'})
  validate({'('})
  compile_expression()
  code_write("".join(expression))
  clear_expression()
  validate({')'})
  
  vm_writer.write_arithmetic('not')
  vm_writer.write_if('L1')
  
  validate({'{'})
  compile_statements()
  validate({'}'})
  
  vm_writer.write_goto('L2')
  
  
  if tokens[index][0] == 'else':
    validate({'else'})
    validate({'{'})
    vm_writer.write_label('L1')
    compile_statements()
    validate({'}'})
  
  vm_writer.write_label('L2')
  
  
  

def compile_while():
  
  validate({'while'})
  validate({'('})
  
  compile_expression()
  code_write("".join(expression))
  clear_expression()
  
  validate({')'})
  
  validate({'{'})
  compile_statements()
  validate({'}'})
    
  

def compile_do():
  
  validate({'do'})
  validate({'identifier'})
  expression.append(tokens[index - 1][0])
  if tokens[index][0] == '.':
    validate({'.'})
    expression.append(tokens[index - 1][0])
    validate({'identifier'})
    expression.append(tokens[index - 1][0])
    
  
  validate({'('})
  expression.append(tokens[index - 1][0])
  compile_expression_list()
  validate({')'})
  expression.append(tokens[index - 1][0])
  code_write("".join(expression))
  clear_expression()

  
  vm_writer.write_pop('temp',0)
  validate({';'})
    

def compile_return():
  
  validate({'return'})
  
  if tokens[index][0] != ';':
    compile_expression()
    code_write("".join(expression))
    clear_expression()
  else:
    vm_writer.write_push('constant',0)
    
  vm_writer.write_return()
  validate({';'})
  
  

def compile_expression():
  compile_term()
  
  if tokens[index][0] in jack_compile_rules["op_symbols"]:
    validate(jack_compile_rules["op_symbols"])
    expression.append(tokens[index - 1][0])
    compile_term()
  

def compile_term():
  previous_token = tokens[index][2]
  constants = {'stringConstant', 'integerConstant', '(' ,*jack_compile_rules["keyword_constants"],*jack_compile_rules["unary_op_symbols"]}  
  validate({'identifier', *constants})
  expression.append(tokens[index - 1][0])
  if previous_token == '(':
    compile_expression()
    validate({')'})
    expression.append(tokens[index - 1][0])
    
  elif previous_token == 'identifier':
    match tokens[index][2]:
      case '[':
        validate({'['})
        expression.append(tokens[index - 1][0])
        compile_expression()
        validate({']'})
        expression.append(tokens[index - 1][0])
        
      case '(':
        validate({'('})
        expression.append(tokens[index - 1][0])
        compile_expression_list()
        validate({')'})
        expression.append(tokens[index - 1][0])
      case '.':
        validate({'.'})
        expression.append(tokens[index - 1][0])
        validate({'identifier'})
        expression.append(tokens[index - 1][0])
        validate({'('})
        expression.append(tokens[index - 1][0])
        compile_expression_list()
        validate({')'})
        expression.append(tokens[index - 1][0])
        
  elif previous_token in jack_compile_rules["unary_op_symbols"]:  
    compile_term()

def compile_expression_list():
  
  if tokens[index][0] != ')':
    compile_expression()
    while tokens[index][0] == ',':
      validate({','})
      expression.append(tokens[index - 1][0])
      compile_expression()
  
  

def validate(valid_values):
  global index 
  t,type_,check_value = tokens[index]
  if check_value in valid_values:
    index += 1
    return
  else:
    raise SyntaxError(f"current token doesn't match {valid_values}")
  

def code_write(exp):
  exp = utilis.unescape_html(exp)
  pattern = r'\s*(\+|\-|\*|\/|&|\||<|>|=)\s*'
  exp_op_exp = [s for s in re.split(pattern,  exp,maxsplit=1) if s.strip()] 
  op_exp = [s.strip() for s in re.split(r'(-|~)', exp, maxsplit=1) if s.strip()]
  
  # If expression is boolean value translate to appropriate number
  if exp == 'true':
    exp = '-1'
  elif exp in ('false','null'):
    exp = '0'
    
  
  # Determine what is expression
  if exp.isdigit():
    vm_writer.write_push('constant',exp)
  elif exp in subroutine_table.table:
    vm_writer.write_push(subroutine_table.kind_of(exp),subroutine_table.index_of(exp))
  elif exp in class_table.table:
    vm_writer.write_push(class_table.kind_of(exp) ,class_table.index_of(exp))
  elif len(exp_op_exp) == 3 and  not utilis.is_function_call(exp):
    code_write(utilis.remove_parenthesis(exp_op_exp[0]))
    code_write(utilis.remove_parenthesis(exp_op_exp[2]))
    vm_writer.write_arithmetic(jack_to_vm_op[exp_op_exp[1]])
  elif len(op_exp) == 2:
    code_write(op_exp[1])
    vm_writer.write_arithmetic(jack_to_vm_unary[op_exp[0]])
  elif utilis.is_function_call(exp):
    sub_name, args = utilis.split_subroutine_call(exp)
    for arg in args:
      code_write(arg)
    print(f"name:{sub_name or None}\n args:{args} \n expression:{exp} \n ----")
    vm_writer.write_call(sub_name,len(args))
    

def get_variable_info():
  return tokens[index - 3][0], tokens[index - 2][0],tokens[index - 1][0]

def clear_expression():
  global expression
  expression = []
  return
