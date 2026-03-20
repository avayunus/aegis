.PHONY: setup backend frontend test lint clean

# ──────────────────────────────────────────────
# AEGIS Development Commands
# ──────────────────────────────────────────────

# First-time setup: installs everything
setup:
	@echo "══════════════════════════════════════"
	@echo "  AEGIS — Setting up dev environment"
	@echo "══════════════════════════════════════"
	cd backend && python3 -m venv .venv && \
		. .venv/bin/activate && \
		pip install --upgrade pip && \
		pip install -e ".[dev]"
	cd frontend && pnpm install
	@echo ""
	@echo "✓ Setup complete. Run 'make backend' and 'make frontend' in separate terminals."

# Start the backend (FastAPI with hot reload)
backend:
	cd backend && . .venv/bin/activate && \
		uvicorn src.aegis.main:app --reload --host 0.0.0.0 --port 8000

# Start the frontend (Vite dev server)
frontend:
	cd frontend && pnpm dev

# Run all tests
test:
	cd backend && . .venv/bin/activate && pytest -v

# Run backend tests with coverage
test-cov:
	cd backend && . .venv/bin/activate && pytest --cov=src/aegis --cov-report=html -v

# Lint and format
lint:
	cd backend && . .venv/bin/activate && ruff check src/ tests/ && ruff format --check src/ tests/
	cd frontend && pnpm lint

# Format code
format:
	cd backend && . .venv/bin/activate && ruff format src/ tests/
	cd frontend && pnpm format

# Clean generated files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/.venv frontend/node_modules frontend/dist
	rm -f *.db

# Show project status
status:
	@echo "Backend deps:"
	@cd backend && . .venv/bin/activate && pip list --format=columns 2>/dev/null | head -20 || echo "  (not set up yet)"
	@echo ""
	@echo "Frontend deps:"
	@cd frontend && pnpm list --depth=0 2>/dev/null || echo "  (not set up yet)"
