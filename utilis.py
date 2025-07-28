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
    return subroutine_name, args.split(',')
  
def is_function_call(s):
    return re.match(r'^[a-zA-Z_]\w*(\.[a-zA-Z_]\w*)?\s*\(.*\)$', s) is not None
  
def remove_parenthesis(str):
  return str.replace('(', '').replace(')', '')


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