from logging import raiseExceptions

import ply.lex as lex
import ply.yacc as yacc

tokens = [
    'FLOAT',
    'INT',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'MOD',
    'EXPONENT',
    'LPAREN',
    'RPAREN',
    'EQUALS',
    'NAME'
]


t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'\%'
t_EXPONENT = r'\^'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQUALS = r'\='

t_ignore = r' '

def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = 'NAME'
    return t

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()

precedence = (
    ('nonassoc', 'LPAREN', 'RPAREN'),
    ('right', 'MOD'),
    ('right', 'EXPONENT'),
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE')
)

def p_calc(p):
    '''
    calc : expression
        | setVariable
        | empty
    '''

    p[0] = evaluate(p[1])

def p_setVariable(p):
    '''
    setVariable : NAME EQUALS expression
    '''
    p[0] = ("=", p[1], p[3])

def p_recurse_expression(p):
    '''
    expression : expression TIMES expression
               | expression DIVIDE expression
               | expression PLUS expression
               | expression MINUS expression
    '''

    p[0] = (p[2], p[1], p[3])

def p_mod(p):
    '''
    expression : expression MOD expression

    '''

    p[0] = ('%', p[1], p[3])

def p_exponent(p):
    '''
    expression : expression EXPONENT expression

    '''

    p[0] = ('^', p[1], p[3])

def p_paran(p):
    '''
    expression : LPAREN expression RPAREN
    '''
    p[0] = p[2]

def p_int_expression(p):
    '''
    expression : INT
    '''

    p[0] = p[1]

def p_float_expression(p):
    '''
    expression : FLOAT
    '''

    p[0] = p[1]

def p_expression_variable(p):
    '''
    expression : NAME
    '''

    p[0] = ('variable',p[1])

def p_error(p):
    raise ValueError('Syntax error')

def p_empty(p):
    '''
    empty :
    '''
    p[0] = None


varDict = {}

def clearVars():
    global varDict
    varDict = {}

def evaluate(p):
    global varDict
    if type(p) == tuple:
        if p[0] == "+":
            return evaluate(p[1]) + evaluate(p[2])
        elif p[0] == '-':
            return evaluate(p[1]) - evaluate(p[2])
        elif p[0] == '*':
            return evaluate(p[1]) * evaluate(p[2])
        elif p[0] == '/':
            return evaluate(p[1]) / evaluate(p[2])
        elif p[0] == '%':
            return evaluate(p[1]) % evaluate(p[2])
        elif p[0] == '^':
            return evaluate(p[1]) ** evaluate(p[2])
        elif p[0] == '=':
            varDict[p[1]] = evaluate(p[2])
            return varDict[p[1]]
        elif p[0] == 'variable':
            if p[1] not in varDict:
                raise ValueError('var')

            else:
                return varDict[p[1]]
    else:
        return p

parser = yacc.yacc()