.PHONY: update-index lint security-scan test test-race test-integration test-coverage help

# ============================================================
# AI Agent Tools
# ============================================================

## Update code index for AI agents (symbols, imports, packages)
update-index:
	@echo "Updating code index..."
	@go run tools/indexer/main.go -dir . -out .ai-agents/index/
	@echo "Done."

# ============================================================
# Code Quality
# ============================================================

## Run all linters
lint:
	golangci-lint run ./...

## Run security scanners
security-scan:
	gosec ./...
	govulncheck ./...

## Run all quality checks
check: lint security-scan test-race
	@echo "All checks passed."

# ============================================================
# Testing
# ============================================================

## Run unit tests
test:
	go test ./...

## Run unit tests with race detector
test-race:
	go test -race ./...

## Run integration tests
test-integration:
	go test -tags=integration ./tests/integration/...

## Run tests with coverage report
test-coverage:
	go test -coverprofile=coverage.out ./...
	go tool cover -func=coverage.out
	@echo ""
	@echo "Coverage report: coverage.out"
	@echo "HTML report: go tool cover -html=coverage.out"

# ============================================================
# Build
# ============================================================

## Build the application
build:
	go build -o bin/api ./cmd/api/

## Build and verify
verify: build
	go vet ./...

# ============================================================
# Development
# ============================================================

## Run the application
run:
	go run ./cmd/api/

## Clean build artifacts
clean:
	rm -rf bin/ coverage.out

# ============================================================
# Help
# ============================================================

## Show this help
help:
	@echo "Available targets:"
	@echo ""
	@grep -E '^## ' Makefile | sed 's/^## /  /'
	@echo ""
	@echo "AI Agent commands:"
	@echo "  make update-index    - Update code index for AI agents"
	@echo "  make check           - Run all quality checks (lint + security + test)"
	@echo ""
	@echo "Testing:"
	@echo "  make test            - Run unit tests"
	@echo "  make test-race       - Run tests with race detector"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-coverage   - Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            - Run golangci-lint"
	@echo "  make security-scan   - Run gosec + govulncheck"
