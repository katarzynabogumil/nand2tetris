package main

import (
	"fmt"
	"os"
)

func main() {
	if len(os.Args) < 3 {
		fmt.Println("Missing arguments, please provide input and output file names")
		return
	}

	assembler := NewAssembler(os.Args[1])

	err := assembler.ScanForLabels()
	if err != nil {
		panic(err)
	}

	err = assembler.Parse()
	if err != nil {
		panic(err)
	}

	err = assembler.WriteToFile(os.Args[2])
	if err != nil {
		panic(err)
	}
}
