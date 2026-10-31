"""
Pytest configuration and fixtures.
"""

import os

import pytest

from application.use_cases.process_incoming_message import ProcessIncomingMessageUseCase
from infrastructure.gateways.evolution_gateway import EvolutionGateway
from infrastructure.repositories.memory_product_repository import MemoryProductRepository
from infrastructure.repositories.sqlite_repository import SqliteRepository
from infrastructure.services.agent_service import AIAgentService

TEST_DB_PATH = "data/test_pecasbot.db"


@pytest.fixture
async def test_sqlite():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    repo = SqliteRepository(TEST_DB_PATH)
    await repo.init_db()
    yield repo
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture
def mock_gateway(test_sqlite):
    return EvolutionGateway(message_recorder=test_sqlite.record_sent_message)


@pytest.fixture
def product_repo():
    return MemoryProductRepository()


@pytest.fixture
def ai_service():
    return AIAgentService()


@pytest.fixture
def use_case(test_sqlite, product_repo, mock_gateway, ai_service):
    return ProcessIncomingMessageUseCase(
        conversation_repo=test_sqlite,
        product_repo=product_repo,
        order_repo=test_sqlite,
        messaging_gateway=mock_gateway,
        ai_service=ai_service,
        sqlite_repo=test_sqlite
    )
