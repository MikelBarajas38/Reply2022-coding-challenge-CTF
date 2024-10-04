import argparse
from enum import Enum

class Instruction(Enum):
    STRING = 1
    INT = 2
    PRINT = 3
    VAR = 4
    ASSIGN = 5
    ADD = 6
    SUB = 7
    MUL = 8
    DIV = 9
    IF = 10
    ELSE = 11
    ENDIF = 12
    ENDELSE = 14
    EQUAL = 15
    NOT_EQUAL = 16
    GREATER = 17
    GREATER_OR_EQUAL = 18
    LESSER = 19
    LESSER_OR_EQUAL = 20
    OR = 21
    AND = 22
    LOOP = 23
    ENDLOOP = 24

instruction_set = {
    'B': Instruction.STRING,
    'N': Instruction.INT,
    'P': Instruction.PRINT,
    'V': Instruction.VAR,
    '=': Instruction.ASSIGN,
    'ADD': Instruction.ADD,
    'SUB': Instruction.SUB,
    'MUL': Instruction.MUL,
    'DIV': Instruction.DIV,
    'BOH': Instruction.IF,
    'OH': Instruction.ELSE,
    'HOB': Instruction.ENDIF,
    'HO': Instruction.ENDELSE,
    'QE': Instruction.EQUAL,
    'EN': Instruction.NOT_EQUAL,
    'TG': Instruction.GREATER,
    'EG': Instruction.GREATER_OR_EQUAL,
    'TL': Instruction.LESSER,
    'EL': Instruction.LESSER_OR_EQUAL,
    'OR': Instruction.OR,
    'AND': Instruction.AND,
    'LOOP': Instruction.LOOP,
    'POOL': Instruction.ENDLOOP
}

class Interpreter:
    
    def __init__(self):

        self.stack = []
        self.memo = {}

        self. int_op = {
            'a': Instruction.ADD,
            's': Instruction.SUB,
            'm': Instruction.MUL,
            'd': Instruction.DIV
        }

    def parse(self, path):

        with open(path, 'r') as f:
            lines = f.readlines()

        code = []
        for line in lines:
            
            line = line.strip()

            if line.startswith('//'):
                continue

            if not line:
                continue

            instructions = line.split()

            for instruction in instructions[::-1]:
                code.append(instruction)

        return code

    def operate(self, a, b, op):
        operations = {
            Instruction.ADD: lambda x, y: x + y,
            Instruction.SUB: lambda x, y: x - y,
            Instruction.MUL: lambda x, y: x * y,
            Instruction.DIV: lambda x, y: x // y,
            Instruction.EQUAL: lambda x, y: x == y,
            Instruction.NOT_EQUAL: lambda x, y: x != y,
            Instruction.GREATER: lambda x, y: x > y,
            Instruction.GREATER_OR_EQUAL: lambda x, y: x >= y,
            Instruction.LESSER: lambda x, y: x < y,
            Instruction.LESSER_OR_EQUAL: lambda x, y: x <= y,
            Instruction.OR: lambda x, y: x or y,
            Instruction.AND: lambda x, y: x and y
        }
        return operations[op](a, b)

    def top(self, get_repr=False):
        top = self.stack[-1]
        if top in self.memo and self.memo[top] is not None and not get_repr:
            top = self.memo[top]
        return top

    def pop(self):
        self.stack.pop()

    def push(self, val):
        self.stack.append(val)

    def solve_condition(self, code):

        lc = 0
        self.solve([code[lc]])

        lc += 1

        while lc < len(code) and code[lc] in instruction_set and (instruction_set[code[lc]] == Instruction.OR or instruction_set[code[lc]] == Instruction.AND):
            
            op = instruction_set[code[lc]]
            lc += 1

            self.solve([code[lc]])

            a = self.top()
            self.pop()

            b = self.top()
            self.pop()

            self.push(self.operate(a, b, op))

            lc += 1

        condition = self.top()
        self.pop()

        return condition

    def solve(self, code):

        lc = 0

        while lc < len(code):

            line = code[lc]

            if line in instruction_set:
                 
                instruction = instruction_set[line]

                if instruction == Instruction.IF:

                    cond_lc = lc
                    cond_lc += 1

                    condition = []
                    while code[cond_lc] != '|':
                        condition.append(code[cond_lc])
                        cond_lc += 1

                    cond_lc += 1

                    true_code = []

                    depth = 1

                    while depth > 0:

                        if code[cond_lc] in instruction_set:

                            instruction = instruction_set[code[cond_lc]]

                            if (instruction == Instruction.ELSE or instruction == Instruction.ENDIF) and depth == 1:
                                break

                            if instruction == Instruction.IF:
                                depth += 1

                            if instruction == Instruction.ENDIF:
                                depth -= 1   


                        true_code.append(code[cond_lc])
                        cond_lc += 1

                    false_code = []

                    if instruction_set[code[cond_lc]] == Instruction.ELSE:

                        cond_lc += 1

                        false_code = ['BOH']

                        depth = 1

                        while depth > 0:

                            if code[cond_lc] in instruction_set:

                                instruction = instruction_set[code[cond_lc]]

                                if instruction == Instruction.ENDELSE and depth == 1:
                                    break

                                if instruction == Instruction.IF:
                                    depth += 1

                                if instruction == Instruction.ENDIF:
                                    depth -= 1

                            false_code.append(code[cond_lc])
                            cond_lc += 1
                        
                        false_code.append('HOB')

                        cond_lc += 1

                    if self.solve_condition(condition):
                        self.solve(true_code)
                    else:
                        self.solve(false_code)

                    lc = cond_lc

                elif instruction == Instruction.LOOP:

                    loop_lc = lc
                    loop_lc += 1
                    
                    condition = []
                    while code[loop_lc] != '|':
                        condition.append(code[loop_lc])
                        loop_lc += 1

                    loop_lc += 1

                    loop_code = []

                    depth = 1

                    while depth > 0:

                        if code[loop_lc] in instruction_set:

                            instruction = instruction_set[code[loop_lc]]

                            if instruction == Instruction.ENDLOOP and depth == 1:
                                break

                            if instruction == Instruction.ENDLOOP:
                                depth -= 1

                            if instruction == Instruction.LOOP:
                                depth += 1

                        loop_code.append(code[loop_lc])
                        loop_lc += 1

                    while self.solve_condition(condition):
                        self.solve(loop_code)

                    lc = loop_lc

            else:

                pc = 0

                while pc < len(line):

                    instruction = ''
                    while instruction not in instruction_set:
                        instruction += line[pc]
                        pc += 1

                    instruction = instruction_set[instruction]

                    if instruction == Instruction.STRING:

                        s = ''
                        while not line[pc].isupper() and line[pc] not in instruction_set:
                            s += line[pc]
                            pc += 2

                        self.push(s[::-1])

                    elif instruction == Instruction.INT:

                        lhs = ''

                        while line[pc].isdigit():
                            lhs += line[pc]
                            pc += 1
                
                        while line[pc] in self.int_op:

                            op = line[pc]
                            pc += 1

                            rhs = ''
                            while line[pc].isdigit():
                                rhs += line[pc]
                                pc += 1

                            lhs = self.operate(int(lhs), int(rhs), self.int_op[op])

                        self.push(int(lhs))

                    elif instruction == Instruction.VAR:

                        v = '$'

                        while not line[pc].isupper() and line[pc] not in instruction_set:
                            v += line[pc]
                            pc += 2 
                        
                        if v not in self.memo:
                            self.memo[v] = None

                        self.push(v)

                    elif instruction == Instruction.ASSIGN:

                        v = self.top(get_repr=True)
                        self.pop()

                        self.memo[v] = self.top()
                        self.pop()

                    elif instruction in [Instruction.ADD, Instruction.SUB, Instruction.MUL, Instruction.DIV,
                                        Instruction.EQUAL, Instruction.NOT_EQUAL, Instruction.GREATER, Instruction.GREATER_OR_EQUAL, Instruction.LESSER, Instruction.LESSER_OR_EQUAL]:

                        b = self.top()
                        self.pop()

                        a = self.top()
                        self.pop()

                        self.push(self.operate(a, b, instruction))

                    elif instruction == Instruction.PRINT:

                        val = self.top()
                        self.pop()
                        print(val, end='')

            lc += 1

def main():

    parser = argparse.ArgumentParser(description='First challenge')
    parser.add_argument('path', help='Path to input file')
    args = parser.parse_args()
    path = args.path

    interpreter = Interpreter()

    code = interpreter.parse(path)

    interpreter.solve(code)

if __name__ == '__main__':
    main()