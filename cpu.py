import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001

CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

SP = 7

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[SP] = 255
        self.pc = 0
        self.halted = False
        # flag register changes based on the operands given to the CMP opcode
        self.FL = {"E": 0, "L": 0, "G": 0
        }

    def ram_read(self, address): # access RAM within CPU object
        return self.ram[address]

    def ram_write(self, address, val): # access RAM within CPU object
        self.ram[address] = val
        return self.ram[address]

    def load(self):
        """Load a program into memory."""
    
        address = 0

        if len(sys.argv) != 2:
            print('incorrect number of arguments')
            sys.exit(1)

        with open(sys.argv[1]) as f:  
            for line in f:
                    n = line.split("#", 1)[0]
                    if n.strip() == "":
                        continue
                    value = int(n, 2) # convert binary string to integer
                    self.ram[address] = value
                    address += 1 
    
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                # FL E
                self.FL["G"] = 0b00000000
                self.FL["E"] = 0b00000001
                self.FL["L"] = 0b00000000

            elif self.reg[reg_a] < self.reg[reg_b]:
                # FL L
                self.FL["G"] = 0b00000000
                self.FL["E"] = 0b00000000
                self.FL["L"] = 0b00000001 
            elif self.reg[reg_a] > self.reg[reg_b]:
                # FL G
                self.FL["G"] = 0b00000001
                self.FL["E"] = 0b00000000
                self.FL["L"] = 0b00000000
        else:
            raise Exception("Unsupported ALU operation")
    
    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
    
    def run(self):
        """Run the CPU."""
        while not self.halted:

            instruction = self.ram_read(self.pc)
            value1 = self.ram_read(self.pc + 1) #index
            value2 = self.ram_read(self.pc + 2) #value

            if instruction == PRN: # print numeric value stored in the given register, print to the console the decimal integer value that is stored in the given register
                print(self.reg[value1])
                self.pc += 2

            elif instruction == LDI: # set the value of a register to an integer
                self.reg[value1] = value2
                self.pc += 3
            
            elif instruction == HLT: # halt the CPU (and exit the emulator)
                self.halted = True
                self.pc += 1
    
            elif instruction == MUL: # multiply the values in two registers together and store the result in registerA.
                self.alu("MUL", value1, value2)
                self.pc += 3

            elif instruction == PUSH: 
                # decrement the SP (stack pointer)
                self.reg[SP] -= 1 
                address = self.reg[SP]
                reg_num = value1
                value = self.reg[reg_num]
                # copy the value in the given register to the address pointed to by SP
                self.ram_write(address, value) 
                self.pc += 2

            elif instruction == POP: 
                # save the value on top of the stack to the given register
                value = self.ram_read(self.reg[SP])
                reg_num = value1
                self.reg[reg_num] = value
                # increment the stack pointer
                self.reg[SP] += 1
                self.pc += 2

            elif instruction == CMP: # compare values in two registers
                self.alu("CMP", value1, value2)
                self.pc += 3

            elif instruction == JMP: # jump to the address stored in the given register
                self.pc = self.reg[value1]

            elif instruction == JEQ: # if equal FL is set (true), jump to the address stored in the given register
                if self.FL["E"] == 1:
                    self.pc = self.reg[value1]
                else:
                    self.pc += 2

            elif instruction == JNE: # if E FL is clear (false, 0), jump to the address stored in the given register
                if self.FL["E"] == 0b00000000:
                   self.pc = self.reg[value1]
                else:
                    self.pc += 2
