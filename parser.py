from typing import cast
from token_list import *

# Global variables tracking active parser execution
input_stream = []
cursor = 0
variables = []

def peek() -> str:
    """Look at the current token in the input stream without moving forward."""
    if cursor < len(input_stream):
        return input_stream[cursor]
    return ""

def consume(expected_type: str = None) -> str:
    """Advance the cursor and return the token. Option to validate it."""
    global cursor
    token = peek()
    if expected_type and token != expected_type:
        raise SyntaxError(f"Expected '{expected_type}', but found '{token}' at position {cursor}")
    if token != "":
        cursor += 1
    return token

def is_variable(token: str) -> bool:
    """Helper to check if a token is a valid variable name (and not a language keyword/operator)."""
    return token.isidentifier() and token not in tokens

def get_binding_power(token: str) -> int:
    """Maps operators to their precedence strengths. Numbers/Variables return 0."""
    binding_power = {
        'or': 10,
        'and': 20,
        '+': 40, '-': 40,
        '*': 50, '/': 50, '//': 50, '%': 50,
        '**': 60,
        '(': 80  # High priority to instantly bind function names to their arguments
    }
    return binding_power.get(token, 0)

def pratt_parse(current_bp: int = 0):
    """Parses expressions using Top-Down Operator Precedence."""
    global cursor

    token = consume()
    if token == 'not':
        left = ('Unary Operation', 'not', pratt_parse(30))
    elif token in ('+', '-'):
        left = ('Unary Operation', token, pratt_parse(70))
    elif token == '(':
        left = pratt_parse(0)
        consume(')')
    elif token.isdigit():
        left = ('Numerical Literal', int(token))
    elif is_variable(token):
        left = ('Variable', token)
    else:
        raise SyntaxError(f"Unexpected token starting an expression: '{token}' at position {cursor-1}") 

    while current_bp < get_binding_power(peek()):
        operator = consume()

        if operator == '(':
            args = []
            if peek() != ')':
                args.append(pratt_parse(0))
                while peek() == ',':
                    consume(',')  # Skip the comma token
                    args.append(pratt_parse(0))
            consume(')')
            left = ('Call', left, args)
        else:
            next_bp = get_binding_power(operator)
            if operator == '**':
                next_bp -= 1

            right = pratt_parse(next_bp)
            left = ('BinaryOp', operator, left, right)

    return left

def parse_variable_declaration(variables, classes, explicity=True, const=False):

    if explicity: #For python-like variable direct declarations
        if const:
            consume('CONST')
        else:
            consume ('LET')
    else:
        pass

    predefined = False
    var_name = consume() # Grab variable name
    type_ = None
    if peek() == ':':
        consume() #Consume for type dec
        type_ = peek()
        if type_ in types or type_ in classes:
            pass
        else:
            raise SyntaxError(f'{type_} is unknown.')

        if peek() == '=':
            consume('=')        # Enforce '='
            predefined = True
            value_expr = pratt_parse(0) 
        else:
            predefined = False
                    
    return   {
        'type': 'VariableDeclaration',
        'body': {
            'variable' : var_name,
            'mutability' : const,
            'type' : type_ if type_ in types or type_ in classes else 'any',
            'value' : value_expr if predefined else None
            }
        }

def parse():
    global input_stream, cursor
    ast = {'type': 'Program', 'body' : []}
    cached_line = []
    variables = []
    classes = []
    
    # Append a trailing 'EOF' to guarantee the final line in input_stream triggers processing
    for tk in input_stream + ['EOF']:
        if tk == 'EOL' or tk == 'EOF':
            if cached_line:
                orignal_stream = input_stream
                orignal_cursor = cursor

                input_stream = cached_line
                cursor = 0
                line_ast = []
                # LET STATEMENT
                match peek():
                    case 'LET':
                        line_ast = parse_variable_declaration(variables, classes)
                    case 'CONST':
                        line_ast = parse_variable_declaration(variables, classes, const=True)
                    case _:
                        # If it's a normal mathematical or logical calculation line, fallback to Pratt
                        line_ast = pratt_parse(0)

                ast['body'].append(line_ast)

                input_stream = orignal_stream
                cursor = orignal_cursor
                cached_line = []
        else:
            cached_line.append(tk)

    return ast

# Testing your layout
input_stream = ['CONST', 'X', '=', '2', '+', '5', '*', '4']
cursor = 0
print(parse())