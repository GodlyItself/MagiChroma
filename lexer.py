from token_list import tokens

def lexer(code: str):
    tokens_list = []
    cursor = 0
    length = len(code)

    while cursor < length:
        char = code[cursor]

        if char.isspace():
            cursor += 1
            continue

        if cursor + 1 < length and code[cursor:cursor+2] in tokens:
            tokens_list.append(code[cursor:cursor+2])
            cursor += 2
            continue

        if char in tokens:
            tokens_list.append(char)
            cursor += 1
            continue

        if char.isalpha() or char == '_':
            word = ""
            while cursor < length and (code[cursor].isalnum() or code[cursor] == '_'):
                word += code[cursor]
                cursor += 1

            tokens_list.append(word) 
            continue

        if char.isdigit():
            number = ""
            while cursor < length and code[cursor].isdigit():
                number += code[cursor]
                cursor += 1
            tokens_list.append(number)
            continue

        raise SyntaxError(f"Unexpected character: {char}")

    return tokens_list

#print(lexer('abc = "ki"'))