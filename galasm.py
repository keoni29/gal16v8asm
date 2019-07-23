# GAL16v8 assembler
# Author : Koen van Vliet
# 

import argparse
import os.path


nof_terms = 8 # Number of terms per macrocell OR gate
nof_outputs = 8 # Number of outputs/macrocells
nof_inputs = 8 # Number of NAND matrix inputs
ptd = [ [0]*nof_terms for _ in range(nof_outputs) ]

parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()
infilename = args.filename
outfilename = os.path.splitext(infilename)[0] + '.JED'

with open(infilename, 'r') as infile:
    with open(outfilename, 'w') as outfile:
        outfile.write(( "\x02JEDEC File*\n"
                        "N Number of fuses*\n"
                        "QF2194*\n"
                        "\n"
                        "N Set undefined fuses to 1 (blown/disconnected)*\n"
                        "F1*\n"
                        "\n"
                        "N Registered Mode using SYN=0,AC0=1*\n"
                        "L2192 01*\n"
                        "\n"
                        "N Active HIGH outputs using XOR=1*\n"
                        "2048 1111 1111*\n"
                        "\n"
                        "N Registered configuration for Registered mode using AC1=0*\n"
                        "L2120 0000 0000*\n"
                        "\n"
                        "N AND Matrix fuses*\n"))

        for linenumber, line in enumerate(infile.readlines(), 1):
            line = line.strip()

            eqn = line.split("#")[0]
            eqn = "".join(eqn.split())
            if not "=" in eqn:
                # This line does not contain an equation
                continue

            out, expr = eqn.split("=")
            if out[0] != 'q':
                print("Warning on Line", linenumber, ": Assignment to invalid symbol", out)
                continue
            
            output = int(out[1:])
            if 0 <= output < nof_outputs:
                pass
            else:
                print("Error on Line", linenumber, ": Output pin", output, "out of range")
                exit()

            print("OUTPUT",output, "=")
            for n,term in enumerate(expr.split('+')):
                for symbol in term.split("&"):
                    print(symbol)
                    c = symbol[0]
                    negate = False
                    
                    if c == '!':
                        c = symbol[1]
                        inpin = int(symbol[2:])
                        negate = True
                    else:
                        inpin = int(symbol[1:])

                    if not(c == 'i' or c == 'q'):
                        print("Warning on Line", linenumber, ": Invalid symbol ", symbol)
                        break

                    if 0 <= inpin < nof_inputs:
                        pass
                    else:
                        print("Error on Line", linenumber, ": Input pin", inpin, "out of range")
                        exit()

                    address = (output * nof_terms + n) * 32 + inpin * 4
                    if c == 'q':
                        address += 2
                    
                    if negate:
                        address += 1
                    s = "L" + str(address) + " 0*"
                    outfile.write(s + '\n')
                    print(s)

                else:
                    # Everything went OK, so enable the product term
                    ptd[output][n] = 1
                    continue
                break
        outfile.write(("\n"
                       "N Product term disable using PTD fuse*\n"
                       "L2128 "))
        for p in ptd:
            for f in p:
                outfile.write(str(f))
                print(f,end="")
        
        outfile.write("*\n"
                      "\n"
                      "N Invalid checksum*\n"
                      "C0000*\x030000")