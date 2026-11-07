from typing import cast
from token_list import *
from pretty_print import pretty_print as pprint
import sys

_token_values = {token_type: value for value, token_type in tokens.items()}

# Global variables tracking active parser execution
input_stream = []
cursor = 0
variables = []

def set_input_stream(input_stream_):
    input_stream = input_stream_

def peek() -> str:
    """Look at the current token in the input stream without moving forward."""
    if cursor < len(input_stream):
        token = input_stream[cursor]
        return token
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
        'OR': 10,
        'AND': 20,
        'LESS_THAN': 35, 'GREATER_THAN': 35, 'LESS_EQUAL': 35, 'GREATER_EQUAL': 35,
        'EQUAL': 35, 'NOT_EQUAL': 35, 'STRICT_EQUAL': 35, 'STRICT_NOT_EQUAL': 35,
        'PLUS': 40, 'MINUS': 40,
        'MULTIPLY': 50, 'DIVIDE': 50, 'INTEGER_DIVIDE': 50, 'MODULO': 50,
        'POWER': 60,
        'LPAREN': 80  # High priority to instantly bind function names to their arguments
    }
    return binding_power.get(token, 0)

def is_f_string(token):
    return token.startswith('f"') or token.startswith("f'")

def pratt_parse(current_bp: int = 0):
    """Parses expressions using Top-Down Operator Precedence."""
    global cursor

    token = consume()

    if token == 'NOT':
        left = ('Unary Operation', 'not', pratt_parse(30))
    elif token in ['PLUS', 'MINUS']:
        left = ['Unary Operation', token, pratt_parse(70)]
    elif token == 'LPAREN':
        left = pratt_parse(0)
        consume() #Consume RPAREN
    elif token.isdigit():
        left = ['Numerical Literal', int(token)]
    elif is_variable(token):
        left = ['Variable', token]
    elif is_f_string(token):
        left = parse_if_statement()
    else:
        raise SyntaxError(f"Unexpected token starting an expression: '{token}' at position {cursor-1}") 

    while current_bp < get_binding_power(peek()):
        if peek() in comparisons.values():
            break
        
        operator = consume()

        if operator == 'LPAREN':
            args = []
            if peek() != 'RPAREN':
                args.append(pratt_parse(0))
                while peek() == 'COMMA':
                    consume('COMMA')  # Skip the comma token
                    args.append(pratt_parse(0))
            consume('RPAREN') 
            left = ["Call", left, args]
        else:
            next_bp = get_binding_power(operator)
            if operator == 'POWER':
                next_bp -= 1

            right = pratt_parse(next_bp)
            left = ["BinaryOp", operator, left, right]

    return left

def parse_conditional():
    left_hand_side = pratt_parse()
    consume()
    right_hand_side = pratt_parse()
    return {
        "type" : "ConditionalExpression",
        "body": {
            "left" : left_hand_side,
            "right" : right_hand_side,
        }
    }

def parse_variable_declaration(classes, explicity=True, const=False): #takes classes for type checking.

    if explicity: #For python-like variable direct declarations
        if const:
            consume()
        else:
            consume()
    else:
        pass

    predefined = False
    var_name = consume() # Grab variable name
    type_ = None

    if peek() == 'COLON':
        consume() #Consume for type dec
        type_ = consume()

        if type_ in types or type_ in classes:
            pass
        else:
            raise SyntaxError(f'{type_} is unknown.')

    if peek() == 'ASSIGN':
        consume('ASSIGN')
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
    if opening != 'LBRACE':
        raise SyntaxError(f"Expected 'LBRACE', but found '{peek()}' at position {cursor}")
    consume(opening)

    terminator = 'RBRACE'
    program = parse(terminator=terminator, classes=classes)
    return {"type": "CodeBlock", "body": program["body"]}

def parse_if_statement(classes=None):
    consume('IF')
    condition = parse_conditional() ##Fixed this.
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

def parse_function_declaration(classes=None):
    consume('FUNCTION')

    func_name = consume()
    if not is_variable(func_name):
        raise SyntaxError(f"Expected a function name, but found '{func_name}' at position {cursor - 1}")

    consume('LPAREN')
    arguments = {}

    while peek() != 'RPAREN':
        if peek() == '': # I lowkey don't remember why I did this but changing/removing it would take time/break stuff so I'll leave it.
            raise SyntaxError(f"Unterminated parameter list for function '{func_name}'")

        param_name = consume()
        if not is_variable(param_name):
            raise SyntaxError(f"Expected a parameter name, but found '{param_name}' at position {cursor - 1}")
        if param_name in arguments:
            raise SyntaxError(f"Duplicate parameter '{param_name}' in function '{func_name}'")

        param_type = None
        if peek() == 'COLON':
            consume('COLON')
            param_type = consume()
            if param_type not in types and param_type not in (classes or []):
                raise SyntaxError(f"Unknown parameter type '{param_type}'")

        arguments[param_name] = param_type

        if peek() != 'RPAREN':
            consume('COMMA')

    consume('RPAREN')
    body = parse_block(classes)

    return {
        "type": "FunctionDeclaration",
        "name": func_name,
        "arguments": arguments,
        "body": body
    }

def parse_for_loop():
    consume('FOR')

    condition = parse_conditional()
    stuff = parse_block()

    return {
        "type" : "ForLoop",
        "condition" : condition,
        "body" : stuff
    }

def parse_statement(classes):
    match peek():
        case 'LET':
            return parse_variable_declaration(classes)
        case 'CONST':
            return parse_variable_declaration(classes, const=True)
        case 'IF':
            return parse_if_statement(classes)
        case 'LBRACE':
            return parse_block(classes)
        case 'FUNCTION':
            return parse_function_declaration() 
        case 'FOR':
            return parse_for_loop()
        case _:
            return parse_variable_mutation()

def parse(input_=None, terminator=None, classes=None):
    global input_stream, cursor
    if input_stream == []:
        input_stream = input_
    else:
        pass

    classes = [] if classes is None else classes
    body = []

    while True:
        token = peek()
        if token == terminator and terminator is not None:
            consume(terminator)
            break
        if token == '': #Again, Empty String for Who knows what but works. i needa write more of comments
            if terminator is not None:
                raise SyntaxError(f"Unterminated block starting before position {cursor}")
            break
        if token in ('RBRACE'):
            raise SyntaxError(f"Unexpected 'RBRACE' at position {cursor}")
        if token in ('EOL', 'SEMICOLON'):
            consume()
            continue

        body.append(parse_statement(classes))

    return {"type": "Program", "body": body}

#input_stream = ['FUNCTION', 'ABC', 'LPAREN', 'HI', 'COMMA', 'BYE','RPAREN', 'LBRACE', 'LET', 'X', '=', '9', 'RBRACE']
#cursor = 0
#pprint(parse())
