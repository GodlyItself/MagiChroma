from typing import cast
from token_list import *
from pretty_print import pretty_print as pprint

_token_values = {token_type: value for value, token_type in tokens.items()}

# Global variables tracking active parser execution
input_stream = []
cursor = 0
variables = []

def peek() -> str:
    """Look at the current token in the input stream without moving forward."""
    if cursor < len(input_stream):
        token = input_stream[cursor]
        return _token_values.get(token, token)
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
        '<': 35, '>': 35, '<=': 35, '>=': 35,
        '==': 35, '!=': 35, '===': 35, '!==': 35,
        '+': 40, '-': 40,
        '*': 50, '/': 50, '//': 50, '%': 50,
        '**': 60,
        '(': 80  # High priority to instantly bind function names to their arguments
    }
    return binding_power.get(token, 0)

def is_f_string(token):
    return token.startswith('f"') or token.startswith("f'")

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
    elif is_f_string(token):
        left = parse_if_statement()
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
            left = ("Call", left, args)
        else:
            next_bp = get_binding_power(operator)
            if operator == '**':
                next_bp -= 1

            right = pratt_parse(next_bp)
            left = ("BinaryOp", operator, left, right)

    return left

def parse_variable_declaration(classes, explicity=True, const=False): #takes classes for type checking.

    if explicity: #For python-like variable direct declarations
        if const:
            consume('CONST' if peek() == 'CONST' else 'const')
        else:
            consume('LET' if peek() == 'LET' else 'let')
    else:
        pass

    predefined = False
    var_name = consume() # Grab variable name
    type_ = None

    if peek() == ':':
        consume() #Consume for type dec
        type_ = consume()

        if type_ in types or type_ in classes:
            pass
        else:
            raise SyntaxError(f'{type_} is unknown.')

    if peek() == '=':
        consume('=')
        predefined = True
        value_expr = pratt_parse(0)
                    
    return   {
        "type": "VariableDeclaration",
        "body": {
            "variable": var_name,
            "mutability": const,
            "type": type_ if type_ in types or type_ in classes else "any",
            "value": value_expr if predefined else None
            }
        }

def parse_block(classes=None):
    opening = peek()
    if opening != '{':
        raise SyntaxError(f"Expected 'LBRACE', but found '{peek()}' at position {cursor}")
    consume(opening)

    terminator = '}'
    program = parse(terminator=terminator, classes=classes)
    return {"type": "CodeBlock", "body": program["body"]}

def parse_if_statement(classes=None):
    consume('IF' if peek() == 'IF' else 'if')
    condition = pratt_parse()
    body = parse_block(classes)
    return {
        "type": "IfStatement",
        "condition": condition,
        "body": body
    }

def parse_variable_mutation():
    var_name = peek()
    consume() #registered and ate variable name

    consume() #ate '='

    val = pratt_parse()

    return {
        "type" : "VariableMutation",
        "name" : var_name,
        "value" : val
    }

def parse_function_declaration():
    consume() #consume what declares the function.
    arguments = {}
    func_name = peek()
    consume()
    consume('(')
    current_param = None

    while peek() != '(':
        if peek() == ',':
            consume()
        elif peek() == ':':
            consume()
            if current_param:
                arguments[current_param] = peek()
            consume()
        else:
            current_param = peek()
            arguments[current_param] = None
            consume

    consume(')')
    body = parse_block()
    return {
        "type" : "FunctionDeclaration",
        "name" : func_name,
        "arguments" : arguments, # Returning the full dict gives you names AND types
        "body" : body
    }


def parse_statement(classes):
    match peek():
        case 'LET' | 'let':
            return parse_variable_declaration(classes)
        case 'CONST' | 'const':
            return parse_variable_declaration(classes, const=True)
        case 'IF' | 'if':
            return parse_if_statement(classes)
        case 'LBRACE' | '{':
            return parse_block(classes)
        case 'FUNCTION' | 'function':
            return parse_function_declaration()
        case _:
            return parse_variable_mutation()

def parse(terminator=None, classes=None):
    global input_stream, cursor
    classes = [] if classes is None else classes
    body = []

    while True:
        token = peek()
        if token == terminator and terminator is not None:
            consume(terminator)
            break
        if token == '':
            if terminator is not None:
                raise SyntaxError(f"Unterminated block starting before position {cursor}")
            break
        if token in ('RBRACE', '}'):
            raise SyntaxError(f"Unexpected 'RBRACE' at position {cursor}")
        if token in ('EOL', ';'):
            consume()
            continue

        body.append(parse_statement(classes))

    return {"type": "Program", "body": body}

input_stream = ['FUNCTION', 'ABC', 'LPAREN', 'HI', 'COMMA', 'BYE','RPAREN', 'LBRACE', 'LET', 'X', '=', '9', 'RBRACE']
cursor = 0
pprint(parse())