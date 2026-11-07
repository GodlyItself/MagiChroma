import os
import tokenize

def clean_file(file_path):
    """
    Safely removes '##' and everything after it on that line,
    ignoring '##' found inside strings or docstrings.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        modified = False
        
        with open(file_path, 'rb') as f:
            tokens = list(tokenize.tokenize(f.readline))
            
        for token in reversed(tokens):
            if token.type == tokenize.COMMENT:
                comment_text = token.string
                
                if '##' in comment_text:
                    line_idx = token.start[0] - 1  
                    current_line = lines[line_idx]
                    
                    start_col = token.start[1]
                    comment_line_part = current_line[start_col:]
                    
                    hash_offset = comment_line_part.find('##')
                    if hash_offset != -1:
                        exact_cutoff = start_col + hash_offset
                        
                        ends_with_newline = current_line.endswith('\n')
                        lines[line_idx] = current_line[:exact_cutoff] + ('\n' if ends_with_newline else '')
                        modified = True
                        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(True, f"Cleaned: {file_path}")
            
    except Exception as e:
        print(False, f"Skipped due to error parsing {file_path}: {e}")

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        
        for filename in filenames:
            if filename.endswith('.py') and filename != os.path.basename(__file__):
                file_path = os.path.join(dirpath, filename)
                clean_file(file_path)

if __name__ == '__main__':
    main()
