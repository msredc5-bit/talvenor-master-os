"""TEST fixtures for the Phase 6 lead chain — TEST DATA ONLY.

Three prospects, all clearly marked TEST (names, ``.invalid`` /
``.example`` addresses, fictional +1-555-01xx numbers). Never use
real records from ``store/leads.json`` as chain inputs — that file
is read-only reference for SHAPE only (its records look like
{"id": "L-0001", "business_name": ..., "email": ..., "phone": ...,
"score": 90, "tier": "Tier 1", "confidence": "medium",
"best_channel": "email"}).

  (a) STRONG_TIER1_PROSPECT — STRONG, Tier 1, complete. Expected
      chain outcome: "blocked" at deployment (always blocked in
      sandbox), outreach send held pending-approval, monitoring
      skipped as a deployment dependency, everything else ok.
  (b) MEDIUM_TIER2_PROSPECT — MEDIUM, Tier 2, complete. Same
      expected outcome as (a) (score 62 -> Tier 2).
  (c) WEAK_INCOMPLETE_PROSPECT — WEAK/incomplete, email MISSING.
      Expected outcome: discovery ok, verification "error"
      (missing email), chain "failed", all later steps "skipped"
      with reason "dependency: lead_verification".

Extra fields beyond the store shape (website, domain, state, city,
business_type) are what the step executors in steps.py need:
discovery requires a website, the CRM dry-run requires state +
domain, qualification DQs dental/medical by business_type.
"""

from __future__ import annotations

__all__ = [
    "STRONG_TIER1_PROSPECT",
    "MEDIUM_TIER2_PROSPECT",
    "WEAK_INCOMPLETE_PROSPECT",
    "FIXTURES",
]

STRONG_TIER1_PROSPECT = {
    "id": "TEST-L-0001",
    "business_name": "TEST Prospect LLC",
    "business_type": "plumbing",
    "website": "https://test-prospect.example",
    "domain": "test-prospect.example",
    "email": "test@example.invalid",
    "phone": "+1-555-0100",
    "city": "Drexel Hill",
    "state": "PA",
    "score": 85,
    "tier": "Tier 1",
    "confidence": "medium",
    "best_channel": "email",
}

MEDIUM_TIER2_PROSPECT = {
    "id": "TEST-L-0002",
    "business_name": "TEST Sample Plumbing LLC",
    "business_type": "hvac",
    "website": "https://test-sample-plumbing.example",
    "domain": "test-sample-plumbing.example",
    "email": "test-plumbing@example.invalid",
    "phone": "+1-555-0101",
    "city": "Drexel Hill",
    "state": "PA",
    "score": 62,
    "tier": "Tier 2",
    "confidence": "medium",
    "best_channel": "email",
}

WEAK_INCOMPLETE_PROSPECT = {
    "id": "TEST-L-0003",
    "business_name": "TEST Incomplete Prospects LLC",
    "business_type": "plumbing",
    "website": "https://test-incomplete.example",
    "domain": "test-incomplete.example",
    "email": None,  # MISSING — exercises verification failure routing
    "phone": "+1-555-0102",
    "city": "Drexel Hill",
    "state": "PA",
    "score": 30,
    "tier": "Tier 4",
    "confidence": "weak",
    "best_channel": "email",
}

FIXTURES = {
    "strong_tier1": STRONG_TIER1_PROSPECT,
    "medium_tier2": MEDIUM_TIER2_PROSPECT,
    "weak_incomplete": WEAK_INCOMPLETE_PROSPECT,
}

if __name__ == "__main__":
    # Self-check: all fixtures are clearly TEST data, and (c) is
    # the only one missing an email.
    for _name, _fx in FIXTURES.items():
        assert str(_fx["business_name"]).startswith("TEST"), _name
        assert str(_fx["id"]).startswith("TEST-"), _name
        assert str(_fx["phone"]).startswith("+1-555-01"), _name
        assert _fx["email"] is None or ".invalid" in _fx["email"], _name
        assert ".example" in str(_fx["website"]), _name
    assert WEAK_INCOMPLETE_PROSPECT["email"] is None
    assert STRONG_TIER1_PROSPECT["score"] == 85
    assert MEDIUM_TIER2_PROSPECT["score"] == 62
    assert WEAK_INCOMPLETE_PROSPECT["score"] == 30
    print("fixtures: OK (3 TEST prospects; (a) STRONG/Tier 1, "
          "(b) MEDIUM/Tier 2, (c) WEAK, email MISSING)")
