try:
    logo = """
    ███╗   ███╗  █████╗   ██████╗  ██╗  ██████╗ ██╗  ██╗ ██████╗   ██████╗  ███╗   ███╗  █████╗ 
    ████╗ ████║ ██╔══██╗ ██╔════╝  ██║ ██╔════╝ ██║  ██║ ██╔══██╗ ██╔═══██╗ ████╗ ████║ ██╔══██╗
    ██╔████╔██║ ███████║ ██║  ███╗ ██║ ██║      ███████║ ██████╔╝ ██║   ██║ ██╔████╔██║ ███████║
    ██║╚██╔╝██║ ██╔══██║ ██║   ██║ ██║ ██║      ██╔══██║ ██╔══██╗ ██║   ██║ ██║╚██╔╝██║ ██╔══██║
    ██║ ╚═╝ ██║ ██║  ██║ ╚██████╔╝ ██║ ╚██████╗ ██║  ██║ ██║  ██║ ╚██████╔╝ ██║ ╚═╝ ██║ ██║  ██║
    ╚═╝     ╚═╝ ╚═╝  ╚═╝  ╚═════╝  ╚═╝  ╚═════╝ ╚═╝  ╚═╝ ╚═╝  ╚═╝  ╚═════╝  ╚═╝     ╚═╝ ╚═╝  ╚═╝
    """
    print(logo)
    import lexer
    import parser
    from rich.traceback import install
    from pretty_print import pretty_print as pprint
    install(show_locals=True)

    input_stream = "from abc import everything"
    print(lexer.lexer(input_stream))
    pprint(parser.parse(lexer.lexer(input_stream)))
except KeyboardInterrupt:
    print('Program Stopped Successfully.')