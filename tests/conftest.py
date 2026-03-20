import pytest
from unittest.mock import MagicMock
from src.poc.app import create_app


@pytest.fixture()
def app():
    app = create_app()

    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_result.inserted_id = "507f1f77bcf86cd799439011"
    mock_db["devices"].insert_one.return_value = mock_result
    app.db = mock_db
    app.testing = True

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
