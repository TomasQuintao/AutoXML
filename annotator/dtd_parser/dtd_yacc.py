import re
import ply.yacc as yacc
from .dtd_lex import tokens

"""
dtd : declarations

declarations : declarations declaration
             | declaration
      
declaration : '<' '!' ELEMENT TAG content '>'

content : child
        | '(' PCDATA options ')' '*'
        | '(' PCDATA ')' quantifier
        | EMPTY_ELEM
        | ANY
        
child : '(' childElems ')' quantifier

childElems : childElems ',' childElem
           | childElems '|' childElem
           | childElem

childElem : child
          | leaf

leaf : TAG quantifier

quantifier : '*' 
           | '+' 
           | '?'
           | empty
      
options : options '|' TAG 
        | '|' TAG  
"""

def p_declarations(p):
    """
    declarations : declarations declaration
                 | declaration
    """
    if (len(p)==2):
        p[0] = p[1]
    else:
        key = list(p[2].keys())[0]
        
        if (key[0]=='_' and key in p[1]):
            p[1][key] += p[2][key]
            p[0] = p[1]
        else:
            p[0] = p[1] | p[2]

def p_declaration(p):
    "declaration : '<' '!' ELEMENT TAG content '>'"

    p[0] = {p[4]: p[5]}

def p_content(p):
    """
    content : child
            | '(' PCDATA options ')' '*'
            | '(' PCDATA ')'
            | EMPTY_ELEM
            | ANY
    """
    if(len(p)==6):
        p[0] = {'content_type': 'mixed', 'children': p[3]}
    elif(len(p)==4):
        p[0] = {'content_type': 'text_only'}
    elif(len(p)==2):
        if(p[1]=='EMPTY'):
            p[0] = {'content_type': 'empty'}
        elif(p[1]=='ANY'):
            p[0] = {'content_type': 'free'}
        else:           
            p[0] = {'content_type': 'normal', 'children': p[1]}
    

def p_child(p):
    "child : '(' childElems ')' quantifier"
    
    p[0] = p[2]
    
def p_childElems(p):
    """
    childElems : childElems ',' childElem
               | childElems '|' childElem
               | childElem
    """
    if(len(p)==4):
        p[0] = p[1] + p[3]
    else:
        p[0] = p[1]

def p_childElem(p):
    """
    childElem : child
              | leaf
    """
    p[0] = p[1]

def p_leaf(p):
    "leaf : TAG quantifier"
    
    p[0] = [p[1]]

def p_quantifier(p):
    """
    quantifier : '*' 
               | '+' 
               | '?'
               | empty
    """
    if(len(p)==2):
        p[0] = p[1]
    else:
        p[0] = '_'

def p_options(p):
    """
    options : options '|' TAG 
            | '|' TAG 
    """
    if(len(p)==4):
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[2]]   
    
def p_empty(p):
    'empty :'
    pass

dtd_parser = yacc.yacc()
