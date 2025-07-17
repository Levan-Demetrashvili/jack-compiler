import sys
import os
from jack_tokenizer import jack_tokenizer

def main():
  tokenized = {}
  #* Handling tokenizing
  if os.path.isfile(sys.argv[1]):
    program_name = sys.argv[1].split('/')[-1].split('.')[0]
    tokenized[program_name] = jack_tokenizer(sys.argv[1],program_name)
  else:
    for file in os.listdir(sys.argv[1])[::-1]:
      if file.endswith('.jack'):
        filepath = os.path.join(sys.argv[1],file)
        file_stem = file.split('.')[0]
        tokenized[file_stem] = jack_tokenizer(filepath,file_stem)

if __name__ == "__main__":
  main()