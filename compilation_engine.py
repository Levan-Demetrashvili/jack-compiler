import re
from variables import jack_compile_rules,jack_to_vm_op,jack_to_vm_unary
from symbol_table import SymbolTable
from vm_writer import VMWriter
import utilis

index = None
tokens = []
class_name = None
class_table = SymbolTable()
subroutine_table = SymbolTable()
vm_writer = None
expression = []
labels_index = 0


def compilation_engine(filepath,tokens_stream):
  global index,tokens,vm_writer,labels_index
  index = 0
  labels_index = 0
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
  is_constructor = tokens[index][0] == 'constructor' 
  is_method = tokens[index][0] == 'method'
  
  validate(jack_compile_rules["subroutines_dec_keywords"])
  validate({'void',*jack_compile_rules["type"]})
  validate({'identifier'})
  
  
  function_name = tokens[index - 1][0]
  validate({'('})
  
  compile_parameter_list(is_method)
  validate({')'})
  
  compile_subroutine_body(function_name,is_constructor,is_method)
  
  

def compile_parameter_list(is_method):
  if tokens[index][0] != ')':
    validate(jack_compile_rules["type"])
    validate({'identifier'})
    _,type_,name = get_variable_info()
    if is_method:
      subroutine_table.define(name,type_,'argument') 
    subroutine_table.define(name,type_,'argument')
    while tokens[index][0]  == ',':
      validate({','})
      validate(jack_compile_rules["type"])
      validate({'identifier'})
      _,type_,name = get_variable_info()
      subroutine_table.define(name,type_,'argument')
      
  

def compile_subroutine_body(function_name,is_constructor,is_method):
  n_locals = 0
  validate({'{'})
  while tokens[index][0]  == 'var':
    n_locals += 1
    n_locals = compile_var_dec(n_locals)
  vm_writer.write_function(f"{class_name}.{function_name}",n_locals)
  
  #* constructor
  if (is_constructor):
    size = 0
    for varialbe in class_table.table.values():
      if varialbe["kind"] == 'this':
        size += 1
    vm_writer.write_push('constant',size)
    vm_writer.write_call('Memory.alloc',1)
    vm_writer.write_pop('pointer',0)
  
  #* method
  if (is_method):
    vm_writer.write_push('argument',0)
    vm_writer.write_pop('pointer',0)
  
  
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
  
  variable = utilis.lookup_symbol(subroutine_table,class_table,variable_name)
  
  is_array_item = False
  
  if tokens[index][0] == '[':
    is_array_item = True
    validate({'['})
    compile_expression()
    code_write("".join(expression))
    vm_writer.write_push(variable["kind"],variable["index"])
    vm_writer.write_arithmetic('add')
    clear_expression()
    validate({']'})
    
  
  validate({'='})
  compile_expression()
  
  code_write("".join(expression))
  if is_array_item:
    vm_writer.write_pop('temp',0)
    vm_writer.write_pop('pointer',1)
    vm_writer.write_push('temp',0)
    vm_writer.write_pop('that',0)
  else:
    vm_writer.write_pop(variable["kind"],variable["index"])
 
  clear_expression()
  
  validate({';'})
  
  

def compile_if():
  global labels_index
  validate({'if'})
  validate({'('})
  compile_expression()
  code_write("".join(expression))
  clear_expression()
  validate({')'})
  
  vm_writer.write_arithmetic('not')
  
  labels_index += 2
  if_index,end_index = labels_index - 1,labels_index - 2
  vm_writer.write_if(f"{class_name}_{if_index}")
  
  validate({'{'})
  compile_statements()
  validate({'}'})
  
  vm_writer.write_goto(f"{class_name}_{end_index}")
  
  vm_writer.write_label(f"{class_name}_{if_index}")
  if tokens[index][0] == 'else':
    validate({'else'})
    validate({'{'})
    compile_statements()
    validate({'}'})
  
  vm_writer.write_label(f"{class_name}_{end_index}")
  

def compile_while():
  global labels_index
  validate({'while'})
  validate({'('})
  
  labels_index += 2
  loop_index,stop_index = labels_index - 2,labels_index - 1
  
  vm_writer.write_label(f"{class_name}_{loop_index}")
  
  compile_expression()
  code_write("".join(expression))
  clear_expression()
  
  validate({')'})
  
  vm_writer.write_arithmetic('not')
  vm_writer.write_if(f"{class_name}_{stop_index}")
  
  validate({'{'})
  compile_statements()
  validate({'}'})
  
  vm_writer.write_goto(f"{class_name}_{loop_index}")
  
  vm_writer.write_label(f"{class_name}_{stop_index}")
      

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
  expression.append(tokens[index - 1][0] if previous_token != 'stringConstant' else f'"{tokens[index-1][0]}"')
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
        #print(expression)
        
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
  _,_,check_value = tokens[index]
  if check_value in valid_values:
    index += 1
    return
  else:
    raise SyntaxError(f"current token doesn't match {valid_values}")
  

def code_write(exp,flag=None):
  exp = utilis.unescape_html(exp)
  # If expression is boolean value translate to appropriate number
  if exp == 'true':
    exp = '-1'
    
  elif exp in ('false','null'):
    exp = '0'
    
  exp_op_exp = utilis.split_expression(exp)
  op_exp = [s.strip() for s in re.split(r'(-|~)', exp, maxsplit=1) if s.strip()]
  
  if exp.isdigit():
    vm_writer.write_push('constant',exp)
  elif exp == 'this':
    vm_writer.write_push('pointer',0)
  elif exp in subroutine_table.table:
    vm_writer.write_push(subroutine_table.kind_of(exp),subroutine_table.index_of(exp))
    if subroutine_table.type_of(exp) == 'Array' and flag =='arr_item':
      vm_writer.write_arithmetic('add')
      vm_writer.write_pop('pointer',1)
      vm_writer.write_push('that',0)
      
  elif exp in class_table.table:
    vm_writer.write_push(class_table.kind_of(exp) ,class_table.index_of(exp))
    if class_table.type_of(exp) == 'Array' and flag =='arr_item':
      vm_writer.write_arithmetic('add')
      vm_writer.write_pop('pointer',1)
      vm_writer.write_push('that',0)
  elif len(exp_op_exp) == 3 and  not utilis.is_function_call(exp) and exp_op_exp[0] and not utilis.is_bracket_expression(exp):
    if utilis.is_array_expression(exp):
      exp_op_exp = utilis.split_array_expression(exp)
      
    code_write(utilis.remove_parenthesis(exp_op_exp[0]))
    code_write(utilis.remove_parenthesis(exp_op_exp[2]))
    vm_writer.write_arithmetic(jack_to_vm_op[exp_op_exp[1]])

  elif len(op_exp) == 2:
    code_write(op_exp[1])
    vm_writer.write_arithmetic(jack_to_vm_unary[op_exp[0]])
  
  elif utilis.is_function_call(exp):
    sub_name, args = utilis.split_subroutine_call(exp)
    
    if subroutine_table.kind_of(sub_name.split('.')[0]) or class_table.kind_of(sub_name.split('.')[0])  :
      args.insert(0,sub_name.split('.')[0])
      callee_class = subroutine_table.type_of(sub_name.split('.')[0]) if subroutine_table.type_of(sub_name.split('.')[0]) else class_table.type_of(sub_name.split('.')[0])
      sub_name = f"{callee_class}.{sub_name.split('.')[1]}"
      
    elif '.' not in sub_name:
      args.insert(0,'this')
      
    for arg in args:
      code_write(arg)
      
    #print(f"name:{sub_name or None}\n args:{args} \n expression:{exp} \n ----")
    if '.' not in sub_name:
      vm_writer.write_call(f"{class_name}.{sub_name}",len(args))
    else: 
      vm_writer.write_call(sub_name,len(args))
  elif '[' in exp:
    address_exp = utilis.remove_outer_brackets(exp)
    arr_name = exp.split('[',maxsplit=1)[0]
    code_write(address_exp)
    code_write(arr_name,'arr_item')
  elif exp.startswith('"'):
    string = exp[1:-1] #* trim '"'
    vm_writer.write_push('constant',len(string))
    vm_writer.write_call('String.new',1)
    for c in string:
      vm_writer.write_push('constant',ord(c))
      vm_writer.write_call('String.appendChar',2)



def get_variable_info():
  return tokens[index - 3][0], tokens[index - 2][0],tokens[index - 1][0]

def clear_expression():
  global expression
  expression = []
  return
