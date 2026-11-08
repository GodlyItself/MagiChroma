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


def node(node_type, **fields):
    return {"type": node_type, **fields}


def peek(state):
    if state["cursor"] < len(state["tokens"]):
        return state["tokens"][state["cursor"]]
    return ""


def consume(state, expected_type=None):
    token = peek(state)
    if expected_type is not None and token != expected_type:
        raise SyntaxError(
            f"Expected '{expected_type}', but found '{token}' "
            f"at position {state['cursor']}"
        )
    if token:
        state["cursor"] += 1
    return token


def is_identifier(token):
    return token.isidentifier() and token not in tokens


def parse_statements(state, terminator=None):
    body = []
    while True:
        token = peek(state)
        if terminator is not None and token == terminator:
            consume(state, terminator)
            return body
        if not token:
            if terminator is not None:
                raise SyntaxError(
                    f"Unterminated block starting before position {state['cursor']}"
                )
            return body
        if token in ("EOL", "SEMICOLON"):
            consume(state)
            continue
        if token == "RBRACE":
            raise SyntaxError(f"Unexpected 'RBRACE' at position {state['cursor']}")
        body.append(parse_statement(state))


def parse_block(state):
    consume(state, "LBRACE")
    return node("BlockStatement", body=parse_statements(state, "RBRACE"))


def parse_statement(state):
    match peek(state):
        case "LET" | "CONST":
            return parse_variable_declaration(state)
        case "IF":
            return parse_if_statement(state)
        case "LBRACE":
            return parse_block(state)
        case "FUNCTION":
            return parse_function_declaration(state)
        case "FOR":
            return parse_for_statement(state)
        case _:
            return parse_expression_statement(state)


def parse_variable_declaration(state):
    kind = consume(state)
    name = consume(state)
    if not is_identifier(name):
        raise SyntaxError(
            f"Expected a variable name, but found '{name}' "
            f"at position {state['cursor'] - 1}"
        )

    annotation = None
    if peek(state) == "COLON":
        consume(state, "COLON")
        annotation = consume(state)
        if annotation not in types:
            raise SyntaxError(f"Unknown variable type '{annotation}'")

    initializer = None
    if peek(state) == "ASSIGN":
        consume(state, "ASSIGN")
        initializer = parse_expression(state)

    return  node(
        "VariableDeclaration",
        kind= TOKEN_TEXT[kind],
        id= node("Identifier", name=name),
        annotation=annotation,
        init=initializer,
    )


def parse_if_statement(state):
    consume(state, "IF")
    test = parse_expression(state)
    consequent = parse_block(state)

    elif_branches = []
    while peek(state) == "ELIF":
        consume(state, "ELIF")
        elif_branches.append(
            (parse_expression(state), parse_block(state))
        )

    if peek(state) == "ELSE":
        consume(state, "ELSE")
        alternate = parse_block(state)
    else:
        alternate = None

    for elif_test, elif_body in reversed(elif_branches):
        alternate = node(
            "IfStatement",
            test=elif_test,
            consequent=elif_body,
            alternate=alternate,
        )

    return node(
        "IfStatement",
        test=test,
        consequent=consequent,
        alternate=alternate,
    )


def parse_expression_statement(state):
    expression = parse_expression(state)
    if peek(state) == "ASSIGN":
        if expression["type"] != "Identifier":
            raise SyntaxError("Only variables can be assigned to")
        consume(state, "ASSIGN")
        return node(
            "AssignmentStatement",
            target=expression,
            value=parse_expression(state),
        )
    return node("ExpressionStatement", expression=expression)


def parse_function_declaration(state):
    consume(state, "FUNCTION")
    name = consume(state)
    if not  is_identifier(name):
        raise SyntaxError(
            f"Expected a function name, but found '{name}' "
            f"at position {state['cursor'] - 1}"
        )

    consume(state, "LPAREN")
    parameters = []
    while  peek(state) != "RPAREN":
        if not  peek(state):
            raise SyntaxError(f"Unterminated parameter list for function '{name}'")
        parameter_name =  consume(state)
        if not  is_identifier(parameter_name):
            raise SyntaxError(
                f"Expected a parameter name, but found '{parameter_name}' "
                f"at position {state['cursor'] - 1}"
            )
        if any(
            parameter["id"]["name"] == parameter_name for parameter in parameters
        ):
            raise SyntaxError(
                f"Duplicate parameter '{parameter_name}' in function '{name}'"
            )

        annotation = None
        if peek(state) == "COLON":
            consume(state, "COLON")
            annotation = consume(state)
            if annotation not in types:
                raise SyntaxError(f"Unknown parameter type '{annotation}'")

        parameters.append(
            node(
                "Parameter",
                id=node("Identifier", name=parameter_name),
                annotation=annotation,
            )
        )
        if peek(state) != "RPAREN":
            consume(state, "COMMA")

    consume(state, "RPAREN")
    return node(
        "FunctionDeclaration",
        id= node("Identifier", name=name),
        params= parameters,
        body= parse_block(state),
    )


def parse_for_statement(state):
    consume(state, "FOR")
    return node(
        "ForStatement",
        test=parse_expression(state),
        body= parse_block(state),
    )


def parse_expression(state, minimum_binding_power=0):
    token = consume(state)
    if not token:
        raise SyntaxError(f"Expected an expression at position {state['cursor']}")

    if token == "NOT":
        left = node(
            "UnaryExpression",
            operator="not",
            argument= parse_expression(state, 30),
        )
    elif token in ("PLUS", "MINUS"):
        left = node(
            "UnaryExpression",
            operator= TOKEN_TEXT[token],
            argument= parse_expression(state, 70),
        )
    elif token == "LPAREN":
        left = parse_expression(state)
        consume(state, "RPAREN")
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

    while minimum_binding_power < BINDING_POWER.get(peek(state), 0):
        operator = consume(state)
        if operator == "LPAREN":
            arguments = []
            if peek(state) != "RPAREN":
                arguments.append(parse_expression(state))
                while peek(state) == "COMMA":
                    consume(state, "COMMA")
                    arguments.append(parse_expression(state))
            consume(state, "RPAREN")
            left = node("CallExpression", callee=left, arguments=arguments)
            continue

        binding_power = BINDING_POWER[operator]
        right_binding_power = binding_power - (operator == "POWER")
        right = parse_expression(state, right_binding_power)
        left = node(
            "BinaryExpression",
            operator= TOKEN_TEXT[operator],
            left=left,
            right=right,
        )

    return left


def parse(input_):
    state = {"tokens": input_, "cursor": 0}
    return node("Program", body=parse_statements(state))
