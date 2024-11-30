package symbolTable

import "errors"

type SymbolTable map[string]int64

var ErrSymbol = errors.New("symbol not found")

func New() *SymbolTable {
	return &SymbolTable{
		"R0":     0,
		"R1":     1,
		"R2":     2,
		"R3":     3,
		"R4":     4,
		"R5":     5,
		"R6":     6,
		"R7":     7,
		"R8":     8,
		"R9":     9,
		"R10":    10,
		"R11":    11,
		"R12":    12,
		"R13":    13,
		"R14":    14,
		"R15":    15,
		"SCREEN": 16384,
		"KBD":    24576,
		"SP":     0,
		"LCL":    1,
		"ARG":    2,
		"THIS":   3,
		"THAT":   4,
	}
}

// Adds <symbol, address> to the table
func (st *SymbolTable) AddEntry(symbol string, address int64) {
	(*st)[symbol] = address
}

// Checks if symbol exists in the table
func (st *SymbolTable) Contains(symbol string) bool {
	for k := range *st {
		if k == symbol {
			return true
		}
	}
	return false
}

// Returns the address associated with symbol
func (st *SymbolTable) GetAddress(symbol string) (int64, error) {
	if !st.Contains(symbol) {
		return 0, ErrSymbol
	}
	return (*st)[symbol], nil
}
