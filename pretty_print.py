import json
import re

def pretty_print(data: dict) -> None:
    """
    Prints a dictionary with strict newlines after [, ], {, }, and commas,
    maintaining a consistent 4-space indentation level.
    """
    # 1. Convert dict to a single-line JSON string (removes existing formatting whitespace)
    raw_str = json.dumps(data)
    
    # 2. Tokenize the string into formatting structural elements and content strings
    # This ensures commas inside text strings don't cause accidental newlines
    tokens = re.split(r'([\{\}\[\],])', raw_str)
    
    indent_level = 0
    indent_size = 4
    
    for token in tokens:
        if not token:
            continue
            
        # Strip structural elements, but preserve content spaces
        stripped_token = token.strip() if token in '\{\}[]' else token
        
        # Adjust indentation BEFORE printing closing brackets/braces
        if stripped_token in '}]':
            indent_level = max(0, indent_level - 1)
            print() # Force newline before closing
            print(" " * (indent_level * indent_size) + stripped_token, end="")
            
        elif stripped_token in '{[':
            # Print opening bracket/brace
            print(stripped_token, end="")
            indent_level += 1
            print() # Force newline after opening
            print(" " * (indent_level * indent_size), end="")
            
        elif stripped_token == ',':
            # Print comma
            print(stripped_token) # Force newline after comma
            print(" " * (indent_level * indent_size), end="")
            
        else:
            # Print standard keys, values, or colons
            # Clean up JSON spacing around colons for better readability
            formatted_content = token.replace(':', ': ')
            print(formatted_content, end="")
            
    print() # Final trailing newline

