import ply.yacc as yacc
import ply.lex as lex

reserved = {
   'ELEMENT' : 'ELEMENT',
   'ATTLIST' : 'ATTLIST',
   'CDATA' : 'CDATA'
}

tokens = [
          "TAG",
          "PCDATA",
          "IMPLIED",
          "REQUIRED",
          "COMMENT"
         ] + list(reserved.values())

literals = ['<', '>', '!', '?', '(', ')', '|', '+', '*', '-', ',', '#']

t_PCDATA = r"\#PCDATA"
t_CDATA = r"\#CDATA"
t_IMPLIED = r"\#IMPLIED"
t_REQUIRED = r"\#REQUIRED"

def t_TAG(t):
    r'\w+'
    t.type = reserved.get(t.value,'TAG')  # Check for reserved words
    return t
    
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


# with open(r"C:\Users\worten\Documents\UNI\Mestrado\Tese\Experimenttal\ResumeSectionTEST\ResumeSection.dtd",
                 # 'r', encoding='utf-8') as f:
    # dtd = f.read()        


# lexer.input(dtd)


# while True:
    # tok = lexer.token()
    # if not tok:
        # break
    # print(tok)