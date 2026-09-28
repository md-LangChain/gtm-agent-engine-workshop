import unittest
from types import SimpleNamespace
from unittest.mock import patch

from gtm_agent import gtm_agent


class SendProspectEmailTests(unittest.TestCase):
    def setUp(self):
        self.runtime = SimpleNamespace(config={"metadata": {"user_id": "REP-10001"}})
        self.prospect = {
            "prospect_id": "LEAD-50001",
            "name": "Disqualified Prospect",
            "email": "disqualified@example.com",
        }

    def test_disqualified_prospect_is_blocked_without_message_id(self):
        with patch.object(gtm_agent.uuid, "uuid4") as uuid4:
            result = gtm_agent.send_prospect_email.func(
                self.prospect, "Subject", "Body", self.runtime
            )

        self.assertEqual(
            result,
            {
                "status": "blocked",
                "reason": "prospect is marked disqualified",
                "prospect_id": "LEAD-50001",
                "requires_override": True,
            },
        )
        uuid4.assert_not_called()

    def test_eligible_prospect_is_sent_with_message_id(self):
        prospect = {
            "prospect_id": "LEAD-12853",
            "name": "Eligible Prospect",
            "email": "eligible@example.com",
        }
        with patch.object(
            gtm_agent.uuid, "uuid4", return_value=SimpleNamespace(hex="abc123")
        ):
            result = gtm_agent.send_prospect_email.func(
                prospect, "Subject", "Body", self.runtime
            )

        self.assertEqual(result["status"], "sent")
        self.assertEqual(result["message_id"], "msg-abc123")

    def test_get_prospect_includes_disqualified_flag(self):
        result = gtm_agent.get_prospect.func("LEAD-50001")

        self.assertTrue(result["prospect"]["disqualified"])


if __name__ == "__main__":
    unittest.main()
