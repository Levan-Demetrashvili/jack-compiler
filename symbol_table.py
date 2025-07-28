class SymbolTable:
  def __init__(self):
    self.table = {}
    self.kind_index  = 0
    self.previous_var_kind = None
  def start_subroutine(self):
    self.table = {}
    self.kind_index  = 0
    self.previous_var_kind = None
    
  def define(self, name, type_, kind):
    # index
    self.var_count(kind)
    self.previous_var_kind = kind
    
    self.table[name] = {
        "name": name,
        "type": type_,
        "kind": 'this' if kind == 'field' else kind,
        "index": self.kind_index
    }
  
  def kind_of(self,name):
    try:
      return self.table[name]["kind"] 
    except Exception:
      return None
  def type_of(self,name):
    try:
      return self.table[name]["type"] 
    except Exception:
      return None
    
  def index_of(self,name):
    try:
      return self.table[name]["index"] 
    except Exception:
      return None
  
  
  def var_count(self,kind):
    if kind == self.previous_var_kind:
      self.kind_index += 1
    else:
      self.kind_index = 0
          
