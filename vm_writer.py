class VMWriter:
  def __init__(self,file_path):
    with open(file_path,'w') as file:
      self.f = file
  def write_push(self,segment,index):
    self.f.write(f"push {segment} {index}\n")
  def write_pop(self,segment,index):
    self.f.write(f"pop {segment} {index}\n")
  def write_arithmetic(self,command):
    self.f.write(f"{command}\n")
  def write_label(self,label):
    self.f.write(f"label {label}\n")
  def write_goto(self,label):
    self.f.write(f"goto {label}\n")
  def write_if(self,label):
    self.f.write(f"if-goto {label}\n")
  def write_call(self,name,nArgs):
    self.f.write(f"call {name} {nArgs}\n")
  def write_function(self,name,nLocals):
    self.f.write(f"function {name} {nLocals}\n")
  def write_return(self):
    self.f.write(f"return\n")
    