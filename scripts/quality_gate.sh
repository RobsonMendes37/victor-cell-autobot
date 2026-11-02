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

# 1. Barreira 1: Linting e Análise de Estilo (Ruff)
echo -e "\n${YELLOW}[Passo 1/4] Executando Análise Estática de Código (Ruff)...${NC}"
$PYTHON_BIN -m ruff check .
echo -e "${GREEN}✓ Linting 100% aprovado sem violações de estilo.${NC}"

# 2. Barreira 2: Checagem Estática de Tipagem (Mypy)
echo -e "\n${YELLOW}[Passo 2/4] Executando Verificação Estrita de Tipos (Mypy)...${NC}"
$PYTHON_BIN -m mypy --config-file pyproject.toml domain application infrastructure presentation
echo -e "${GREEN}✓ Tipagem estática 100% aprovada em todos os módulos.${NC}"

# 3. Barreira 3: Suite Completa de Testes Automatizados (Pytest)
echo -e "\n${YELLOW}[Passo 3/4] Executando Testes Unitários e de Integração (Pytest)...${NC}"
$PYTHON_BIN -m pytest tests/ -q
echo -e "${GREEN}✓ Todos os testes automatizados passaram com sucesso.${NC}"

# 4. Barreira 4: Verificação de Backup e Integridade de Dados
echo -e "\n${YELLOW}[Passo 4/4] Validando Rotina de Backup a Quente de Banco...${NC}"
$PYTHON_BIN scripts/backup_database.py
echo -e "${GREEN}✓ Rotina de backup e segurança de dados operacional.${NC}"

echo -e "\n${GREEN}======================================================${NC}"
echo -e "${GREEN}   QUALITY GATE 100% APROVADO - PRONTO PARA PRODUÇÃO  ${NC}"
echo -e "${GREEN}======================================================${NC}"
