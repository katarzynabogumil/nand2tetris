// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

(CLEAR)
@SCREEN
D=A
@addr
M=D // addr = screen's base

(CLEARLOOP)
@KBD
D=M
@BLACK
D;JNE // if @KBD != 0 goto BLACK

@addr
A=M
M=0 // clear the pixel

@addr
M=M+1 // addr++

@addr
D=M
@KBD
D=D-A
@CLEAR
D;JEQ // if addr == KBD goto CLEAR

@CLEARLOOP
0;JMP

(BLACK)
@SCREEN
D=A
@addr
M=D // addr = screen's base

(BLACKLOOP)
@KBD
D=M
@CLEAR
D;JEQ // if @KBD != 0 goto CLEAR

@addr
A=M
M=-1 // blacken the pixel

@addr
M=M+1 // addr++

@addr
D=M
@KBD
D=D-A
@BLACK
D;JEQ // if addr == KBD goto BLACK

@BLACKLOOP
0;JMP
