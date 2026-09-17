import pytest

from gtm_agent import data_service


@pytest.fixture
def prospect(monkeypatch):
    prospect_id = next(iter(data_service.PROSPECTS))
    record = data_service.PROSPECTS[prospect_id]
    replacement = {**record, "tech_stack": list(record["tech_stack"])}
    monkeypatch.setitem(data_service.PROSPECTS, prospect_id, replacement)
    return prospect_id


def test_update_prospect_info_persists_and_invalidates_profile(prospect):
    technology = "Test Technology"
    data_service._PROFILES[prospect] = {"tech_stack": ["stale"]}

    result = data_service.update_prospect_info(prospect, technology)

    assert result["updated"] is True
    assert technology in data_service.fetch_tech_stack(prospect)
    assert prospect not in data_service._PROFILES


def test_update_prospect_info_reports_existing_technology(prospect):
    technology = data_service.fetch_tech_stack(prospect)[0]

    result = data_service.update_prospect_info(prospect, technology)

    assert result == {
        "updated": False,
        "found": True,
        "tech_stack": data_service.fetch_tech_stack(prospect),
        "reason": "technology already present",
    }
