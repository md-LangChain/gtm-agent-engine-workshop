import os

os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["LANGSMITH_TRACING"] = "false"

import pytest

from gtm_agent import data_service
from gtm_agent.gtm_agent import build_prospect_profile


PROSPECT_ID = "LEAD-71001"


@pytest.fixture
def clean_prospect_state():
    original_stack = list(data_service.PROSPECTS[PROSPECT_ID]["tech_stack"])
    original_profile = data_service._PROFILES.pop(PROSPECT_ID, None)
    yield
    data_service.PROSPECTS[PROSPECT_ID]["tech_stack"] = original_stack
    data_service._PROFILES.pop(PROSPECT_ID, None)
    if original_profile is not None:
        data_service._PROFILES[PROSPECT_ID] = original_profile


def test_update_persists_technology(clean_prospect_state):
    data_service.update_prospect_info(PROSPECT_ID, "Kafka")

    assert "Kafka" in data_service.fetch_tech_stack(PROSPECT_ID)


def test_update_invalidates_cached_profile(clean_prospect_state):
    profile = build_prospect_profile.invoke({"prospect_id": PROSPECT_ID})
    assert "Kafka" not in profile["prospect_profile"]["tech_stack"]

    data_service.update_prospect_info(PROSPECT_ID, "Kafka")
    refreshed_profile = build_prospect_profile.invoke({"prospect_id": PROSPECT_ID})

    assert "Kafka" in refreshed_profile["prospect_profile"]["tech_stack"]


def test_update_does_not_duplicate_existing_technology(clean_prospect_state):
    data_service.update_prospect_info(PROSPECT_ID, "Kafka")
    data_service.update_prospect_info(PROSPECT_ID, "Kafka")

    assert data_service.fetch_tech_stack(PROSPECT_ID).count("Kafka") == 1
