import re
import ply.yacc as yacc
from .dtd_lex import tokens

"""
dtd : declarations

declarations : declarations declaration
             | declaration
      
declaration : '<' '!' ELEMENT TAG content '>'
            | '<' '!' ATTLIST TAG att_content '>'
            | entity

content : child
        | '(' PCDATA options ) '*'
        | '(' PCDATA ')' quantifier
        
child : '(' childElems ')' quantifier

childElems : childElems ',' childElem
           | childElems '|' childElem
           | childElem

childElem : child
          | leaf

leaf : TAG quantifier

quantifier : '*' | '+' | '?'
           | empty
      
options : options '|' TAG 
        | '|' TAG  

att_content : TAG att_type att_value_declaration

att_type : CDATA

att_value_declaration : IMPLIED
                      | REQUIRED
"""

def p_declarations(p):
    """
    declarations : declarations declaration
                 | declaration
    """
    if(len(p)==3):
        p[0] = p[1] | p[2] 
    else:
        p[0] = p[1]
        
def p_declaration(p):
    """
    declaration : '<' '!' ELEMENT TAG content '>'
                | '<' '!' ATTLIST TAG att_content '>'
    """
    if(p[3]=='ATTLIST'):
        p[4] = '_' + p[4]
    p[0] = {p[4]: p[5]}

def p_content(p):
    """
    content : child
            | '(' PCDATA options ')' '*'
            | '(' PCDATA ')' quantifier
    """
    
    if(len(p)==2):
        p[0] = {'content_type': 'normal', 'children': p[1]}
    elif(len(p)==6):
        p[0] = {'content_type': 'mixed', 'children': p[3]}
    else:
        p[0] = {'content_type': 'text_only'}

def p_options(p):
    """
    options : options '|' TAG 
            | '|' TAG 
    """
    if(len(p)==4):
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[2]]

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
        
def p_att_content(p):
    "att_content : TAG att_type att_value_declaration"
    
    p[0] = {'name': p[1], 'type': p[2], 'value_declaration': p[3]}

def p_att_type(p):
    "att_type : CDATA"
    
    p[0] = p[1]

def p_att_value_declaration(p):
    """
    att_value_declaration : IMPLIED
                          | REQUIRED
    """
    p[0] = p[1]
    
    
def p_empty(p):
    'empty :'
    pass

dtd_parser = yacc.yacc()
