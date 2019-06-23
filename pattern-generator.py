import boolean

UART_BITS = 10 # 1 start, 8 data, 1 stop bit
LFSR_BITS = 7 # Width of the linear feedback shift register
startbit = '0'
stopbit = '1'

string = "Hello World\n"
minstates = len(string) * UART_BITS
print("String requires", minstates, "states.")

states = (2 ** LFSR_BITS) - 1
print("LFSR can encode", states, "states.")

if minstates > states:
    raise BaseException("Too many states required. Need higher LFSR_BITS")

# Convert the string to a pattern of bits
pattern = ''.join([startbit + ("{0:b}".format(ord(c)).rjust(8, '0')) + stopbit for c in string])

# Pad the pattern with idle states
pattern = pattern.rjust(states,'1')

print("Pattern :", pattern)

#TODO if all zeroes, insert a one!

uniquestates = list()
sr = 1
for n,i in enumerate(range(256)):

    # Shift the register
    sr_first_bit = sr & 0x01
    sr_last_bit = (sr >> (LFSR_BITS - 1)) & 0x01
    sr = (sr << 1) | (sr_last_bit ^ sr_first_bit)
    sr &= 0x7F

    if sr not in uniquestates:
        uniquestates.append(sr)
    else:
        break
    #print(n,sr)
print("LFSR produces sequence of", len(uniquestates),"unique states")
if states != len(uniquestates):
    raise BaseException("Bug: LFSR produces unexpected number of unique states")

algebra = boolean.BooleanAlgebra()
q0, q1, q2, q3, q4, q5, q6, q7 = algebra.symbols('a','b','c','d','e','f','g', 'h')

q0 = algebra.parse('FALSE')
for state, output in zip(uniquestates, pattern):
    print(str(state).rjust(4),output)
    if (output == '1'):
        term = q1 if state & 0x01 else ~q1
        term &= q2 if state & 0x02 else ~q2
        term &= q3 if state & 0x04 else ~q3
        term &= q4 if state & 0x08 else ~q4
        term &= q5 if state & 0x10 else ~q5
        term &= q6 if state & 0x20 else ~q6
        term &= q7 if state & 0x40 else ~q7
        term = term.simplify()
        print(term)
        q0 |= term
        #q0 = q0.simplify()
        #print("New q0", q0)
q0 = q0.simplify()
print("Need", len(q0.args), "terms after optimization.")
print(q0)