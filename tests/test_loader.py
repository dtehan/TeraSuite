"""YAML suite loading."""

from tests.case_loader import load_all_cases, load_persona_cases, persona_names


def test_every_persona_file_loads():
    names = persona_names()
    assert names == [
        "business_user",
        "data_analyst",
        "data_scientist",
        "database_operations",
        "dba",
        "security_expert",
    ]
    cases = load_all_cases(apply_env=False)
    ids = [case["id"] for case in cases]
    assert len(ids) == len(set(ids))
    for name in names:
        persona_cases = [case for case in cases if case["persona"] == name]
        assert len(persona_cases) >= 20, name
        assert {case["category"] for case in persona_cases} >= {"typical", "edge"}


def test_filters_do_not_read_process_env(monkeypatch):
    monkeypatch.setenv("EVALS_PERSONA", "dba")
    monkeypatch.setenv("EVALS_CASE_ID", "DBA-001")
    everyone = load_all_cases(apply_env=False)
    assert len(everyone) > 20
    only = load_all_cases(persona="security_expert", apply_env=False)
    assert only
    assert {case["persona"] for case in only} == {"security_expert"}
    one = load_all_cases(case_id="BU-001", apply_env=False)
    assert [case["id"] for case in one] == ["BU-001"]
    assert load_persona_cases("dba")[0]["persona"] == "dba"
