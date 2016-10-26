import hashlib
from random import choice
from operator import add, sub#, mul

OPERATORS = [
    (add, 'plus', '+'),
    (sub, 'minus', '-'),
    #(mul, 'multiplied by', 'by', '*')
]

NUMBERS = [
    (0, 'zero', '0'),
    (1, 'one', '1'),
    (2, 'two', '2'),
    (3, 'three', '3'),
    (4, 'four', '4'),
    (5, 'five', '5'),
    (6, 'six', '6'),
    (7, 'seven', '7'),
    (8, 'eight', '8'),
    (9, 'nine', '9'),
    (10, 'ten', '10')
]

def pick():
    a = choice(NUMBERS)
    op = choice(OPERATORS)
    b = choice(NUMBERS)

    if op[0] is sub:
        b = choice(NUMBERS[:a[0] + 1])

    return a, op, b

def compute(a, op, b):
    return op[0](a[0], b[0])

def speak(a, op, b):
    return '%s %s %s' % (choice(a[1:]), choice(op[1:]), choice(b[1:]))

def hash(result):
    return hashlib.sha256(str(result)).hexdigest()

def generate():
    (a, op, b) = pick()

    return compute(a, op, b), speak(a, op, b)
