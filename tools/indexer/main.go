// Package main provides a code indexer that generates symbols.json, imports.json,
// and packages.json for the AI agent context store.
//
// Usage:
//
//	go run tools/indexer/main.go -dir ./internal -out .ai-agents/index/
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"os"
	"path/filepath"
	"strings"
)

// Symbol represents a Go symbol (function, type, interface, method).
type Symbol struct {
	Name      string   `json:"name"`
	Kind      string   `json:"kind"` // func, type, interface, method, const, var
	Package   string   `json:"package"`
	File      string   `json:"file"`
	Line      int      `json:"line"`
	Exported  bool     `json:"exported"`
	Methods   []string `json:"methods,omitempty"`   // for types
	Fields    []string `json:"fields,omitempty"`    // for structs
	Signature string   `json:"signature,omitempty"` // for funcs
}

// ImportInfo represents import relationships for a file.
type ImportInfo struct {
	File    string   `json:"file"`
	Package string   `json:"package"`
	Imports []string `json:"imports"`
}

// PackageInfo represents a package summary.
type PackageInfo struct {
	Name       string   `json:"name"`
	Path       string   `json:"path"`
	Files      []string `json:"files"`
	Types      int      `json:"types"`
	Functions  int      `json:"functions"`
	Interfaces int      `json:"interfaces"`
}

func main() {
	dir := flag.String("dir", ".", "Root directory to scan")
	out := flag.String("out", ".ai-agents/index", "Output directory for index files")
	flag.Parse()

	absDir, err := filepath.Abs(*dir)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error resolving dir: %v\n", err)
		os.Exit(1)
	}

	if err := os.MkdirAll(*out, 0o755); err != nil {
		fmt.Fprintf(os.Stderr, "error creating output dir: %v\n", err)
		os.Exit(1)
	}

	var symbols []Symbol
	var imports []ImportInfo
	pkgMap := make(map[string]*PackageInfo)

	fset := token.NewFileSet()

	err = filepath.Walk(absDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		// Skip vendor, testdata, hidden dirs, and non-Go files.
		if info.IsDir() {
			base := filepath.Base(path)
			if base == "vendor" || base == "testdata" || strings.HasPrefix(base, ".") {
				return filepath.SkipDir
			}
			return nil
		}

		if !strings.HasSuffix(path, ".go") || strings.HasSuffix(path, "_test.go") {
			return nil
		}

		relPath, _ := filepath.Rel(absDir, path)

		f, parseErr := parser.ParseFile(fset, path, nil, parser.ParseComments)
		if parseErr != nil {
			fmt.Fprintf(os.Stderr, "warning: skipping %s: %v\n", relPath, parseErr)
			return nil
		}

		pkgName := f.Name.Name
		pkgDir := filepath.Dir(relPath)

		// Track package info.
		if _, ok := pkgMap[pkgDir]; !ok {
			pkgMap[pkgDir] = &PackageInfo{
				Name: pkgName,
				Path: pkgDir,
			}
		}
		pkgMap[pkgDir].Files = append(pkgMap[pkgDir].Files, relPath)

		// Extract imports.
		var fileImports []string
		for _, imp := range f.Imports {
			impPath := strings.Trim(imp.Path.Value, `"`)
			fileImports = append(fileImports, impPath)
		}
		if len(fileImports) > 0 {
			imports = append(imports, ImportInfo{
				File:    relPath,
				Package: pkgName,
				Imports: fileImports,
			})
		}

		// Extract symbols.
		for _, decl := range f.Decls {
			switch d := decl.(type) {
			case *ast.FuncDecl:
				sym := Symbol{
					Name:     d.Name.Name,
					Package:  pkgName,
					File:     relPath,
					Line:     fset.Position(d.Pos()).Line,
					Exported: d.Name.IsExported(),
				}
				if d.Recv != nil && len(d.Recv.List) > 0 {
					sym.Kind = "method"
					sym.Signature = formatRecv(d.Recv.List[0].Type) + "." + d.Name.Name
				} else {
					sym.Kind = "func"
					sym.Signature = d.Name.Name
				}
				symbols = append(symbols, sym)
				pkgMap[pkgDir].Functions++

			case *ast.GenDecl:
				for _, spec := range d.Specs {
					switch s := spec.(type) {
					case *ast.TypeSpec:
						sym := Symbol{
							Name:     s.Name.Name,
							Package:  pkgName,
							File:     relPath,
							Line:     fset.Position(s.Pos()).Line,
							Exported: s.Name.IsExported(),
						}
						switch t := s.Type.(type) {
						case *ast.InterfaceType:
							sym.Kind = "interface"
							sym.Methods = extractFieldNames(t.Methods)
							pkgMap[pkgDir].Interfaces++
						case *ast.StructType:
							sym.Kind = "struct"
							sym.Fields = extractFieldNames(t.Fields)
							pkgMap[pkgDir].Types++
						default:
							sym.Kind = "type"
							pkgMap[pkgDir].Types++
						}
						symbols = append(symbols, sym)

					case *ast.ValueSpec:
						for _, name := range s.Names {
							kind := "var"
							if d.Tok == token.CONST {
								kind = "const"
							}
							symbols = append(symbols, Symbol{
								Name:     name.Name,
								Kind:     kind,
								Package:  pkgName,
								File:     relPath,
								Line:     fset.Position(name.Pos()).Line,
								Exported: name.IsExported(),
							})
						}
					}
				}
			}
		}

		return nil
	})

	if err != nil {
		fmt.Fprintf(os.Stderr, "error walking directory: %v\n", err)
		os.Exit(1)
	}

	// Convert pkgMap to slice.
	var packages []PackageInfo
	for _, pkg := range pkgMap {
		packages = append(packages, *pkg)
	}

	// Write output files.
	writeJSON(filepath.Join(*out, "symbols.json"), symbols)
	writeJSON(filepath.Join(*out, "imports.json"), imports)
	writeJSON(filepath.Join(*out, "packages.json"), packages)

	fmt.Printf("Index generated: %d symbols, %d import entries, %d packages\n",
		len(symbols), len(imports), len(packages))
}

func writeJSON(path string, v interface{}) {
	data, err := json.MarshalIndent(v, "", "  ")
	if err != nil {
		fmt.Fprintf(os.Stderr, "error marshaling %s: %v\n", path, err)
		os.Exit(1)
	}
	if err := os.WriteFile(path, data, 0o644); err != nil {
		fmt.Fprintf(os.Stderr, "error writing %s: %v\n", path, err)
		os.Exit(1)
	}
}

func formatRecv(expr ast.Expr) string {
	switch t := expr.(type) {
	case *ast.StarExpr:
		if ident, ok := t.X.(*ast.Ident); ok {
			return "*" + ident.Name
		}
	case *ast.Ident:
		return t.Name
	}
	return "?"
}

func extractFieldNames(fields *ast.FieldList) []string {
	if fields == nil {
		return nil
	}
	var names []string
	for _, f := range fields.List {
		for _, name := range f.Names {
			names = append(names, name.Name)
		}
		// Embedded fields (no name).
		if len(f.Names) == 0 {
			names = append(names, formatRecv(f.Type))
		}
	}
	return names
}
