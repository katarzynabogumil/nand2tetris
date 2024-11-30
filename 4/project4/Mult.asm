// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

@i
M=0
@R2
M=0

(LOOP)
// if i == RAM[0] goto END
@i
D=M
@R0
D=D-M
@END
D;JEQ

// RAM[2] = RAM[2] + RAM[1]
@R1
D=M
@R2
M=D+M

// i++
@i
M=M+1

@LOOP
0;JMP

(END)
@END
0;JMP