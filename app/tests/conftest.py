import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from app.main import app
from app.DataBase.main import get_session

# Mock objects for testing
mock_session = Mock()
mock_user_service = Mock()

# Override dependency
def get_mock_session():
    yield mock_session

app.dependency_overrides[get_session] = get_mock_session

@pytest.fixture
def fake_session():
    return mock_session

@pytest.fixture
def fake_user_service():
    return mock_user_service

@pytest.fixture
def test_client():
    return TestClient(app)
