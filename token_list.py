tokens = {
    # --- 1. Keywords & Reserved Words ---
    'break': 'BREAK', #done
    'case': 'CASE', #done
    'catch': 'CATCH',#done
    'const': 'CONST',#done
    'continue': 'CONTINUE', #done
    'debugger': 'DEBUGGER', #idk if i'll include it. skipping for now.
    'default': 'DEFAULT', #done
    #'delete': 'DELETE',
    'do': 'DO', #done
    'else': 'ELSE', #done
    'elif': 'ELIF', #done
    #'export': 'EXPORT',
    #'extends': 'EXTENDS',
    'finally': 'FINALLY',
    'for': 'FOR',
    'function': 'FUNCTION', #done partial
    'if': 'IF', #done
    'import': 'IMPORT',
    'in': 'IN',
    'instanceof': 'INSTANCEOF',
    'new': 'NEW',
    'return': 'RETURN',
    'super': 'SUPER',
    'match': 'MATCH', 
    'this': 'THIS',
    'throw': 'THROW',
    'try': 'TRY',
    'typeof': 'TYPEOF',
    'var': 'VAR',
    'void': 'VOID',
    'while': 'WHILE', #done
    'with': 'WITH',
    'yield': 'YIELD',
    'enum': 'ENUM',
    'await': 'AWAIT',

    # --- 2. Strict Mode & Future Reserved Words ---
    'implements': 'IMPLEMENTS',
    'interface': 'INTERFACE',
    'let': 'LET', #done
    'package': 'PACKAGE',
    'private': 'PRIVATE',
    'protected': 'PROTECTED',
    'public': 'PUBLIC',
    'static': 'STATIC',

    # --- 3. Python-Specific Logical Keywords --- #done
    'not': 'NOT',
    'or': 'OR',
    'and': 'AND',

    # --- 4. Structural Delimiters ---
    '{': 'LBRACE',
    '}': 'RBRACE',
    '(': 'LPAREN',
    ')': 'RPAREN',
    '[': 'LBRACK',
    ']': 'RBRACK',
    '.': 'DOT', #left due to classes
    ',': 'COMMA',
    ';': 'SEMICOLON',

    # --- 5. Arithmetic & Update Operators --- #done
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'MULTIPLY',
    '/': 'DIVIDE',
    '//': 'INTEGER_DIVIDE',
    '**':'POWER',
    '%': 'MODULO',
    '++': 'INCREMENT',
    '--': 'DECREMENT',

    # --- 6. Relational & Comparison Operators --- #done
    '<': 'LESS_THAN',
    '>': 'GREATER_THAN',
    '<=': 'LESS_EQUAL',
    '>=': 'GREATER_EQUAL',
    '==': 'EQUAL',
    '!=': 'NOT_EQUAL',
    '===': 'STRICT_EQUAL',
    '!==': 'STRICT_NOT_EQUAL',

    # --- 7. Logical & Bitwise Operators --- #?
    '&': 'AMPERSAND',
    '|': 'PIPE',
    '^': 'CARET',
    '!': 'BANG',
    '~': 'TILDE',
    '&&': 'AND_AND',
    '||': 'OR_OR',
    '?': 'QUESTION',
    ':': 'COLON',

    # --- 8. Assignment Operators --- #done
    '=': 'ASSIGN',
    '+=': 'PLUS_ASSIGN',
    '-=': 'MINUS_ASSIGN',
    '*=': 'MULTIPLY_ASSIGN',
    '/=': 'DIVIDE_ASSIGN',
    '%=': 'MODULO_ASSIGN',
    '<<=': 'LSHIFT_ASSIGN',
    '>>=': 'RSHIFT_ASSIGN',
    '>>>=': 'URSHIFT_ASSIGN',
    '&=': 'AND_ASSIGN',
    '^=': 'XOR_ASSIGN',
    '|=': 'OR_ASSIGN',
    '**=': 'EXP_ASSIGN',

    # --- 9. Special Arrow Operators ---
    '=>': 'ARROW',

    #--- 10. Strings ---
    '`' : 'TOGGLE_F_STRING',
    '"': 'DOUBLE_QUOTE',
    "'": 'SINGLE_QUOTE',
}

keywords = {
    'break': 'BREAK',
    'case': 'CASE',
    'catch': 'CATCH',
    'const': 'CONST',
    'continue': 'CONTINUE',
    'debugger': 'DEBUGGER',
    'default': 'DEFAULT',
    'delete': 'DELETE',
    'do': 'DO',
    'else': 'ELSE',
    'elif' : "ELIF",
    'export': 'EXPORT',
    'extends': 'EXTENDS',
    'finally': 'FINALLY',
    'for': 'FOR',
    'function': 'FUNCTION',
    'if': 'IF',
    'import': 'IMPORT',
    'in': 'IN',
    'instanceof': 'INSTANCEOF',
    'new': 'NEW',
    'return': 'RETURN',
    'super': 'SUPER',
    'switch': 'SWITCH',
    'this': 'THIS',
    'throw': 'THROW',
    'try': 'TRY',
    'typeof': 'TYPEOF',
    'var': 'VAR',
    'void': 'VOID',
    'while': 'WHILE',
    'with': 'WITH',
    'yield': 'YIELD',
    'enum': 'ENUM',
    'await': 'AWAIT',
}

reserved = {
    'implements': 'IMPLEMENTS',
    'interface': 'INTERFACE',
    'let': 'LET',
    'package': 'PACKAGE',
    'private': 'PRIVATE',
    'protected': 'PROTECTED',
    'public': 'PUBLIC',
    'static': 'STATIC',
}

logic_words = {
    'not': 'NOT',
    'or': 'OR',
    'and': 'AND',
}

delimiters = {
    '{': 'LBRACE',
    '}': 'RBRACE',
    '(': 'LPAREN',
    ')': 'RPAREN',
    '[': 'LBRACK',
    ']': 'RBRACK',
    '.': 'DOT',
    ',': 'COMMA',
    ';': 'SEMICOLON',
}

arithmetic = {
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'MULTIPLY',
    '/': 'DIVIDE',
    '%': 'MODULO',
    '++': 'INCREMENT',
    '--': 'DECREMENT',
}

comparisons = {
    '<': 'LESS_THAN',
    '>': 'GREATER_THAN',
    '<=': 'LESS_EQUAL',
    '>=': 'GREATER_EQUAL',
    '==': 'EQUAL',
    '!=': 'NOT_EQUAL',
    '===': 'STRICT_EQUAL',
    '!==': 'STRICT_NOT_EQUAL',
}

logic_bitwise = {
    '&': 'AMPERSAND',
    '|': 'PIPE',
    '^': 'CARET',
    '!': 'BANG',
    '~': 'TILDE',
    '&&': 'AND_AND',
    '||': 'OR_OR',
    '?': 'QUESTION',
    ':': 'COLON',
}

assignments = {
    '=': 'ASSIGN',
    '+=': 'PLUS_ASSIGN',
    '-=': 'MINUS_ASSIGN',
    '*=': 'MULTIPLY_ASSIGN',
    '/=': 'DIVIDE_ASSIGN',
    '%=': 'MODULO_ASSIGN',
    '<<=': 'LSHIFT_ASSIGN',
    '>>=': 'RSHIFT_ASSIGN',
    '>>>=': 'URSHIFT_ASSIGN',
    '&=': 'AND_ASSIGN',
    '^=': 'XOR_ASSIGN',
    '|=': 'OR_ASSIGN',
    '**=': 'EXP_ASSIGN',
}

arrows = {
    '=>': 'ARROW',
}

conditionals = {
    '<': 'LESS_THAN',
    '>': 'GREATER_THAN',
    '<=': 'LESS_EQUAL',
    '>=': 'GREATER_EQUAL',
    '==': 'EQUAL',
    '!=': 'NOT_EQUAL',
    '===': 'STRICT_EQUAL',
    '!==': 'STRICT_NOT_EQUAL',
}

types = {
    'string' : 'STRING',
    'int' : 'INTEGER',
}