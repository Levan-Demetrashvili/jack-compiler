jack_lexical_elements = {
    "keywords": {
        "class", "constructor", "function", "method",
        "field", "static", "var",
        "int", "char", "boolean", "void",
        "true", "false", "null", "this",
        "let", "do", "if", "else", "while", "return"
    },
    "symbols": {
        "{", "}", "(", ")", "[", "]", ".", ",", ";",
        "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"
    },
}

jack_compile_rules = {
  "type": {'int','boolean','char','identifier'},
  "class_var_dec_keywords" : {'field', 'static'},
  "subroutines_dec_keywords" : {'constructor', 'function', 'method'},
  "statements_keywords" : {"if", "while", "do", "let", "return"},
  "op_symbols": {'+' , '-' , '*' , '/' , '&amp;',  '|',  '&lt;', '&gt;', '=' },
  "unary_op_symbols": {'~' , '-' },
  "keyword_constants": {"true", "false", "null", "this"}
}