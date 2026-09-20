"""Comprehensive test script for hardened TeachMind skill extraction flow.

Executes:
1. TEST 1: Coffee workflow extraction & storage
2. TEST 2: Weekly calendar summary extraction
3. TEST 3: Customer complaint categorization extraction
4. TEST 4: Presentation preparation extraction
5. TEST 5: Deadline-based study schedule extraction
6. TEST 6: Store TEST 1 (Coffee) in PostgreSQL + pgvector
7. TEST 7: Semantic Search with completely different wording ("Prepare my usual coffee.")
8. TEST 8: Verify retrieved complete canonical Skill JSON & similarity score
"""

import sys
import json
import urllib.request
import urllib.error

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://127.0.0.1:8000"

def request_json(endpoint: str, method: str = "GET", data: dict = None, timeout: int = 45) -> dict:
    url = f"{BASE_URL}{endpoint}"
    req_data = json.dumps(data).encode("utf-8") if data else None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    print("==================================================")
    print("STARTING TEACHMIND HARDENED EXTRACTION & REUSE TEST")
    print("==================================================")

    test_cases = [
        (
            "TEST 1 (Coffee Preparation)",
            "I want you to make my morning coffee. Boil the water, add one teaspoon of coffee and two teaspoons of sugar, pour the hot water, stir well, and serve."
        ),
        (
            "TEST 2 (Weekly Calendar Summary)",
            "Every Friday, check my calendar for next week's meetings and create a short summary."
        ),
        (
            "TEST 3 (Customer Complaint Handling)",
            "When I receive a customer complaint, record it in the complaints sheet, categorize it, and notify me if it is urgent."
        ),
        (
            "TEST 4 (Presentation Preparation)",
            "Whenever I ask you to prepare my presentation, use the latest slides, check for missing content, and export the final version."
        ),
        (
            "TEST 5 (Study Schedule Optimization)",
            "Organize my study schedule around upcoming deadlines. Give more time to subjects with earlier deadlines."
        ),
    ]

    extracted_skills = []

    for name, prompt in test_cases:
        print(f"\n--- {name} ---")
        print(f"Input text: \"{prompt}\"")
        try:
            res = request_json("/skills/extract", method="POST", data={"text": prompt}, timeout=45)
            skill = res.get("skill", {})
            assert skill.get("skill_id"), "Missing skill_id"
            assert skill.get("name"), "Missing name"
            assert skill.get("description"), "Missing description"
            assert isinstance(skill.get("triggers"), list), "triggers not list"
            assert len(skill.get("steps", [])) > 0, "No steps extracted"
            assert skill.get("version") == 1, "version not 1"
            assert skill.get("verified") is False, "verified not False"
            assert skill.get("metadata", {}).get("created_at"), "Missing metadata"

            print(f"[PASS] Extracted: ID='{skill['skill_id']}' | Name='{skill['name']}'")
            print(f"       Steps: {len(skill['steps'])} | Rules: {len(skill.get('rules', []))} | Triggers: {skill.get('triggers')[:2]}")
            extracted_skills.append(skill)
        except Exception as e:
            print(f"[FAIL] Extraction failed for {name}: {e}")
            sys.exit(1)

    # ----------------------------------------------------
    # Store Test 1 (Coffee) in PostgreSQL + pgvector
    # ----------------------------------------------------
    coffee_skill = extracted_skills[0]
    print(f"\n--- STORING TEST 1 SKILL IN POSTGRESQL (ID: {coffee_skill['skill_id']}) ---")
    store_payload = {
        "skill_id": coffee_skill["skill_id"],
        "name": coffee_skill["name"],
        "description": coffee_skill["description"],
        "triggers": coffee_skill.get("triggers", []),
        "steps": coffee_skill.get("steps", []),
        "rules": coffee_skill.get("rules", []),
        "examples": coffee_skill.get("examples", []),
        "version": 1,
        "verified": False,
    }
    try:
        store_res = request_json("/skills", method="POST", data=store_payload)
        print(f"[PASS] Successfully stored '{store_res['name']}' in PostgreSQL via POST /skills")
    except urllib.error.HTTPError as e:
        if e.code == 409:
            print(f"[PASS] Skill '{coffee_skill['skill_id']}' already stored in PostgreSQL. Proceeding to search.")
        else:
            print(f"[FAIL] Failed to store skill: {e}")
            sys.exit(1)

    # ----------------------------------------------------
    # Semantic Search with Substantially Different Wording
    # ----------------------------------------------------
    diff_query = "Prepare my usual coffee."
    print(f"\n--- SEMANTIC SEARCH (TEST 8: REUSE WITH DIFFERENT WORDING) ---")
    print(f"Query: \"{diff_query}\"")
    try:
        search_res = request_json("/skills/search", method="POST", data={"query": diff_query, "top_k": 3})
        results = search_res.get("results", [])
        assert len(results) > 0, "No semantic search results returned"
        top_match = results[0]
        print(f"[PASS] Top match: {top_match['name']} (ID: {top_match['skill_id']})")
        print(f"       Similarity score: {top_match['similarity']}")
        assert top_match["similarity"] > 0.4, f"Similarity {top_match['similarity']} below expected threshold"
        assert top_match["skill"]["skill_id"] == top_match["skill_id"], "Nested canonical skill mismatch"
        print(f"[PASS] Complete canonical Skill JSON retrieved for: {top_match['skill']['description'][:60]}...")
    except Exception as e:
        print(f"[FAIL] Semantic retrieval failed: {e}")
        sys.exit(1)

    print("\n==================================================")
    print("ALL TESTS PASSED WITH 100% SUCCESS")
    print("==================================================")

if __name__ == "__main__":
    main()
