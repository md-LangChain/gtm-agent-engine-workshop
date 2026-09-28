import os
import unittest

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("LANGSMITH_TRACING", "false")

from gtm_agent import data_service
from gtm_agent.gtm_agent import build_prospect_profile, get_prospect


def assert_no_sensitive_fields(test_case, value):
    if isinstance(value, dict):
        test_case.assertNotIn("billing_qualification", value)
        for child in value.values():
            assert_no_sensitive_fields(test_case, child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            assert_no_sensitive_fields(test_case, child)


class ProspectRedactionTest(unittest.TestCase):
    prospect_id = "LEAD-12853"

    def setUp(self):
        data_service._PROFILES.clear()

    def tearDown(self):
        data_service._PROFILES.clear()

    def test_prospect_and_new_profile_omit_billing_qualification(self):
        source = data_service.PROSPECTS[self.prospect_id]
        self.assertIn("billing_qualification", source)

        prospect = get_prospect.invoke({"prospect_id": self.prospect_id})
        profile = build_prospect_profile.invoke({"prospect_id": self.prospect_id})

        assert_no_sensitive_fields(self, prospect)
        assert_no_sensitive_fields(self, profile)
        self.assertEqual(prospect["prospect"]["name"], source["name"])
        self.assertEqual(prospect["prospect"]["email"], source["email"])
        self.assertEqual(profile["prospect_profile"]["name"], source["name"])
        self.assertEqual(profile["prospect_profile"]["email"], source["email"])
        assert_no_sensitive_fields(self, data_service._PROFILES)

    def test_cached_profile_is_redacted_before_return(self):
        source = data_service.PROSPECTS[self.prospect_id]
        data_service._PROFILES[self.prospect_id] = {
            "prospect_id": self.prospect_id,
            "name": source["name"],
            "email": source["email"],
            "billing_qualification": source["billing_qualification"],
        }

        profile = build_prospect_profile.invoke({"prospect_id": self.prospect_id})

        assert_no_sensitive_fields(self, profile)
        assert_no_sensitive_fields(self, data_service._PROFILES)
        self.assertEqual(profile["prospect_profile"]["name"], source["name"])
        self.assertEqual(profile["prospect_profile"]["email"], source["email"])


if __name__ == "__main__":
    unittest.main()
