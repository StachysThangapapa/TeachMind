"""
Comprehensive API Endpoint & Integration Tests for TeachMind.
Tests both /skills (Skill Memory API) and /api/v1/agent (AI Agent API) endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.db.migrations import run_migrations

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    run_migrations()


def test_health_check():
    """Verify health endpoint."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "online"


def test_agent_execute_research_summary_no_500():
    """CRITICAL TEST: Verify original 500 error is eliminated and returns HTTP 200."""
    payload = {
        "query": "Give me a research summary.",
        "user_id": "user_default"
    }
    resp = client.post("/api/v1/agent/execute", json=payload)
    assert resp.status_code == 200, f"Expected 200 OK, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["status"] == "success"
    assert data["decision"] == "PROCESSED"
    assert len(data["message"]) > 0


def test_agent_execute_calculator():
    """Verify calculator tool execution."""
    payload = {
        "query": "What is 18% of 1250?",
        "user_id": "user_default"
    }
    resp = client.post("/api/v1/agent/execute", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "225" in data["message"]


def test_agent_execute_datetime():
    """Verify datetime tool execution."""
    payload = {
        "query": "What day of the week is today?",
        "user_id": "user_default"
    }
    resp = client.post("/api/v1/agent/execute", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "Today is" in data["message"]


def test_skills_crud_and_search_endpoints():
    """Verify Skill Memory API: create, search, get, update, verify, and version history."""
    skill_id = "skill_test_order_processing"

    # 1. POST /skills (Store new skill)
    create_payload = {
        "skill_id": skill_id,
        "name": "Order Processing Workflow",
        "description": "Process ecommerce orders and notify warehouse.",
        "triggers": ["process order", "handle new order", "order fulfillment"],
        "steps": [
            {"step": 1, "instruction": "Validate order items and inventory."},
            {"step": 2, "instruction": "Charge customer payment method."},
            {"step": 3, "instruction": "Send packing slip to warehouse."}
        ],
        "rules": [
            {"condition": "order value > 500", "action": "require manager approval"}
        ],
        "examples": [
            {"input": "New order #1234 received.", "expected_behavior": "Warehouse notified."}
        ],
        "version": 1,
        "verified": False
    }
    post_resp = client.post("/skills", json=create_payload)
    assert post_resp.status_code in (201, 409)
    if post_resp.status_code == 201:
        data = post_resp.json()
        assert data["skill_id"] == skill_id
        assert data["name"] == "Order Processing Workflow"
        assert data["version"] == 1
        assert not data["verified"]
        assert "metadata" in data

    # 2. GET /skills (List skills)
    list_resp = client.get("/skills")
    assert list_resp.status_code == 200
    assert "skills" in list_resp.json()
    assert any(s["skill_id"] == skill_id for s in list_resp.json()["skills"])

    # 3. GET /skills/{skill_id} (Retrieve single skill)
    get_resp = client.get(f"/skills/{skill_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["skill_id"] == skill_id

    # 4. POST /skills/search (Search matching struct.json contract)
    search_payload = {
        "query": "handle new order for customer",
        "top_k": 3
    }
    search_resp = client.post("/skills/search", json=search_payload)
    assert search_resp.status_code == 200
    sdata = search_resp.json()
    assert "query" in sdata
    assert "results" in sdata
    assert len(sdata["results"]) > 0
    top_res = sdata["results"][0]
    assert "skill_id" in top_res
    assert "name" in top_res
    assert "similarity" in top_res
    assert "skill" in top_res
    assert top_res["skill"]["skill_id"] == skill_id

    # 5. PATCH /skills/{skill_id}/verify (Verify skill)
    verify_resp = client.patch(f"/skills/{skill_id}/verify")
    assert verify_resp.status_code == 200
    assert verify_resp.json()["verified"] is True

    # 6. PATCH /skills/{skill_id} (Update/Correction)
    # Read the current version first so the assertion is run-independent
    pre_update = client.get(f"/skills/{skill_id}")
    version_before = pre_update.json()["version"]

    update_payload = {
        "description": "Updated order processing workflow with fraud check.",
        "rules": [
            {"condition": "order value > 500", "action": "require manager approval"},
            {"condition": "billing address mismatch", "action": "flag for review"}
        ]
    }
    update_resp = client.patch(f"/skills/{skill_id}", json=update_payload)
    assert update_resp.status_code == 200
    updata = update_resp.json()
    assert updata["version"] == version_before + 1
    assert len(updata["rules"]) == 2

    # 7. GET /skills/{skill_id}/versions (Version history)
    ver_resp = client.get(f"/skills/{skill_id}/versions")
    assert ver_resp.status_code == 200
    versions = ver_resp.json()
    assert len(versions) >= 2
    # Most recent two snapshots must be consecutive
    last_two = sorted(versions, key=lambda v: v["version"])[-2:]
    assert last_two[1]["version"] == last_two[0]["version"] + 1

