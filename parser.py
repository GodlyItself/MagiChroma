from token_list import tokens, types


_TOKEN_TEXT = {token_type: text for text, token_type in tokens.items()}
_BINDING_POWER = {
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


def _node(node_type, **fields):
    return {"type": node_type, **fields}


def _peek(state):
    if state["cursor"] < len(state["tokens"]):
        return state["tokens"][state["cursor"]]
    return ""


def _consume(state, expected_type=None):
    token = _peek(state)
    if expected_type is not None and token != expected_type:
        raise SyntaxError(
            f"Expected '{expected_type}', but found '{token}' "
            f"at position {state['cursor']}"
        )
    if token:
        state["cursor"] += 1
    return token


def _is_identifier(token):
    return token.isidentifier() and token not in tokens


def _parse_statements(state, terminator=None):
    body = []
    while True:
        token = _peek(state)
        if terminator is not None and token == terminator:
            _consume(state, terminator)
            return body
        if not token:
            if terminator is not None:
                raise SyntaxError(
                    f"Unterminated block starting before position {state['cursor']}"
                )
            return body
        if token in ("EOL", "SEMICOLON"):
            _consume(state)
            continue
        if token == "RBRACE":
            raise SyntaxError(f"Unexpected 'RBRACE' at position {state['cursor']}")
        body.append(_parse_statement(state))


def _parse_block(state):
    _consume(state, "LBRACE")
    return _node("BlockStatement", body=_parse_statements(state, "RBRACE"))


def _parse_statement(state):
    match _peek(state):
        case "LET" | "CONST":
            return _parse_variable_declaration(state)
        case "IF":
            return _parse_if_statement(state)
        case "LBRACE":
            return _parse_block(state)
        case "FUNCTION":
            return _parse_function_declaration(state)
        case "FOR":
            return _parse_for_statement(state)
        case _:
            return _parse_expression_statement(state)


def _parse_variable_declaration(state):
    kind = _consume(state)
    name = _consume(state)
    if not _is_identifier(name):
        raise SyntaxError(
            f"Expected a variable name, but found '{name}' "
            f"at position {state['cursor'] - 1}"
        )

    annotation = None
    if _peek(state) == "COLON":
        _consume(state, "COLON")
        annotation = _consume(state)
        if annotation not in types:
            raise SyntaxError(f"Unknown variable type '{annotation}'")

    initializer = None
    if _peek(state) == "ASSIGN":
        _consume(state, "ASSIGN")
        initializer = _parse_expression(state)

    return _node(
        "VariableDeclaration",
        kind=_TOKEN_TEXT[kind],
        id=_node("Identifier", name=name),
        annotation=annotation,
        init=initializer,
    )


def _parse_if_statement(state):
    _consume(state, "IF")
    test = _parse_expression(state)
    consequent = _parse_block(state)

    elif_branches = []
    while _peek(state) == "ELIF":
        _consume(state, "ELIF")
        elif_branches.append(
            (_parse_expression(state), _parse_block(state))
        )

    if _peek(state) == "ELSE":
        _consume(state, "ELSE")
        alternate = _parse_block(state)
    else:
        alternate = None

    for elif_test, elif_body in reversed(elif_branches):
        alternate = _node(
            "IfStatement",
            test=elif_test,
            consequent=elif_body,
            alternate=alternate,
        )

    return _node(
        "IfStatement",
        test=test,
        consequent=consequent,
        alternate=alternate,
    )


def _parse_expression_statement(state):
    expression = _parse_expression(state)
    if _peek(state) == "ASSIGN":
        if expression["type"] != "Identifier":
            raise SyntaxError("Only variables can be assigned to")
        _consume(state, "ASSIGN")
        return _node(
            "AssignmentStatement",
            target=expression,
            value=_parse_expression(state),
        )
    return _node("ExpressionStatement", expression=expression)


def _parse_function_declaration(state):
    _consume(state, "FUNCTION")
    name = _consume(state)
    if not _is_identifier(name):
        raise SyntaxError(
            f"Expected a function name, but found '{name}' "
            f"at position {state['cursor'] - 1}"
        )

    _consume(state, "LPAREN")
    parameters = []
    while _peek(state) != "RPAREN":
        if not _peek(state):
            raise SyntaxError(f"Unterminated parameter list for function '{name}'")
        parameter_name = _consume(state)
        if not _is_identifier(parameter_name):
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
        if _peek(state) == "COLON":
            _consume(state, "COLON")
            annotation = _consume(state)
            if annotation not in types:
                raise SyntaxError(f"Unknown parameter type '{annotation}'")

        parameters.append(
            _node(
                "Parameter",
                id=_node("Identifier", name=parameter_name),
                annotation=annotation,
            )
        )
        if _peek(state) != "RPAREN":
            _consume(state, "COMMA")

    _consume(state, "RPAREN")
    return _node(
        "FunctionDeclaration",
        id=_node("Identifier", name=name),
        params=parameters,
        body=_parse_block(state),
    )


def _parse_for_statement(state):
    _consume(state, "FOR")
    return _node(
        "ForStatement",
        test=_parse_expression(state),
        body=_parse_block(state),
    )


def _parse_expression(state, minimum_binding_power=0):
    token = _consume(state)
    if not token:
        raise SyntaxError(f"Expected an expression at position {state['cursor']}")

    if token == "NOT":
        left = _node(
            "UnaryExpression",
            operator="not",
            argument=_parse_expression(state, 30),
        )
    elif token in ("PLUS", "MINUS"):
        left = _node(
            "UnaryExpression",
            operator=_TOKEN_TEXT[token],
            argument=_parse_expression(state, 70),
        )
    elif token == "LPAREN":
        left = _parse_expression(state)
        _consume(state, "RPAREN")
    elif token.isdigit():
        left = _node("NumericLiteral", value=int(token))
    elif token[:1] in ('"', "'") and token[-1:] == token[:1]:
        left = _node("StringLiteral", value=token[1:-1])
    elif _is_identifier(token):
        left = _node("Identifier", name=token)
    else:
        raise SyntaxError(
            f"Unexpected token starting an expression: '{token}' "
            f"at position {state['cursor'] - 1}"
        )

    while minimum_binding_power < _BINDING_POWER.get(_peek(state), 0):
        operator = _consume(state)
        if operator == "LPAREN":
            arguments = []
            if _peek(state) != "RPAREN":
                arguments.append(_parse_expression(state))
                while _peek(state) == "COMMA":
                    _consume(state, "COMMA")
                    arguments.append(_parse_expression(state))
            _consume(state, "RPAREN")
            left = _node("CallExpression", callee=left, arguments=arguments)
            continue

        binding_power = _BINDING_POWER[operator]
        right_binding_power = binding_power - (operator == "POWER")
        right = _parse_expression(state, right_binding_power)
        left = _node(
            "BinaryExpression",
            operator=_TOKEN_TEXT[operator],
            left=left,
            right=right,
        )

    return left


def parse(input_):
    state = {"tokens": input_, "cursor": 0}
    return _node("Program", body=_parse_statements(state))
