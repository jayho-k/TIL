import pytest
from unittest.mock import AsyncMock
from app.main import container
from app.models.user import User

@pytest.mark.asyncio
async def test_create_user(client):
    # Mock Service Layer (or Repository Layer)
    mock_service = AsyncMock()
    mock_service.create_new_user.return_value = User(id=1, email="test@example.com", is_active=1)

    with container.user_service.override(mock_service):
        response = await client.post("/users", json={"email": "test@example.com", "password": "password"})
    
    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["state_code"] == 200
    assert resp_data["data"]["email"] == "test@example.com"
    assert resp_data["data"]["id"] == 1
    mock_service.create_new_user.assert_called_once_with("test@example.com", "password")

@pytest.mark.asyncio
async def test_get_user(client):
    mock_service = AsyncMock()
    mock_service.get_user.return_value = User(id=1, email="existing@example.com", is_active=1)

    with container.user_service.override(mock_service):
        response = await client.get("/users/1")
    
    assert response.status_code == 200
    resp_data = response.json()
    assert resp_data["state_code"] == 200
    assert resp_data["data"]["email"] == "existing@example.com"
