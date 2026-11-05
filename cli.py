import lexer
import parser
from rich.traceback import install
from pretty_print import pretty_print as pprint
install(show_locals=True)

input_stream =' let x = (9)'
print(lexer.lexer(input_stream))
print(parser.parse(lexer.lexer(input_stream)))