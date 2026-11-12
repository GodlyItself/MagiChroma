from contextvars import ContextVar

from token_list import tokens, types


TOKEN_TEXT = {token_type: text for text, token_type in tokens.items()}
BINDING_POWER = {
    "OR": 10,
    "OR_OR": 10,
    "AND": 20,
    "AND_AND": 20,
    "LESS_THAN": 35,
    "GREATER_THAN": 35,
    "LESS_EQUAL": 35,
    "GREATER_EQUAL": 35,
    "EQUAL": 35,
    "NOT_EQUAL": 35,
    "STRICT_EQUAL": 35,
    "STRICT_NOT_EQUAL": 35,
    "PLUS": 40,
    "MINUS": 40,
    "MULTIPLY": 50,
    "DIVIDE": 50,
    "INTEGER_DIVIDE": 50,
    "MODULO": 50,
    "POWER": 60,
    "LPAREN": 80,
}

_parser_state = ContextVar("parser_state", default=None) 


def _state():
    state = _parser_state.get()
    if state is None:
        raise RuntimeError("Parser state is not initialized")
    return state


def node(node_type, **fields):
    return {"type": node_type, **fields}


def peek():
    state = _state()
    if state["cursor"] < len(state["tokens"]):
        return state["tokens"][state["cursor"]]
    return ""


def consume():
    state = _state()
    token = peek()
    if token:
        state["cursor"] += 1
    return token

def consume_if(token_type):
    if peek() == token_type:
        consume()
        return True
    return False

def expect(expected_type):
    token = peek()
    if token != expected_type:
        raise SyntaxError(
            f"Expected '{expected_type}', but found '{token}' "
            f"at position {_state()['cursor']}"
        )
    return consume()


def is_identifier(token):
    return token.isidentifier() and token not in tokens


def parse_statements():
    state = _state()
    body = []
    while True:
        token = peek()
        if state["terminators"] and token == state["terminators"][-1]:
            consume()
            return body
        if not token:
            if state["terminators"]:
                raise SyntaxError(
                    f"Unterminated block starting before position {state['cursor']}"
                )
            return body
        if token in ("EOL", "SEMICOLON"):
            consume()
            continue
        if token == "RBRACE":
            raise SyntaxError(f"Unexpected 'RBRACE' at position {state['cursor']}")
        statement = parse_statement()
        body.append(statement)


def parse_block(loop=False):
    state = _state()
    expect("LBRACE")
    state["terminators"].append("RBRACE")
    
    if loop:
        state["loop_depth"] = state.get("loop_depth", 0) + 1
        
    try:
        body = parse_statements()
    finally:
        state["terminators"].pop()
        if loop:
            state["loop_depth"] -= 1
            
    block = node("BlockStatement", body=body)
    return block

def parse_statement():
    match peek():
        case "LET" | "CONST":
            statement = parse_variable_declaration()
        case "IF":
            statement = parse_if_statement()
        case "LBRACE":
            statement = parse_block()
        case "FUNCTION":
            statement = parse_function_declaration()
        case "FOR":
            statement = parse_for_statement()
        case "WHILE":
            statement = parse_while_loop() 
        case "TRY" :
            statement = parse_try_catch()
        case "BREAK" :
            statement = parse_break_statement()
        case "MATCH":
            statement = parse_match_case()
        case "CASE":
            statement = SyntaxError("Cannot use CASE  outside of MATCH")
        case "CONTINUE":
            statement = parse_continue_statement()
        case "DO":
            statement = parse_do_statement()
        case "RETURN":
            statement = parse_return_statement()
        case _:
            statement = parse_expression_statement()

    while consume_if("SEMICOLON"):
        pass
    return statement

def parse_continue_statement():
    state = _state()
    if state.get("loop_depth", 0) == 0:
        raise SyntaxError("Cannot use CONTINUE outside of loop")
    consume()
    return node("ContinueStatement")

def parse_variable_declaration():
    kind = consume()
    name = consume()
    if not is_identifier(name):
        raise SyntaxError(
            f"Expected a variable name, but found '{name}' "
            f"at position {_state()['cursor'] - 1}"
        )

    annotation = None
    if peek() == "COLON":
        consume()
        annotation = consume()
        if annotation not in types:
            raise SyntaxError(f"Unknown variable type '{annotation}'")

    initializer = None
    if peek() == "ASSIGN":
        consume()
        initializer = parse_expression()

    identifier = node("Identifier", name=name)
    declaration = node(
        "VariableDeclaration",
        kind=TOKEN_TEXT[kind],
        id=identifier,
        annotation=annotation,
        init=initializer,
    )
    return declaration


def parse_if_statement():
    expect("IF")
    test = parse_expression(condition=True)
    consequent = parse_block()

    elif_branches = []
    while peek() == "ELIF":
        consume()
        elif_test = parse_expression()
        elif_body = parse_block()
        elif_branches.append((elif_test, elif_body))

    if peek() == "ELSE":
        consume()
        alternate = parse_block()
    else:
        alternate = None

    for elif_test, elif_body in reversed(elif_branches):
        alternate = node(
            "IfStatement",
            test=elif_test,
            consequent=elif_body,
            alternate=alternate,
        )

    statement = node(
        "IfStatement",
        test=test,
        consequent=consequent,
        alternate=alternate,
    )
    return statement


def parse_expression_statement():
    expression = parse_expression()
    if peek() == "ASSIGN":
        if expression["type"] != "Identifier":
            raise SyntaxError("Only variables can be assigned to")
        consume()
        value = parse_expression()
        statement = node(
            "AssignmentStatement",
            target=expression,
            value=value,
        )
        return statement
    statement = node("ExpressionStatement", expression=expression)
    return statement


def parse_function_declaration():
    expect("FUNCTION")
    name = consume()
    if not is_identifier(name):
        raise SyntaxError(
            f"Expected a function name, but found '{name}' "
            f"at position {_state()['cursor'] - 1}"
        )

    expect("LPAREN")
    parameters = []
    while peek() != "RPAREN":
        if not peek():
            raise SyntaxError(f"Unterminated parameter list for function '{name}'")
        parameter_name = consume()
        if not is_identifier(parameter_name):
            raise SyntaxError(
                f"Expected a parameter name, but found '{parameter_name}' "
                f"at position {_state()['cursor'] - 1}"
            )
        if any(
            parameter["id"]["name"] == parameter_name for parameter in parameters
        ):
            raise SyntaxError(
                f"Duplicate parameter '{parameter_name}' in function '{name}'"
            )

        annotation = None
        if peek() == "COLON":
            consume()
            annotation = consume()
            if annotation not in types:
                raise SyntaxError(f"Unknown parameter type '{annotation}'")

        identifier = node("Identifier", name=parameter_name)
        parameter = node(
            "Parameter",
            id=identifier,
            annotation=annotation,
        )
        parameters.append(parameter)
        if peek() != "RPAREN":
            expect("COMMA")

    consume()
    identifier = node("Identifier", name=name)
    body = parse_block()
    declaration = node(
        "FunctionDeclaration",
        id=identifier,
        params=parameters,
        body=body,
    )
    return declaration


def parse_for_statement(): 
    expect("FOR")
    test = parse_expression(condition=True)
    body = parse_block(loop=True)
    statement = node(
        "ForStatement",
        test=test,
        body=body,
    )
    return statement


def parse_while_loop():
    expect("WHILE")
    test = parse_expression(condition=True)
    body = parse_block(loop=True)
    statement = node(
        "WhileStatement",
        test=test,
        body=body, 
    )
    return statement

def parse_try_catch():
    expect("TRY")
    try_body = parse_block()
    catch_clauses = []

    while peek() == "CATCH":
        expect("CATCH")
        condition = None

        if peek() == "LPAREN":
            expect("LPAREN")
            condition = parse_expression(condition=False)
            expect("RPAREN")
        elif peek() != "LBRACE":
            condition = parse_expression(condition=False)

        body = parse_block()
        catch_clauses.append(
            node("CatchClause", condition=condition, body=body)
        )
    final_statement = []
    if peek() == "FINALLY":
        expect("FINALLY")
        final_statement = parse_block()

    if not catch_clauses:
        raise SyntaxError("Expected at least one 'catch' block after 'try'")

    return node(
        "TryStatement",
        try_body=try_body,
        catch_clauses=catch_clauses,
        final_statement=final_statement
    )

def parse_break_statement():
    expect("BREAK")
    return node(
        "BreakStatement"
    ) 

def parse_match_case():
    expect("MATCH")
    to_match = parse_expression()
    expect("LBRACE")
    
    cases = {}
    case_id = 0
    while peek() == "CASE":
        expect("CASE")
        case_expr = parse_expression() 
        case_block = parse_block()
        cases[case_id] = case_block
        print(f'cases are {cases}')

    default : bool = False
    if peek() == 'DEFAULT':
        default = True
        expect("DEFAULT")
        default_block = parse_block()
        expect("RBRACE")
        
    return node(
        "MatchCaseStatement",
        MatchExpression=to_match,
        Cases=cases,
        Default=default_block if default else None
    )

def parse_do_statement():
    expect("DO")
    body=parse_block()
    #expect("RPAREN")
    expect("WHILE")
    condition=parse_expression(condition=True)

    return node(
        "DoWhileStatement",
        body=body,
        condition=condition
    )

def parse_return_statement():
    expect("RETURN")
    return_statement = parse_expression()
    return node(
        "ReturnStatement",
        expression=return_statement
    )

def parse_expression(condition=False):
    state = _state()
    token = consume()

    if not token:
        raise SyntaxError(f"Expected an expression at position {state['cursor']}")

    if token == "NOT":
        state["binding_power_stack"].append(30)

        try:
            argument = parse_expression()
        finally:
            state["binding_power_stack"].pop()

        left = node(
            "UnaryExpression",
            operator="not",
            argument=argument,
        )

    elif token in ("PLUS", "MINUS"):
        state["binding_power_stack"].append(70)

        try:
            argument = parse_expression()
        finally:
            state["binding_power_stack"].pop()

        left = node(
            "UnaryExpression",
            operator=TOKEN_TEXT[token],
            argument=argument,
        )

    elif token == "LPAREN":
        state["binding_power_stack"].append(0)

        try:
            left = parse_expression()
        finally:
            state["binding_power_stack"].pop()

        expect("RPAREN")

    elif token.isdigit():
        left = node("NumericLiteral", value=int(token))

    elif token[:1] in ('"', "'") and token[-1:] == token[:1]:
        left = node("StringLiteral", value=token[1:-1])

    elif is_identifier(token):
        left = node("Identifier", name=token)

    else:
        raise SyntaxError(
            f"Unexpected token starting an expression: '{token}' "
            f"at position {state['cursor'] - 1}"
        )

    while state["binding_power_stack"][-1] < BINDING_POWER.get(peek(), 0):

        operator = consume()

        if operator == "LPAREN":
            arguments = []

            if peek() != "RPAREN":
                state["binding_power_stack"].append(0)

                try:
                    argument = parse_expression()
                    arguments.append(argument)
                    while peek() == "COMMA":
                        consume()
                        argument = parse_expression()
                        arguments.append(argument)
                finally:
                    state["binding_power_stack"].pop()

            expect("RPAREN")
            left = node("CallExpression", callee=left, arguments=arguments)
            continue

        binding_power = BINDING_POWER[operator]
        right_binding_power = binding_power - (operator == "POWER")
        state["binding_power_stack"].append(right_binding_power)

        try:
            right = parse_expression()
        finally:
            state["binding_power_stack"].pop()
            
        left = node(
            "BinaryExpression",
            operator=TOKEN_TEXT[operator],
            left=left,
            right=right,
        )

    if condition and left["type"] == "Identifier":
        left = node(
            "BinaryExpression",
            operator="==",
            left=left,
            right=node("BooleanLiteral", value=True),
        )

    return left


def parse(input_):
    state = {
        "tokens": input_,
        "cursor": 0,
        "binding_power_stack": [0],
        "terminators": [],
    }
    state_token = _parser_state.set(state)
    try:
        body = parse_statements()
        program = node("Program", body=body)
        return program
    finally:
        _parser_state.reset(state_token)
