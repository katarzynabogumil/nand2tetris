package parser

import (
	"assembler/code"
	"assembler/symbolTable"
	"bufio"
	"errors"
	"fmt"
	"os"
	"strconv"
	"strings"
)

type Parser struct {
	file              *os.File
	fileScanner       *bufio.Scanner
	symbolTable       *symbolTable.SymbolTable
	firstEmptyRegisty int64
	CurrentLineIdx    int64
}

type InstructionType string

const (
	AInstruction InstructionType = "A_INSTRUCTION"
	CInstruction InstructionType = "C_INSTRUCTION"
	LInstruction InstructionType = "L_INSTRUCTION"
)

var ErrInvalidInstructionLength = errors.New("instruction is too short")

// Creates a Parser and opens the source text file
func New(filename string, symbolTable *symbolTable.SymbolTable) (*Parser, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, fmt.Errorf("Can't open file %s: %w", filename, err)
	}

	fileScanner := bufio.NewScanner(file)

	fileScanner.Split(bufio.ScanLines)

	return &Parser{
		file:              file,
		fileScanner:       fileScanner,
		symbolTable:       symbolTable,
		firstEmptyRegisty: 16,
	}, nil
}

func (p *Parser) closeFile() error {
	err := p.file.Close()
	if err != nil {
		return fmt.Errorf("Can't close file: %w", err)
	}
	return nil
}

// Checks if there is more work to do (boolean)
func (p *Parser) HasMoreLines() bool {
	hasMorelines := p.fileScanner.Scan()

	if !hasMorelines {
		p.closeFile()
	}

	return hasMorelines
}

// Gets the current instruction (string)
func (p *Parser) GetCurrentLine() string {
	return p.fileScanner.Text()
}

// Parses the current instruction and returns the current instruction type, as a constant
func (p *Parser) InstructionType(str string) (InstructionType, error) {
	if len(str) < 1 {
		return AInstruction, ErrInvalidInstructionLength
	}

	switch string(str[0]) {
	case "@":
		return AInstruction, nil
	case "(":
		return LInstruction, nil
	default:
		return CInstruction, nil
	}
}

// Parses the current instruction and returns the instruction’s symbol (string)
// Used only if the current instruction is @ symbol or (symbol )
func (p *Parser) Symbol(str string) string {
	tempStr1 := strings.Replace(str, "@", "", 1)
	tempStr2 := strings.Replace(tempStr1, "(", "", 1)
	return strings.Replace(tempStr2, ")", "", 1)
}

// Updated API design, not acc. to project instructions - new methods:
// Parses comments
func (p *Parser) ParseComments(str string) string {
	tempStr := strings.Split(str, "//")
	return strings.TrimSpace(tempStr[0])
}

// Parses A instruction to binary code
func (p *Parser) ParseAInstruction(instruction string) (string, error) {
	addressStr := instruction[1:]

	address, err := strconv.ParseInt(addressStr, 10, 64)
	if err != nil {
		if !p.symbolTable.Contains(addressStr) {
			p.symbolTable.AddEntry(addressStr, p.firstEmptyRegisty)
			p.firstEmptyRegisty++
		}
		address, err = p.symbolTable.GetAddress(addressStr)
		if err != nil {
			return "", fmt.Errorf("failed to get address of symbol %s: %w", addressStr, err)
		}
	}

	parsedAddress := strconv.FormatInt(address, 2)

	for len(parsedAddress) < 15 {
		parsedAddress = "0" + parsedAddress
	}

	return "0" + parsedAddress + "\n", nil
}

// Parses C instruction to binary code
func (p *Parser) ParseCInstruction(instruction string) (string, error) {
	dest, comp, jump := p.parseCInstructionString(instruction)

	c := code.New()

	parsedComp, err := c.Comp(comp)
	if err != nil {
		return "", fmt.Errorf("%w, instruction: %s", err, instruction)
	}

	parsedDist, err := c.Dest(dest)
	if err != nil {
		return "", fmt.Errorf("%w, instruction: %s", err, instruction)
	}

	parsedJump, err := c.Jump(jump)
	if err != nil {
		return "", fmt.Errorf("%w, instruction: %s", err, instruction)
	}

	return "111" + parsedComp + parsedDist + parsedJump + "\n", nil
}

// Parses the current instruction and returns the instruction’s dest, comp and jump fields (string)
// Used only if the current instruction is dest =comp ; jump
func (p *Parser) parseCInstructionString(str string) (string, string, string) {
	var dest string
	var comp string
	var jump string

	if strings.Contains(str, "=") {
		tempStr := strings.Split(str, "=")
		dest = tempStr[0]
		comp = tempStr[1]
		jump = ""

		if strings.Contains(tempStr[1], ";") {
			tempStr2 := strings.Split(tempStr[1], ";")
			comp = tempStr2[0]
			jump = tempStr2[1]
		}
	} else {
		dest = ""
		comp = str
		jump = ""

		if strings.Contains(str, ";") {
			tempStr2 := strings.Split(str, ";")
			comp = tempStr2[0]
			jump = tempStr2[1]
		}
	}

	return dest, comp, jump
}
