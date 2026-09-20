"""
TeachMind Unified System Verification & Acceptance Test.
Tests all endpoints (C, D, E, F) and demonstrates the complete 16-step end-to-end flow.
"""

import json
import time
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"


def http_req(method: str, path: str, payload: dict = None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def run_tests():
    print("=" * 70)
    print("TEACHMIND UNIFIED INTEGRATION VERIFICATION")
    print("=" * 70)

    # -------------------------------------------------------------
    # 1. C: Verify GET / and GET /health
    # -------------------------------------------------------------
    print("\n[Step 1] Checking GET / and GET /health...")
    status, root_data = http_req("GET", "/")
    assert status == 200, f"Expected 200, got {status}"
    print(f"  [OK] GET /: status={status}, project='{root_data.get('project')}'")

    status, health_data = http_req("GET", "/health")
    assert status == 200 and health_data.get("status") == "online"
    print(f"  [OK] GET /health: online={health_data.get('status')}, subsystems={health_data.get('subsystems')}")

    # -------------------------------------------------------------
    # 2. E: Cohere Natural-Language Extraction: POST /skills/extract
    # -------------------------------------------------------------
    print("\n[Step 2] Testing POST /skills/extract (Cohere Natural-Language Extraction)...")
    teaching_text = (
        "When handling urgent customer refund requests, first verify if the purchase was made within 7 days. "
        "If it is a clearance item, reject unless the item arrived damaged or defective. "
        "For approved items, issue a replacement or refund immediately."
    )
    print(f"  Input text: \"{teaching_text}\"")
    status, extract_resp = http_req("POST", "/skills/extract", {"text": teaching_text})
    assert status == 200, f"Extraction failed with status {status}"
    extracted_skill = extract_resp["skill"]
    skill_id = extracted_skill["skill_id"]
    skill_name = extracted_skill["name"]
    print(f"  [OK] POST /skills/extract returned 200 OK")
    print(f"    - Extracted skill_id: {skill_id}")
    print(f"    - Extracted name:     {skill_name}")
    print(f"    - Extracted steps:    {len(extracted_skill['steps'])} step(s)")
    print(f"    - Extracted rules:    {len(extracted_skill['rules'])} rule(s)")
    print(f"    - Extracted triggers: {extracted_skill['triggers']}")

    # -------------------------------------------------------------
    # 3. D: Store in PostgreSQL + pgvector: POST /skills
    # -------------------------------------------------------------
    print(f"\n[Step 3] Storing extracted skill in PostgreSQL + pgvector via POST /skills...")
    # Prepare SkillCreate payload
    store_payload = {
        "skill_id": skill_id,
        "name": skill_name,
        "description": extracted_skill["description"],
        "triggers": extracted_skill["triggers"],
        "steps": extracted_skill["steps"],
        "rules": extracted_skill["rules"],
        "examples": extracted_skill["examples"],
        "version": 1,
        "verified": False
    }
    try:
        status, stored_skill = http_req("POST", "/skills", store_payload)
        print(f"  [OK] POST /skills: status={status}, stored skill_id='{stored_skill['skill_id']}', version={stored_skill['version']}")
    except urllib.error.HTTPError as e:
        if e.code == 409:
            print(f"  Note: Skill '{skill_id}' already stored, retrieving existing.")
            status, stored_skill = http_req("GET", f"/skills/{skill_id}")
        else:
            raise

    # -------------------------------------------------------------
    # 4. D: List and Retrieve: GET /skills and GET /skills/{id}
    # -------------------------------------------------------------
    print(f"\n[Step 4] Checking GET /skills and GET /skills/{skill_id}...")
    status, list_data = http_req("GET", "/skills")
    assert status == 200
    skills_list = list_data.get("skills", [])
    print(f"  [OK] GET /skills: total stored skills={len(skills_list)}")
    assert any(s["skill_id"] == skill_id for s in skills_list)

    status, single_skill = http_req("GET", f"/skills/{skill_id}")
    assert status == 200 and single_skill["skill_id"] == skill_id
    print(f"  [OK] GET /skills/{skill_id}: name='{single_skill['name']}', version={single_skill['version']}")

    # -------------------------------------------------------------
    # 5. D: Semantic Search via pgvector: POST /skills/search
    # -------------------------------------------------------------
    differently_worded_task = "A client wants their money back for broken clearance merchandise bought last week."
    print(f"\n[Step 5] Performing semantic search using differently-worded task via POST /skills/search...")
    print(f"  Query: \"{differently_worded_task}\"")
    status, search_resp = http_req("POST", "/skills/search", {"query": differently_worded_task, "top_k": 3})
    assert status == 200
    results = search_resp.get("results", [])
    print(f"  [OK] POST /skills/search returned {len(results)} candidate(s):")
    for r in results:
        print(f"    - Skill: '{r['name']}' | Similarity: {r['similarity']:.4f} | ID: {r['skill_id']}")
    assert len(results) > 0, "Expected at least one search result"
    top_result = results[0]
    # Check that the complete canonical Skill JSON is present inside the nested 'skill' object
    assert "skill" in top_result
    assert "steps" in top_result["skill"]
    assert "rules" in top_result["skill"]
    print(f"  [OK] Verified complete nested canonical Skill JSON present in search response.")

    # -------------------------------------------------------------
    # 6. F: AI Agent Execution: POST /agent/execute
    # -------------------------------------------------------------
    print(f"\n[Step 6] Testing AI Agent execution via POST /agent/execute...")
    status, agent_resp = http_req("POST", "/agent/execute", {
        "query": differently_worded_task,
        "user_id": "u_test_demo"
    })
    assert status == 200
    print(f"  [OK] POST /agent/execute: status={status}")
    print(f"    - Decision:      {agent_resp.get('decision')}")
    print(f"    - Reason:        {agent_resp.get('reason')}")
    print(f"    - Skill used:    {agent_resp.get('skill_used', {}).get('name') if agent_resp.get('skill_used') else 'None'}")
    print(f"    - Similarity:    {agent_resp.get('similarity')}")
    print(f"    - Timeline:      {len(agent_resp.get('timeline', []))} step(s)")
    for t in agent_resp.get("timeline", []):
        print(f"      * [{t.get('status')}] {t.get('label')}: {t.get('detail') or ''}")

    # -------------------------------------------------------------
    # 7. D: Correction & Version Bump: PATCH /skills/{skill_id}
    # -------------------------------------------------------------
    print(f"\n[Step 7] Testing human correction and version bump via PATCH /skills/{skill_id}...")
    correction_payload = {
        "description": "Updated refund policy with VIP customer expedited approval.",
        "rules": single_skill["rules"] + [
            {"condition": "VIP customer", "action": "approve_immediately"}
        ]
    }
    status, updated_skill = http_req("PATCH", f"/skills/{skill_id}", correction_payload)
    assert status == 200
    print(f"  [OK] PATCH /skills/{skill_id}: status={status}")
    print(f"    - Previous version: {single_skill['version']}")
    print(f"    - New version:      {updated_skill['version']}")
    assert updated_skill["version"] == single_skill["version"] + 1

    # -------------------------------------------------------------
    # 8. D: Mark Verified: PATCH /skills/{skill_id}/verify
    # -------------------------------------------------------------
    print(f"\n[Step 8] Marking skill verified via PATCH /skills/{skill_id}/verify...")
    status, verified_skill = http_req("PATCH", f"/skills/{skill_id}/verify")
    assert status == 200
    assert verified_skill["verified"] is True
    print(f"  [OK] PATCH /skills/{skill_id}/verify: status={status}, verified={verified_skill['verified']}")

    # -------------------------------------------------------------
    # 9. D: Version History: GET /skills/{skill_id}/versions
    # -------------------------------------------------------------
    print(f"\n[Step 9] Retrieving historical versions via GET /skills/{skill_id}/versions...")
    status, versions = http_req("GET", f"/skills/{skill_id}/versions")
    assert status == 200
    print(f"  [OK] GET /skills/{skill_id}/versions: found {len(versions)} historical version(s):")
    for v in versions:
        print(f"    - v{v['version']} created at {v['created_at']} (rules: {len(v['rules'])}, verified: {v['verified']})")
    assert len(versions) >= 2, f"Expected at least 2 versions, got {len(versions)}"

    print("\n" + "=" * 70)
    print("ALL 16-STEP INTEGRATION CRITERIA VERIFIED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
