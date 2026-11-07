# MAGICHROMA
## BY GODLYITSELF

## ADDED `parse_conditional()`
This function has been added to `parser.py` . It uses `pratt-parse()` to parse a conditional and return it in the format:
```AST JSON
"type" : "ConditionalExpression",
"body" : {
    "left" ; [
        ...
    ],
    "right" : [
        ...
    ]
}
```
Doing this needed to change `pratt_parse()` itself to add a line to break when it encounters a value from the dictionary `comparisons` from `token_list.py`.

## 2. ADDED FOR LOOPS AST
The function `parse_for_loop()` was added in `parser.py` to parse for loops.
The AST produced is following.
```AST JSON
...
"type" : "ForLoop",
"condition" : {...}, //mentioned above
"body" : {
    "type" : "CodeBlock",
    "body" : [...]
}
```
## 3. ADDED `de-comment.py`
In a previous commit I mentioned that commit-specific or non long-term comments were to start with `##` instead of `#`. To make removing them easier right before a commit, I made `de-comment.py`. It doesnt check for any folders starting with `.`.
Safe to say, it works.

## 4. ADDED `gradient_print.py`
This is an intresting peice of code I found. Ultimately I'll include it in `pretty_print.py`'s `pprint()` function and use it in `cli.py`.

## 5. IMPROVED LICENSE
This should be self explanatory. I previously used MIT LICENSE, but not anymore.