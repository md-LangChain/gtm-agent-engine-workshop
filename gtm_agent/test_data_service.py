import os
import unittest

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ["LANGSMITH_TRACING"] = "false"

from gtm_agent import data_service
from gtm_agent.gtm_agent import build_prospect_profile


class UpdateProspectInfoTests(unittest.TestCase):
    prospect_id = "LEAD-71001"

    def setUp(self):
        self.record = data_service.PROSPECTS[self.prospect_id]
        self.original_tech_stack = list(self.record["tech_stack"])
        data_service._PROFILES.clear()

    def tearDown(self):
        self.record["tech_stack"] = self.original_tech_stack
        data_service._PROFILES.clear()

    def test_update_persists_technology(self):
        data_service.update_prospect_info(self.prospect_id, "Kafka")

        self.assertIn("Kafka", data_service.fetch_tech_stack(self.prospect_id))

    def test_update_invalidates_cached_profile(self):
        initial = build_prospect_profile.invoke({"prospect_id": self.prospect_id})

        data_service.update_prospect_info(self.prospect_id, "Kafka")
        refreshed = build_prospect_profile.invoke({"prospect_id": self.prospect_id})

        self.assertNotIn("Kafka", initial["prospect_profile"]["tech_stack"])
        self.assertIn("Kafka", refreshed["prospect_profile"]["tech_stack"])

    def test_second_update_reports_already_present(self):
        data_service.update_prospect_info(self.prospect_id, "Kafka")

        result = data_service.update_prospect_info(self.prospect_id, "Kafka")

        self.assertFalse(result["updated"])
        self.assertTrue(result["already_present"])


if __name__ == "__main__":
    unittest.main()
