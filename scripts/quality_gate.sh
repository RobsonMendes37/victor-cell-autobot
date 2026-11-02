#!/usr/bin/env bash
# ==============================================================================
# Quality Gate Script for PecasBot Enterprise Platform
# Standard: Google & VTEX CI/CD Quality Barriers
# Runs: Ruff Linter -> Mypy Static Typing -> Pytest Suite -> Backup Test
# ==============================================================================

set -eo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}   PecasBot Enterprise Quality Gate & CI/CD Verifier  ${NC}"
echo -e "${BLUE}======================================================${NC}"

# Detect Python Environment
PYTHON_BIN=".venv/bin/python3"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

# Detect Node.js & NPM Environment (incluindo NVM)
if ! command -v npm &> /dev/null; then
    if [ -d "$HOME/.nvm/versions/node" ]; then
        LATEST_NODE=$(ls -d $HOME/.nvm/versions/node/v* 2>/dev/null | sort -V | tail -n 1)
        if [ -n "$LATEST_NODE" ] && [ -d "$LATEST_NODE/bin" ]; then
            export PATH="$LATEST_NODE/bin:$PATH"
        fi
    fi
fi

# 1. Barreira 1: Linting e Análise de Estilo Python (Ruff)
echo -e "\n${YELLOW}[Passo 1/7] Executando Análise Estática de Código Python (Ruff)...${NC}"
$PYTHON_BIN -m ruff check .
echo -e "${GREEN}✓ Linting Python 100% aprovado sem violações de estilo.${NC}"

# 2. Barreira 2: Checagem Estática de Tipagem Python (Mypy)
echo -e "\n${YELLOW}[Passo 2/7] Executando Verificação Estrita de Tipos Python (Mypy)...${NC}"
$PYTHON_BIN -m mypy --config-file pyproject.toml domain application infrastructure presentation
echo -e "${GREEN}✓ Tipagem estática Python 100% aprovada.${NC}"

# 3. Barreira 3: Suite Completa de Testes Automatizados Python (Pytest)
echo -e "\n${YELLOW}[Passo 3/7] Executando Testes Unitários e de Integração Python (Pytest)...${NC}"
$PYTHON_BIN -m pytest tests/ -q
echo -e "${GREEN}✓ Todos os testes Python passaram com sucesso.${NC}"

# 4. Barreira 4: Checagem Estática de Tipagem Front-End (TypeScript tsc)
echo -e "\n${YELLOW}[Passo 4/7] Executando Checagem Estrita de Tipagem Front-End (TypeScript)...${NC}"
npm run typecheck
echo -e "${GREEN}✓ Tipagem estática TypeScript 100% aprovada sem erros.${NC}"

# 5. Barreira 5: Linting e Boas Práticas Front-End (ESLint)
echo -e "\n${YELLOW}[Passo 5/7] Executando Análise de Qualidade Front-End (ESLint)...${NC}"
npm run lint
echo -e "${GREEN}✓ ESLint 100% aprovado nos módulos TypeScript.${NC}"

# 6. Barreira 6: Testes Unitários de Interface e Multi-Tenant (Vitest)
echo -e "\n${YELLOW}[Passo 6/7] Executando Testes Automatizados de Front-End (Vitest)...${NC}"
npm run test
echo -e "${GREEN}✓ Todos os testes unitários de interface e serviços passaram.${NC}"

# 7. Barreira 7: Verificação de Backup e Integridade de Dados
echo -e "\n${YELLOW}[Passo 7/7] Validando Rotina de Backup a Quente de Banco...${NC}"
$PYTHON_BIN scripts/backup_database.py
echo -e "${GREEN}✓ Rotina de backup e segurança de dados operacional.${NC}"

echo -e "\n${GREEN}======================================================${NC}"
echo -e "${GREEN}   QUALITY GATE 100% APROVADO - PRONTO PARA COMMIT/CI ${NC}"
echo -e "${GREEN}======================================================${NC}"

