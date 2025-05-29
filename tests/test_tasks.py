import pytest
from httpx import AsyncClient
from app.main import app
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_create_task():
    async with AsyncClient(base_url="http://localhost:8000/") as client:
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "priority": 2
        }

        response = await client.post("/tasks/", json=task_data)
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["priority"] == task_data["priority"]
        assert data["status"] == "pending"
        assert "id" in data

@pytest.mark.asyncio
async def test_get_tasks():
    async with AsyncClient(base_url="http://localhost:8000/") as client:
        for i in range(3):
            await client.post("/tasks/", json={
                "title": f"Task {i}",
                "description": f"Description {i}",
                "priority": i + 1
            })

        response = await client.get("/tasks/")
        assert response.status_code == 200

        data = response.json()
        assert len(data["items"]) == 4
        assert data["total"] == 4
        assert data["page"] == 1
        assert data["per_page"] == 10

@pytest.mark.asyncio
async def test_get_task_by_id():
    async with AsyncClient(base_url="http://localhost:8000/") as client:
        create_response = await client.post("/tasks/", json={
            "title": "Test Task",
            "description": "Test Description"
        })
        task_id = create_response.json()["id"]

        response = await client.get(f"/tasks/{task_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"

@pytest.mark.asyncio
async def test_update_task():
    async with AsyncClient(base_url="http://localhost:8000/") as client:
        create_response = await client.post("/tasks/", json={
            "title": "Original Title",
            "description": "Original Description"
        })
        task_id = create_response.json()["id"]

        update_data = {
            "title": "Updated Title",
            "status": "in_progress"
        }

        response = await client.put(f"/tasks/{task_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "in_progress"

@pytest.mark.asyncio
async def test_delete_task():
    async with AsyncClient(base_url="http://localhost:8000/") as client:
        create_response = await client.post("/tasks/", json={
            "title": "Task to Delete"
        })
        task_id = create_response.json()["id"]

        response = await client.delete(f"/tasks/{task_id}")
        assert response.status_code == 204

        response = await client.get(f"/tasks/{task_id}")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_start_task_processing():
    async with AsyncClient(base_url="http://localhost:8000/") as client:
        create_response = await client.post("/tasks/", json={
            "title": "Task to Process"
        })
        task_id = create_response.json()["id"]

        response = await client.post(f"/tasks/{task_id}/process")
        assert response.status_code == 202

        data = response.json()
        assert "Background processing started" in data["message"]

@pytest.mark.asyncio
async def test_task_filtering():
    async with AsyncClient(base_url="http://localhost:8000/") as client:
        await client.post("/tasks/", json={"title": "Important Task", "priority": 1})
        await client.post("/tasks/", json={"title": "Regular Task", "priority": 2})

        response = await client.get("/tasks/?title=Important")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert "Important" in data["items"][0]["title"]

@pytest.mark.asyncio
async def test_task_validation():
    async with AsyncClient(base_url="http://localhost:8000/") as client:
        response = await client.post("/tasks/", json={
            "title": "",
            "description": "Test"
        })
        assert response.status_code == 422

        response = await client.post("/tasks/", json={
            "title": "Test Task",
            "priority": 10
        })
        assert response.status_code == 422