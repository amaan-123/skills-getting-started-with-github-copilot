import pytest
from httpx import AsyncClient, ASGITransport
from src.app import app

@pytest.mark.anyio
async def test_get_activities():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "participants" in data["Chess Club"]

@pytest.mark.anyio
async def test_signup_for_activity():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Test successful signup
        response = await client.post("/activities/Chess%20Club/signup?email=test@example.com")
        assert response.status_code == 200
        data = response.json()
        assert "Signed up test@example.com for Chess Club" in data["message"]

        # Verify the participant was added
        response = await client.get("/activities")
        data = response.json()
        assert "test@example.com" in data["Chess Club"]["participants"]

@pytest.mark.anyio
async def test_signup_already_signed_up():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # First signup
        await client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")
        
        # Try to signup again
        response = await client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")
        assert response.status_code == 400
        data = response.json()
        assert "Student is already signed up" in data["detail"]

@pytest.mark.anyio
async def test_signup_activity_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post("/activities/NonExistent/signup?email=test@example.com")
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

@pytest.mark.anyio
async def test_unregister_from_activity():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # First signup
        await client.post("/activities/Chess%20Club/signup?email=unregister@example.com")
        
        # Unregister
        response = await client.delete("/activities/Chess%20Club/unregister?email=unregister@example.com")
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered unregister@example.com from Chess Club" in data["message"]

        # Verify removed
        response = await client.get("/activities")
        data = response.json()
        assert "unregister@example.com" not in data["Chess Club"]["participants"]

@pytest.mark.anyio
async def test_unregister_not_signed_up():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.delete("/activities/Chess%20Club/unregister?email=notsigned@example.com")
        assert response.status_code == 400
        data = response.json()
        assert "Student is not signed up" in data["detail"]

@pytest.mark.anyio
async def test_root_redirect():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/")
        assert response.status_code == 307  # Redirect
        assert response.headers["location"] == "/static/index.html"