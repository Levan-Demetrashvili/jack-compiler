def trimmer(line,multi_line_comment):
      trimmedLine = line.strip()
      #* Parse the line
      if "*/" in trimmedLine:
        trimmedLine = trimmedLine.split('/*')[0].strip() if "/*" in trimmedLine else ''
        multi_line_comment = False
      elif multi_line_comment:
        trimmedLine = ''
      elif "//" in trimmedLine:
        trimmedLine = trimmedLine.split('//')[0].strip()
      elif "/*" in trimmedLine:
        multi_line_comment = True
        trimmedLine = trimmedLine.split('/*')[0].strip()
      
      return trimmedLine,multi_line_comment