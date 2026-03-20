#!/usr/bin/env bash
# ──────────────────────────────────────────────────────
# AEGIS — One-command development environment setup
# Run from the project root:  bash scripts/setup.sh
# ──────────────────────────────────────────────────────

set -euo pipefail

YELLOW='\033[1;33m'
GREEN='\033[1;32m'
BLUE='\033[1;34m'
NC='\033[0m'

echo -e "${BLUE}══════════════════════════════════════${NC}"
echo -e "${BLUE}  AEGIS — Setting up dev environment  ${NC}"
echo -e "${BLUE}══════════════════════════════════════${NC}"
echo ""

# ── Check prerequisites ─────────────────────────────
echo -e "${YELLOW}[1/5] Checking prerequisites...${NC}"

command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not found. Install Python 3.11+"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "ERROR: node not found. Install Node.js 20+"; exit 1; }
command -v pnpm >/dev/null 2>&1 || { echo "ERROR: pnpm not found. Run: npm install -g pnpm"; exit 1; }

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
NODE_VERSION=$(node --version)
echo "  Python: $PYTHON_VERSION"
echo "  Node:   $NODE_VERSION"
echo "  pnpm:   $(pnpm --version)"
echo ""

# ── Backend setup ────────────────────────────────────
echo -e "${YELLOW}[2/5] Setting up Python backend...${NC}"

cd backend

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "  Created virtual environment"
fi

source .venv/bin/activate
pip install --upgrade pip -q
pip install -e ".[dev]" -q
echo "  Installed backend dependencies"

cd ..
echo ""

# ── Frontend setup ───────────────────────────────────
echo -e "${YELLOW}[3/5] Setting up React frontend...${NC}"

cd frontend
pnpm install --silent
cd ..
echo "  Installed frontend dependencies"
echo ""

# ── Environment file ─────────────────────────────────
echo -e "${YELLOW}[4/5] Checking environment config...${NC}"

if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env 2>/dev/null || true
    echo "  Created backend/.env from template"
else
    echo "  backend/.env already exists"
fi
echo ""

# ── Verify ───────────────────────────────────────────
echo -e "${YELLOW}[5/5] Running verification...${NC}"

cd backend
source .venv/bin/activate
python3 -c "import fastapi; import sqlalchemy; print('  Backend imports OK')"
cd ..

echo ""
echo -e "${GREEN}══════════════════════════════════════${NC}"
echo -e "${GREEN}  Setup complete!                     ${NC}"
echo -e "${GREEN}══════════════════════════════════════${NC}"
echo ""
echo "  Start the backend:"
echo "    cd backend && source .venv/bin/activate"
echo "    uvicorn src.aegis.main:app --reload"
echo ""
echo "  Start the frontend (new terminal):"
echo "    cd frontend && pnpm dev"
echo ""
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "  API docs: http://localhost:8000/docs"
