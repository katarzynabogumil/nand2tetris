package main

import (
	"assembler/parser"
	"assembler/symbolTable"
	"errors"
	"fmt"
	"os"
)

type Assembler struct {
	symbolTable   *symbolTable.SymbolTable
	inputFileName string
	parsedData    string
}

func NewAssembler(inputFileName string) *Assembler {
	return &Assembler{
		inputFileName: inputFileName,
		symbolTable:   symbolTable.New(),
	}
}

// Helper function to make a new parser and traverse the file
func (a *Assembler) traverseFile(iterator func(p *parser.Parser, inst string, instType parser.InstructionType) error) error {
	p, err := parser.New(a.inputFileName, a.symbolTable)
	if err != nil {
		return fmt.Errorf("failed to initialize parser: %w", err)
	}

	for p.HasMoreLines() {
		line := p.GetCurrentLine()
		instruction := p.ParseComments(line)
		if len(instruction) == 0 {
			continue
		}

		instructionType, err := p.InstructionType(instruction)
		if err != nil {
			return fmt.Errorf("failed to parse instruction type: %w", err)
		}

		err = iterator(p, instruction, instructionType)
		if err != nil {
			return fmt.Errorf("failed to handle line: %w", err)
		}

		p.CurrentLineIdx++
	}

	return nil
}

// Runs first pass scanning for unknown labels
func (a *Assembler) ScanForLabels() error {
	err := a.traverseFile(a.scanLine)
	if err != nil {
		return fmt.Errorf("failed to scan file for labels: %w", err)
	}

	return nil
}

// Scan parsed line for unknown labels
func (a *Assembler) scanLine(p *parser.Parser, instruction string, instructionType parser.InstructionType) error {
	switch instructionType {
	case parser.LInstruction:
		p.CurrentLineIdx-- // don't count labels as instruction lines
		symbol := p.Symbol(instruction)
		if !a.symbolTable.Contains(symbol) {
			a.symbolTable.AddEntry(symbol, p.CurrentLineIdx+1)
		}
	}
	return nil
}

// Runs second pass to parse assembly code
func (a *Assembler) Parse() error {
	err := a.traverseFile(a.parseLine)
	if err != nil {
		return fmt.Errorf("failed to parse file: %w", err)
	}

	return nil
}

// Parse line of assembly code
func (a *Assembler) parseLine(p *parser.Parser, instruction string, instructionType parser.InstructionType) error {
	var parsedLine string
	var err error

	switch instructionType {
	case parser.AInstruction:
		parsedLine, err = p.ParseAInstruction(instruction)
		if err != nil {
			return fmt.Errorf("failed to parse A instruction: %w", err)
		}

	case parser.CInstruction:
		parsedLine, err = p.ParseCInstruction(instruction)
		if err != nil {
			return fmt.Errorf("failed to parse C instruction: %w", err)
		}
	}

	a.parsedData += parsedLine

	return nil
}

// Writes provided data to a file and prints out written data
func (a *Assembler) WriteToFile(outputFileName string) error {
	f, err := os.Create(outputFileName)
	if err != nil {
		return errors.New(fmt.Sprintf("Can't create to file: %s", outputFileName))
	}

	defer f.Close()

	_, err = f.WriteString(a.parsedData)
	if err != nil {
		return errors.New(fmt.Sprintf("Can't write to file: %s", outputFileName))
	}

	fmt.Printf("Following data has been written to file %s: ", outputFileName)
	fmt.Println(a.parsedData)

	return nil
}
