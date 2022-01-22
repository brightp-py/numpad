import ply.lex as lex

tokens = (
    'D',
    'M',
    'S',
    'A',
    'NUMBER',
    'DOT',
    'N',
    'ZERO'
)

t_D = r'/'
t_M = r'\*'
t_S = r'-'
t_A = r'\+'
t_DOT = r'(?<!\n)\.'
# t_ZERO = r'(?<!\d)0'
t_ignore = r' '

def t_NUMBER(t):
    r'([1-9]\d*)'
    t.value = int(t.value)
    return t

def t_ZERO(t):
    r'(?<![1-9])0'
    t.value = 0
    return t

def t_N(t):
    r'\n'
    t.lexer.lineno += t.value.count('\n')
    return t

def t_whitespace(t):
    r'(?<=\n)\.+'
    pass

def t_comment(t):
    r'\#[^\n]*\n'
    pass

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()

if __name__ == "__main__":
    with open('test.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    lexer.input(text)
    i = 0
    while i < 100:
        tok = lexer.token()
        if not tok:
            break
        print(tok)
        i += 1