import os
import unittest

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from gtm_agent import data_service
from gtm_agent import gtm_agent
from gtm_agent.gtm_records import PROSPECTS


class ProspectToolPrivacyTests(unittest.TestCase):
    prospect_id = "LEAD-12853"

    def setUp(self):
        self.record = PROSPECTS[self.prospect_id]
        self.original_record = self.record.copy()
        data_service._PROFILES.pop(self.prospect_id, None)

    def tearDown(self):
        self.record.clear()
        self.record.update(self.original_record)
        data_service._PROFILES.pop(self.prospect_id, None)

    def assert_safe_prospect(self, prospect):
        self.assertNotIn("billing_qualification", prospect)
        self.assertNotIn("tax_id", prospect)
        self.assertNotIn("date_of_birth", prospect)
        self.assertNotIn("card_on_file", prospect)
        self.assertNotIn("credit_check_ref", prospect)
        self.assertNotIn("synthetic_sensitive_field", prospect)

    def test_get_prospect_returns_only_allowlisted_fields(self):
        self.record["synthetic_sensitive_field"] = "synthetic-value"

        result = gtm_agent.get_prospect.invoke({"prospect_id": self.prospect_id})

        self.assert_safe_prospect(result["prospect"])
        self.assertEqual(set(result["prospect"]), set(gtm_agent.PROSPECT_FIELDS))

    def test_build_profile_excludes_sensitive_fields_and_persists_safe_profile(self):
        self.record["synthetic_sensitive_field"] = "synthetic-value"

        result = gtm_agent.build_prospect_profile.invoke({"prospect_id": self.prospect_id})
        profile = result["prospect_profile"]

        self.assert_safe_prospect(profile)
        self.assertEqual(data_service._PROFILES[self.prospect_id], profile)

    def test_build_profile_sanitizes_contaminated_cached_profile(self):
        contaminated = {
            **self.record,
            "prospect_id": self.prospect_id,
            "billing_qualification": {"tax_id": "synthetic-tax-id"},
            "synthetic_sensitive_field": "synthetic-value",
        }
        data_service._PROFILES[self.prospect_id] = contaminated

        result = gtm_agent.build_prospect_profile.invoke({"prospect_id": self.prospect_id})
        profile = result["prospect_profile"]

        self.assert_safe_prospect(profile)
        self.assertEqual(data_service._PROFILES[self.prospect_id], profile)
        self.assertEqual(profile["prospect_id"], self.prospect_id)
        self.assertNotIn("billing_qualification", data_service._PROFILES[self.prospect_id])


if __name__ == "__main__":
    unittest.main()
