# MagiChrome
A new language I've been making.

## Parser AST

The parser returns dictionaries with a `type` field. Every expression is a
typed node, and statement bodies are arrays of nodes:

- `Program` and `BlockStatement`: `body`
- `VariableDeclaration`: `kind`, `id`, `annotation`, `init`
- `FunctionDeclaration`: `id`, `params`, `body`; each `Parameter` has an
  `id` and `annotation`
- `IfStatement`: `test`, `consequent`, `alternate`
- `ForStatement`: `test`, `body`
- `AssignmentStatement`: `target`, `value`
- `ExpressionStatement`: `expression`
- `BinaryExpression`: `operator`, `left`, `right`
- `UnaryExpression`: `operator`, `argument`
- `CallExpression`: `callee`, `arguments`
- `Identifier`, `NumericLiteral`, `StringLiteral`: `name` or `value`

An `if`/`elif` chain is represented as nested `IfStatement` nodes in
`alternate`; the final `else` is a `BlockStatement`, or `null` when absent.
