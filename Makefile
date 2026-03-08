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

.PHONY: index

BIN_DIR := $(CURDIR)/bin
INDEXER_OUT_DIR := $(CURDIR)/.ai-agents/index

# Indexing
# ======================================================================================================================
index:
	@echo "--> Running indexer..."
	@mkdir -p $(INDEXER_OUT_DIR)
	@go run $(CURDIR)/tools/indexer/main.go -dir $(CURDIR) -out $(INDEXER_OUT_DIR)

.PHONY: help
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  index                            - Run the indexer to generate AI agent context."
	@echo "  help                             - Show this help message."
