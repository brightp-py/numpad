from numpy import var
import ply.yacc as yacc

from numpadlex import tokens
from numpad import *

start = 'program'

precedence = (
    ('left', 'OP0'),
    ('left', 'OP1'),
    ('left', 'OP2'),
    ('left', 'OP3'),
    ('right', 'MIN')
)

def p_var(p):
    '''var : M NUMBER
           | M ZERO NUMBER
    '''
    p[0] = ''.join(map(str, p[1:]))

def p_op_0(p):
    '''op0 : DOT DOT
           | DOT S
           | DOT A
    '''
    p[0] = ''.join(p[1:])

def p_op_1(p):
    '''op1 : S
           | A
    '''
    p[0] = ''.join(p[1:])

def p_op_2(p):
    '''op2 : D
           | M
    '''
    p[0] = ''.join(p[1:])

def p_op_3(p):
    '''op3 : D A
           | M A
           | D S
           | M S
    '''
    p[0] = ''.join(p[1:])

def p_set(p):
    'set : N M'
    pass

def p_if(p):
    'if : N D'
    pass

def p_while(p):
    'while : N A D'
    pass

def p_list_create(p):
    'list_open : D DOT'
    p[0] = []

def p_list_append(p):
    'list_open : list_open expr DOT'
    p[0] = p[1] + [p[2]]

def p_list_close(p):
    'list : list_open expr D DOT'
    p[0] = p[1] + [p[2]]

def p_param_create(p):
    'paramlist : N NUMBER DOT'
    p[0] = [0] * p[2]

def p_param_def(p):
    'paramlist : N NUMBER DOT DOT NUMBER paramlist'
    p[6][p[2]] = p[5]
    p[0] = p[6]

def p_expr(p):
    '''expr : NUMBER
            | ZERO NUMBER   %prec MIN
            | ZERO
            | var
            | list
            | expr op0 expr %prec OP0
            | expr op1 expr %prec OP1
            | expr op2 expr %prec OP2
            | expr op3 expr %prec OP3
    '''
    if len(p) == 2:
        p[0] = Expression(p[1])
    elif len(p) == 3:
        p[0] = Expression(f"-{p[2]}")
    elif len(p) == 4:
        p[0] = OperExpression(p[1], p[2], p[3])

def p_function_def(p):
    '''stmt : set NUMBER DOT paramlist block
    '''
    p[0] = StatementDef(p[2], p[4], p[5])

def p_stmt_set(p):
    'stmt : set NUMBER DOT expr'
    p[0] = StatementSet(p[2], p[4])

def p_stmt_set_return(p):
    'stmt : set ZERO ZERO DOT expr'
    p[0] = StatementSet('00', p[5])

def p_stmt_if(p):
    'stmt : if expr block'
    p[0] = StatementIf(p[2], p[3])

def p_stmt_while(p):
    'stmt : while expr block'
    p[0] = StatementWhile(p[2], p[3])

def p_create_block(p):
    'open_block : stmt'
    p[0] = StatementBlock()
    p[0].append(p[1])

def p_append_block(p):
    'open_block : open_block stmt'
    p[0] = p[1]
    p[0].append(p[2])

def p_close_block(p):
    '''block : open_block N
    '''
    p[0] = p[1]

def p_program(p):
    'program : block'
    p[0] = p[1]

def p_extra_newlines(p):
    'program : program N'
    p[0] = p[1]

def p_error(p):
    if p:
        print("Syntax error at token", p.type, p.__dict__)
    else:
        print("Syntax error")

parser = yacc.yacc()

if __name__ == "__main__":
    with open('test.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    result = parser.parse(text)
    print(result)