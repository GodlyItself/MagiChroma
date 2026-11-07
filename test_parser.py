import unittest

import lexer
import parser


def parse_source(source):
    return parser.parse(lexer.lexer(source))


class ParserAstTests(unittest.TestCase):
    def assert_typed_nodes(self, value):
        if isinstance(value, dict):
            self.assertIn("type", value)
            for child in value.values():
                self.assert_typed_nodes(child)
        elif isinstance(value, list):
            for child in value:
                self.assert_typed_nodes(child)

    def test_declarations_and_expressions_use_typed_nodes(self):
        program = parse_source('let total: int = 1 + 2 * 3; const title = "hello"')

        self.assert_typed_nodes(program)
        self.assertEqual(program["type"], "Program")
        declaration, constant = program["body"]
        self.assertEqual(declaration["type"], "VariableDeclaration")
        self.assertEqual(declaration["kind"], "let")
        self.assertEqual(declaration["id"], {"type": "Identifier", "name": "total"})
        self.assertEqual(declaration["annotation"], "int")
        expression = declaration["init"]
        self.assertEqual(expression["type"], "BinaryExpression")
        self.assertEqual(expression["operator"], "+")
        self.assertEqual(expression["right"]["operator"], "*")
        self.assertEqual(constant["kind"], "const")
        self.assertEqual(constant["init"], {"type": "StringLiteral", "value": "hello"})

    def test_if_ast_nests_any_number_of_elif_branches(self):
        program = parse_source(
            "if x == 0 { x = 1 } "
            "elif x == 1 { x = 2 } "
            "elif x == 2 { x = 3 } "
            "elif x == 3 { x = 4 } "
            "else { x = 5 }"
        )

        self.assert_typed_nodes(program)
        branch = program["body"][0]
        self.assertEqual(branch["type"], "IfStatement")
        self.assertEqual(branch["test"]["operator"], "==")
        for expected in (1, 2, 3):
            alternate = branch["alternate"]
            self.assertEqual(alternate["type"], "IfStatement")
            self.assertEqual(alternate["consequent"]["body"][0]["value"]["value"], expected + 1)
            branch = alternate
        self.assertEqual(branch["alternate"]["type"], "BlockStatement")
        self.assertEqual(branch["alternate"]["body"][0]["value"]["value"], 5)

    def test_functions_loops_calls_and_assignments_have_consistent_nodes(self):
        program = parse_source(
            "function run(x: int) { log(x) } "
            "for x < 3 and not y == 0 { x = x + 1 }"
        )

        self.assert_typed_nodes(program)
        function, loop = program["body"]
        self.assertEqual(function["type"], "FunctionDeclaration")
        self.assertEqual(function["params"][0]["type"], "Parameter")
        self.assertEqual(function["params"][0]["id"]["name"], "x")
        call = function["body"]["body"][0]["expression"]
        self.assertEqual(call["type"], "CallExpression")
        self.assertEqual(call["arguments"][0]["type"], "Identifier")
        self.assertEqual(loop["type"], "ForStatement")
        self.assertEqual(loop["test"]["operator"], "and")
        self.assertEqual(loop["body"]["body"][0]["type"], "AssignmentStatement")

    def test_each_parse_starts_with_fresh_parser_state(self):
        first = parse_source("let first = 1")
        second = parse_source("let second = 2")

        self.assertEqual(first["body"][0]["id"]["name"], "first")
        self.assertEqual(second["body"][0]["id"]["name"], "second")

    def test_unterminated_blocks_raise_syntax_error(self):
        with self.assertRaisesRegex(SyntaxError, "Unterminated block"):
            parse_source("if x == 1 { let y = 2")

    def test_class_is_not_a_language_keyword_or_type(self):
        self.assertEqual(lexer.lexer("class"), ["class"])
        declaration = parse_source("let class = 1")["body"][0]
        self.assertEqual(declaration["id"]["name"], "class")
        with self.assertRaisesRegex(SyntaxError, "Unknown variable type"):
            parse_source("let value: Widget = 1")


if __name__ == "__main__":
    unittest.main()
