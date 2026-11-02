# ==============================================================================
# Makefile for PecasBot Enterprise Platform
# Standard DevOps & Engineering Quality Commands
# ==============================================================================

.PHONY: help check test lint format typecheck run docker-up docker-down backup seed hooks

PYTHON ?= .venv/bin/python3

help:
	@echo "Comandos disponíveis no PecasBot Enterprise:"
	@echo "  make check      - Roda todo o Quality Gate (Lint, Mypy, Pytest, Backup)"
	@echo "  make test       - Roda a suite de testes automatizados"
	@echo "  make lint       - Executa análise estática de código com Ruff"
	@echo "  make format     - Formata o código com Ruff"
	@echo "  make typecheck  - Executa verificação de tipos com Mypy"
	@echo "  make run        - Inicia o servidor FastAPI localmente na porta 8000"
	@echo "  make backup     - Executa backup a quente do banco de dados com compressão"
	@echo "  make seed       - Popula dados de demonstração (pedidos, logs, perfil)"
	@echo "  make hooks      - Instala o Git Pre-Commit Hook local"
	@echo "  make docker-up  - Sobe todos os containers (API, Evolution, Postgres, Redis)"
	@echo "  make docker-down- Para e desce todos os containers"

check:
	@./scripts/quality_gate.sh

test:
	@$(PYTHON) -m pytest tests/ -v

lint:
	@$(PYTHON) -m ruff check .

format:
	@$(PYTHON) -m ruff format .

typecheck:
	@$(PYTHON) -m mypy --config-file pyproject.toml domain application infrastructure presentation

run:
	@$(PYTHON) -m uvicorn presentation.api:app --host 0.0.0.0 --port 8000 --reload

backup:
	@$(PYTHON) scripts/backup_database.py

seed:
	@$(PYTHON) scripts/seed_demo_data.py

hooks:
	@./scripts/setup_git_hooks.sh

docker-up:
	@docker compose up -d

docker-down:
	@docker compose down
