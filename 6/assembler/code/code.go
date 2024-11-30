package code

import (
	"errors"
	"strings"
)

// Deals only with C-instructions: dest = comp ; jump
type Code struct{}

var (
	ErrInvalidDest = errors.New("invalid dest instruction")
	ErrInvalidComp = errors.New("invalid comp instruction")
	ErrInvalidJump = errors.New("invalid jump instruction")
)

func New() *Code {
	return &Code{}
}

// Returns the binary representation of the parsed dest field (string)
func (c *Code) Dest(str string) (string, error) {
	destMap := map[string]string{
		"":    "000",
		"M":   "001",
		"D":   "010",
		"DM":  "011",
		"MD":  "011", // due to known bug in project description
		"A":   "100",
		"AM":  "101",
		"AD":  "110",
		"ADM": "111",
		"AMD": "111", // due to known bug in project description
	}

	if destMap[str] == "" {
		return "", ErrInvalidDest
	}

	return destMap[str], nil
}

// Returns the binary representation of the parsed comp field (string)
func (c *Code) Comp(str string) (string, error) {
	var a string
	if strings.Contains(str, "M") {
		a = "1"
	} else {
		a = "0"
	}

	strWithoutM := strings.Replace(str, "M", "A", 1)

	compMap := map[string]string{
		"0":   "101010",
		"1":   "111111",
		"-1":  "111010",
		"D":   "001100",
		"A":   "110000",
		"!D":  "001101",
		"!A":  "110001",
		"-D":  "001111",
		"-A":  "110011",
		"D+1": "011111",
		"A+1": "110111",
		"D-1": "001110",
		"A-1": "110010",
		"D+A": "000010",
		"D-A": "010011",
		"A-D": "000111",
		"D&A": "000000",
		"D|A": "010101",
	}

	if compMap[strWithoutM] == "" {
		return "", ErrInvalidComp
	}

	return a + compMap[strWithoutM], nil
}

// Returns the binary representation of the parsed jump field (string)
func (c *Code) Jump(str string) (string, error) {
	jumpMap := map[string]string{
		"":    "000",
		"JGT": "001",
		"JEQ": "010",
		"JGE": "011",
		"JLT": "100",
		"JNE": "101",
		"JLE": "110",
		"JMP": "111",
	}

	if jumpMap[str] == "" {
		return "", ErrInvalidJump
	}

	return jumpMap[str], nil
}
