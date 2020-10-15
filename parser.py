from parsita import *
from parsita.util import constant

import sys

def concatenateall(x):
    return "".join(map(str, x))

def addifpossible(x):
    return correctprefix(x[1])

def correctprefix(x):
    if not x.startswith("Type("):
        return "Type(" + x + ")"
    if not x.endswith(")"):
        return "Type(" + x + ")"
    substr = x[5:-1]
    if substr.count('(') != substr.count(')'):
        return "Type(" + x + ")"
    balance = 0;
    for element in substr:
        if element == '(':
            balance += 1
        elif element == ')':
            balance -= 1
        if balance < 0:
            return "Type(" + x + ")"
    return x

class Parser(TextParsers, whitespace=r'[ \t\n\r]*'):
    idreg = reg(r'[a-z_A-Z][a-z_A-Z0-9]*')
    id = pred(idreg,
              (lambda x: x != 'module' and x != 'type'),
              "Identificator name cannot be 'module' or 'type'") > concatenateall
    rthen = lit(':-') > constant('')
    conj = lit(',') > constant('')
    disj = lit(';') > constant('')
    lbracket = lit('(') > constant('')
    rbracket = lit(')') > constant('')
    dot = lit('.') > constant('')

    mod = lit('module')
    type = lit('type')

    atom_in = (((id & atom_close) > (lambda x: "ID(" + x[0] + "), " + x[1]))
              | (id > (lambda x: "ID(" + x + ")"))
              | ((lbracket & atom_in & rbracket) > (lambda x: x[1]))) > concatenateall
    atom_in_gen = lbracket & atom_in & rbracket > (lambda x: "Atom(" + x[1] + ")")
    atom_close = (((id & atom_close) > (lambda x: "ID(" + x[0] + "), " + x[1]))
                  | (id > (lambda x: "ID(" + x + ")"))
                  | ((atom_in_gen & atom_close) > (lambda x: x[0] + ", " + x[1]))
                  | atom_in_gen) > concatenateall
    atom = (((id & atom_close) > (lambda x: "Atom(ID(" + x[0] + "), " + x[1] + ")"))
            | (id > (lambda x: "ID(" + x + ")"))) > concatenateall
    liter = (((lbracket & Disj & rbracket) > (lambda x: x[1])) | atom) > concatenateall
    Conj = (((liter & conj & Conj) > (lambda x: "Conj(" + x[0] + ", " + x[2] + ")"))
            | liter) > concatenateall
    Disj = (((Conj & disj & Disj) > (lambda x: "Disj(" + x[0] + ", " + x[2] + ")"))
            | Conj) > concatenateall
    relation = ((((atom & rthen & Disj) > (lambda x: "Head(" + x[0] + "), Body(" + x[2] + ")"))
                | atom) & dot) > (lambda x: "Rel(" + x[0] + ")")
    possible_t = (((lbracket & possible_t & rbracket & rep1('->' >> possible_t)) > (lambda x: "Type(" + x[1] + ", " + ", ".join(x[3]) + ")"))
                  | ((lbracket & possible_t & rbracket) > (lambda x: x[1]))
                  | (atom & rep1('->' >> possible_t) > (lambda x: "Type(" + x[0] + ", " + ", ".join(x[1]) + ")"))
                  | atom) > (lambda x: "".join(x))
    types = (rep1sep(possible_t, '->') > (lambda x: ", ".join(x))) > correctprefix
    type_block = type & id & types & dot > (lambda x: "Typedef(" + x[1] + ", " + x[2] + ")")
    mod_block = mod & id & dot > (lambda x: "Module(" + x[1] + ")")
    program = ((opt(mod_block) > (lambda x: "\n".join(x)))\
              & (rep(type_block) > (lambda x: "\n".join(x))) \
              & (rep(relation) > (lambda x: "\n".join(x)))) > (lambda x: "\n".join(x))

if __name__ == '__main__':
    filename = sys.argv[1]
    with open(filename, "r") as f:
        data = f.read()
    p = Parser.program.parse(data)
    if type(p) == Failure:
        print(p.message)
    else:
        resfile = open(filename + '.out', 'w')
        resfile.write(str(p.value))