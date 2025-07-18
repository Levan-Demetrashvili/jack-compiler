import sys
import os
from jack_tokenizer import jack_tokenizer
from compilation_engine import compilation_engine

def main():
  tokenized = {}
  if os.path.isfile(sys.argv[1]):
    program_name = sys.argv[1].split('/')[-1].split('.')[0]
    #* Handling tokenizing
    tokenized[program_name] = jack_tokenizer(sys.argv[1],program_name)
    #* compilation engine
    for _,tokens_array in tokenized.items():
      compilation_engine(sys.argv[1].replace('jack','xml'),tokens_array)
  else:
    for file in os.listdir(sys.argv[1])[::-1]:
      if file.endswith('.jack'):
        #* Handling tokenizing
        filepath = os.path.join(sys.argv[1],file)
        file_stem = file.split('.')[0]
        tokenized[file_stem] = jack_tokenizer(filepath,file_stem)
  
    #* compilation engine
    for class_name,tokens_array in tokenized.items():
      compilation_engine(f"{sys.argv[1]}/{class_name}.xml",tokens_array)
  
  
if __name__ == "__main__":
  main()