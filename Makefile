# ==============================================================================
# Makefile for PecasBot Enterprise Platform
# Standard DevOps & Engineering Quality Commands
# ==============================================================================

.PHONY: help check test lint format typecheck run docker-up docker-down backup seed hooks ts-typecheck ts-lint ts-test sonar

PYTHON ?= .venv/bin/python3
NODE_BIN_DIR := $(dir $(shell which npm 2>/dev/null || ls -d $(HOME)/.nvm/versions/node/v*/bin/npm 2>/dev/null | sort -V | tail -n 1))
export PATH := $(NODE_BIN_DIR):$(PATH)

help:
	@echo "Comandos disponíveis no PecasBot Enterprise:"
	@echo "  make check        - Roda todo o Quality Gate (Python + TypeScript + Backup)"
	@echo "  make test         - Roda a suite de testes automatizados (Pytest)"
	@echo "  make sonar        - Gera cobertura e executa scanner SonarQube"
	@echo "  make lint         - Executa análise estática Python com Ruff"
	@echo "  make format       - Formata o código Python com Ruff"
	@echo "  make typecheck    - Executa verificação de tipos Python com Mypy"
	@echo "  make ts-typecheck - Executa checagem de tipos TypeScript (tsc)"
	@echo "  make ts-lint      - Executa linter de boas práticas Front-End (ESLint)"
	@echo "  make ts-test      - Executa testes unitários de interface (Vitest)"
	@echo "  make run          - Inicia o servidor FastAPI localmente na porta 8000"
	@echo "  make backup       - Executa backup a quente do banco de dados com compressão"
	@echo "  make seed         - Popula dados de demonstração (pedidos, logs, perfil)"
	@echo "  make hooks        - Instala o Git Pre-Commit Hook local"
	@echo "  make docker-up    - Sobe todos os containers (API, Evolution, Postgres, Redis)"
	@echo "  make docker-down  - Para e desce todos os containers"

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

ts-typecheck:
	@npm run typecheck

ts-lint:
	@npm run lint

ts-test:
	@npm run test

sonar:
	@$(PYTHON) -m pytest tests/ --cov=domain --cov=application --cov=infrastructure --cov=presentation --cov-report=xml:coverage.xml
	@if command -v sonar-scanner >/dev/null 2>&1; then \
		sonar-scanner; \
	else \
		echo "sonar-scanner CLI não encontrado localmente. No GitHub Actions, ele roda automaticamente com o SonarSource/sonarqube-scan-action."; \
	fi


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
