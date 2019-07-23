# UART Pattern Generator using LFSR (Linear feedback shift register)
# See: https://www.xilinx.com/support/documentation/application_notes/xapp052.pdf

import boolean
START_BITS = 1
STOP_BITS = 1
DATA_BITS = 7
UART_BITS = START_BITS + DATA_BITS + STOP_BITS
LFSR_BITS = 7 # Width of the linear feedback shift register
TAP0_BIT = 0
TAP1_BIT = 6
MASK = (2 ** LFSR_BITS) - 1
startbit = '0' * START_BITS
stopbit = '1' * STOP_BITS

string = "Hello World\n"
minstates = len(string) * UART_BITS
print("String requires", minstates, "states.")

states = (2 ** LFSR_BITS) - 1
print("LFSR can encode", states, "states.")

if minstates > states:
    raise BaseException("Too many states required. Need higher LFSR_BITS")

# Convert the string to a pattern of bits
pattern = [startbit + ("{0:b}".format(ord(c)).rjust(DATA_BITS, '0')) + stopbit for c in string]
pattern = ''.join(pattern)

# Pad the pattern with idle states
pattern = pattern.ljust(states,'1')

print("Pattern :", pattern)

#TODO if all zeroes, insert a one!

uniquestates = list()
sr = 1
while True:
    # Shift the register
    sr_tap0 = (sr >> TAP0_BIT) & 0x01
    sr_tap1 = (sr >> TAP1_BIT) & 0x01
    sr = (sr << 1) | (sr_tap0 ^ sr_tap1)
    sr &= MASK

    if sr not in uniquestates:
        uniquestates.append(sr)
    else:
        break
print("LFSR produces sequence of", len(uniquestates),"unique states")
if states != len(uniquestates):
    print("Warning: LFSR produces unexpected number of unique states")

if len(uniquestates) < minstates:
    raise BaseException("LFSR cannot hold enough states to encode the full pattern")

algebra = boolean.BooleanAlgebra()
q0, q1, q2, q3, q4, q5, q6, q7 = algebra.symbols('q0','q1','q2','q3','q4','q5','q6','q7')

q0 = algebra.parse('FALSE')
for state, output in zip(uniquestates, pattern):
    print(str(state).rjust(4),output)
    if (output == '1'):
        if LFSR_BITS >= 1:
            term = q1 if state & 0x01 else ~q1
        if LFSR_BITS >= 2:
            term &= q2 if state & 0x02 else ~q2
        if LFSR_BITS >= 3:
            term &= q3 if state & 0x04 else ~q3
        if LFSR_BITS >= 4:
            term &= q4 if state & 0x08 else ~q4
        if LFSR_BITS >= 5:
            term &= q5 if state & 0x10 else ~q5
        if LFSR_BITS >= 6:
            term &= q6 if state & 0x20 else ~q6
        if LFSR_BITS >= 7:
            term &= q7 if state & 0x40 else ~q7
        if LFSR_BITS > 7:
            raise NotImplementedError("LFSR width over 7 bits currently not implemented")

        term = term.simplify()
        #print(term)
        q0 |= term

q0 = q0.simplify()
print("Need", len(q0.args), "terms after optimization.")
print(q0)