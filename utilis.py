import re
def unescape_html(s):
    return re.sub(r'&(lt|gt|amp);', lambda m: {
        'lt': '<',
        'gt': '>',
        'amp': '&'
    }[m.group(1)], s)

    
def split_subroutine_call(exp):
    i = exp.find('(')
    if i == -1:
        return exp.strip(), ''
    
    subroutine_name = exp[:i].strip()
    depth = 1
    j = i + 1
    while j < len(exp) and depth > 0:
        if exp[j] == '(':
            depth += 1
        elif exp[j] == ')':
            depth -= 1
        j += 1
    
    args = exp[i+1:j-1].strip()  # remove the outer parentheses
    return subroutine_name, args.split(',') if args.split(',')[0] != "" else []
  
def is_function_call(s):
    return re.match(r'^[a-zA-Z_]\w*(\.[a-zA-Z_]\w*)?\s*\(.*\)$', s) is not None
  
def remove_parenthesis(str):
  if str[0] == '(' and str[-1] == ')':
    return str[1:-1]
  else:
    return str 


def lookup_symbol(sub_table,class_table,variable):
    # Try subroutine first
    if sub_table.kind_of(variable) is not None:
        return {
            'kind': sub_table.kind_of(variable),
            'index': sub_table.index_of(variable),
            'type': sub_table.type_of(variable)
        }
    # Then class-level
    if class_table.kind_of(variable) is not None:
        return {
            'kind': class_table.kind_of(variable),
            'index': class_table.index_of(variable),
            'type': class_table.type_of(variable)
        }
    return None

def split_expression(exp):
    exp = exp.strip()

    # Remove unnecessary outer parentheses
    while exp.startswith('(') and exp.endswith(')'):
        depth = 0
        valid = True
        for i, c in enumerate(exp):
            if c == '(': depth += 1
            elif c == ')': depth -= 1
            if depth == 0 and i != len(exp) - 1:
                valid = False
                break
        if valid:
            exp = exp[1:-1].strip()
        else:
            break

    # Operators in increasing precedence (last is lowest)
    ops = ['|', '&', '=',  '<', '>',  '+', '-', '*', '/']

    for op in ops:
        i = 0
        depth = 0
        while i < len(exp):
            if exp[i] == '(':
                depth += 1
            elif exp[i] == ')':
                depth -= 1
            elif depth == 0:
                if exp[i] == op:
                    left = exp[:i].strip()
                    right = exp[i+1:].strip()
                    return [left, op, right]
            i += 1

    return [exp]
  
  
def split_array_expression(exp):
  ops = {'|', '&', '=',  '<', '>',  '+', '-', '*', '/'}
  i = 0
  depth = 0
  
  while i < len(exp):
    if exp[i] == '[':
        depth += 1
    elif exp[i] == ']':
        depth -= 1
    elif depth == 0:
        if exp[i] in  ops:
            left = exp[:i].strip()
            right = exp[i+1:].strip()
            return [left, exp[i], right]
    i += 1
  return [exp]

def remove_outer_brackets(s):
  depth = 0
  result = ""
  for char in s:
    if depth:
      result += char
    if char == '[':
      depth += 1
    elif char == ']':
      depth -= 1
    if depth == 0 and result:
      return result[:-1]
  return s
      
    
def is_bracket_expression(s):
    if not s:
        return False

    i = s.find('[')
    if i == -1 or not s.endswith(']'):
        return False

    identifier = s[:i]
    if not identifier.isidentifier():
        return False

    depth = 0
    for j, c in enumerate(s[i:], start=i):
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return j == len(s) - 1  # outermost ] must be at the end
        if depth < 0:
            return False

    return depth == 0

def is_array_expression(expr):
  depth_paren = 0
  i = 0
  while i < len(expr):
    c = expr[i]
    if c == '(':
      depth_paren += 1
    elif c == ')':
      depth_paren -= 1
    elif c == '[' and depth_paren == 0:
      return True
    i += 1
  return False