from token_list import tokens

def lexer(code: str):
    tokens_list = []
    cursor = 0
    length = len(code)

    # Sort operators by length descending to match longer operators (like '==') before shorter ones (like '=')
    # Filter out alphabetical keywords from this specific operator check
    operators = [k for k in tokens.keys() if not (k[0].isalpha() or k[0] == '_')]
    operators.sort(key=len, reverse=True)

    while cursor < length:
        char = code[cursor]

        # 1. Skip whitespace
        if char.isspace():
            cursor += 1
            continue

        # 2. Match multi-character or single-character operators
        matched_operator = False
        for op in operators:
            op_len = len(op)
            if code[cursor:cursor + op_len] == op:
                tokens_list.append(tokens[op])
                cursor += op_len
                matched_operator = True
                break
        if matched_operator:
            continue

        # 3. Handle Identifiers and Keywords (like 'let')
        if char.isalpha() or char == '_':
            word = ""
            while cursor < length and (code[cursor].isalnum() or code[cursor] == '_'):
                word += code[cursor]
                cursor += 1
            
            # Check if the full word is a reserved keyword in your token list
            if word in tokens:
                tokens_list.append(tokens[word])
            else:
                tokens_list.append(word) # Or your identifier token type, e.g., ('IDENTIFIER', word)
            continue

        # 4. Handle Numbers
        if char.isdigit():
            number = ""
            while cursor < length and code[cursor].isdigit():
                number += code[cursor]
                cursor += 1
            tokens_list.append(number)
            continue

        # 5. Handle Strings (since your example includes "ki")
        if char == '"' or char == "'":
            quote_type = char
            string_val = char  # Keep or omit quotes based on preference
            cursor += 1
            while cursor < length and code[cursor] != quote_type:
                string_val += code[cursor]
                cursor += 1
            if cursor < length:
                string_val += code[cursor] # Close quote
                cursor += 1
            tokens_list.append(string_val)
            continue

        raise SyntaxError(f"Unexpected character: {char}")

    return tokens_list