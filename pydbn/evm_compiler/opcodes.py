

class Opcode(object):
    def __init__(self, mnemonic, params=None):
        self.mnemonic = mnemonic
        self.params = params

        self.args = None

    def ethasm_format(self):
        out = self.mnemonic
        if self.params is not None:
            out += "("
            out += ', '.join(["$$"] * self.params)
            out += ")"
        return out

STOP    = Opcode('STOP')
ADD     = Opcode('ADD', 2)
MUL     = Opcode('MUL', 2)
SUB     = Opcode('SUB', 2)
DIV     = Opcode('DIV', 2)
SDIV    = Opcode('SDIV', 2)
MOD     = Opcode('MOD', 2)
SMOD    = Opcode('SMOD', 2)

LT      = Opcode('LT', 2)
GT      = Opcode('GT', 2)
SLT     = Opcode('SLT', 2)
SGT     = Opcode('SGT', 2)
EQ      = Opcode('EQ', 2)
ISZERO  = Opcode('ISZERO', 1)

AND     = Opcode('AND', 2)
OR      = Opcode('OR', 2)
XOR     = Opcode('XOR', 2)
NOT     = Opcode('NOT', 1)

SHL     = Opcode('SHL', 2)
SHR     = Opcode('SHR', 2)
SAR     = Opcode('SAR', 2)

POP     = Opcode('POP', 0)
MLOAD   = Opcode('MLOAD', 1)
MSTORE  = Opcode('MSTORE', 2)
MSTORE8 = Opcode('MSTORE8', 2)

JUMP    = Opcode('JUMP', 1)
JUMPI   = Opcode('JUMPI', 2)

DUP1    = Opcode('DUP1')
DUP2    = Opcode('DUP2')
DUP3    = Opcode('DUP3')
DUP4    = Opcode('DUP4')
DUP5    = Opcode('DUP5')
DUP6    = Opcode('DUP6')
DUP7    = Opcode('DUP7')
DUP8    = Opcode('DUP8')
DUP9    = Opcode('DUP9')
DUP10   = Opcode('DUP10')
DUP11   = Opcode('DUP11')
DUP12   = Opcode('DUP12')
DUP13   = Opcode('DUP13')
DUP14   = Opcode('DUP14')
DUP15   = Opcode('DUP15')
DUP16   = Opcode('DUP16')

SWAP1   = Opcode('SWAP1')
SWAP2   = Opcode('SWAP2')
SWAP3   = Opcode('SWAP3')
SWAP4   = Opcode('SWAP4')
SWAP5   = Opcode('SWAP5')
SWAP6   = Opcode('SWAP6')
SWAP7   = Opcode('SWAP7')
SWAP8   = Opcode('SWAP8')
SWAP9   = Opcode('SWAP9')
SWAP10  = Opcode('SWAP10')
SWAP11  = Opcode('SWAP11')
SWAP12  = Opcode('SWAP12')
SWAP13  = Opcode('SWAP13')
SWAP14  = Opcode('SWAP14')
SWAP15  = Opcode('SWAP15')
SWAP16  = Opcode('SWAP16')


REVERT = Opcode('REVERT', 2)
