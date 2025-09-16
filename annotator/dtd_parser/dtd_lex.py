import ply.yacc as yacc
import ply.lex as lex

reserved = {
   'ELEMENT' : 'ELEMENT',
   'ANY' : 'ANY',
   'EMPTY' : 'EMPTY_ELEM'
}

tokens = [
          "TAG",
          "PCDATA",
          "COMMENT",
          "ENTDECL",
          "ATTDECL"
         ] + list(reserved.values())

literals = ['<', '>', '!', '?', '(', ')', '"',
            '|', '+', '*', '-', ',', '#']

t_PCDATA = r"\#PCDATA"

def t_TAG(t):
    r'\w+'
    t.type = reserved.get(t.value,'TAG')  # Check for reserved words
    return t

def t_ENTDECL(t):
    r'<!ENTITY[^>]+>'
    t.lexer.lineno += t.value.count('\n')
    pass

def t_ATTDECL(t):
    r'<!ATTLIST[^>]+>'
    t.lexer.lineno += t.value.count('\n')
    pass
    
def t_COMMENT(t):
    r'<!--(.|\n)*?-->'
    t.lexer.lineno += t.value.count('\n')  # update line number
    pass  
    
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    
t_ignore = ' \t'

def t_error(t):
    print(f"Ilegal character '{t.value[0]}' on line {t.lexer.lineno}")
    t.lexer.skip(1)
    
lexer = lex.lex()


dtd = """<!ENTITY AUTHOR "John Doe">
<!ENTITY COMPANY "JD Power Tools, Inc.">
<!ENTITY EMAIL "jd@jd-tools.com">

<!ELEMENT CATALOG (PRODUCT+)>

<!ELEMENT PRODUCT
(SPECIFICATIONS+,OPTIONS?,PRICE+,NOTES?)>
<!ATTLIST PRODUCT
NAME CDATA #IMPLIED
CATEGORY (HandTool|Table|Shop-Professional) "HandTool"
PARTNUM CDATA #IMPLIED
PLANT (Pittsburgh|Milwaukee|Chicago) "Chicago"
INVENTORY (InStock|Backordered|Discontinued) "InStock">

<!ELEMENT SPECIFICATIONS EMPTY>


<!ELEMENT OPTIONS (#PCDATA)>
<!ATTLIST OPTIONS
FINISH (Metal|Polished|Matte) "Matte"
ADAPTER (Included|Optional|NotApplicable) "Included"
CASE (HardShell|Soft|NotApplicable) "HardShell">

<!ELEMENT PRICE (#PCDATA)>
<!ATTLIST PRICE
MSRP CDATA #IMPLIED
WHOLESALE CDATA #IMPLIED
STREET CDATA #IMPLIED
SHIPPING CDATA #IMPLIED>

<!ELEMENT NOTES ANY>"""

# lexer.input(dtd)


# while True:
    # tok = lexer.token()
    # if not tok:
        # break
    # print(tok)