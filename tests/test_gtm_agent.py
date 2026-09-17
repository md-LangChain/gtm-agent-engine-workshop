import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from gtm_agent import gtm_agent


class GtmAgentTest(unittest.TestCase):
    def test_scoring_request_receives_rep_identity_without_email(self):
        rep = {"rep_id": "REP-1001", "name": "Alex Rivera", "email": "alex@example.com"}
        result_message = SimpleNamespace(content="Scored prospect")

        with patch.object(gtm_agent.data_service, "get_rep", return_value=rep), patch.object(
            gtm_agent.gtm_agent,
            "invoke",
            return_value={"messages": [result_message]},
        ) as invoke:
            gtm_agent.run_agent(
                "Score LEAD-12853 for OFFER-10001.",
                user_id="REP-1001",
            )

        invocation = invoke.call_args.args[0]
        self.assertEqual(
            invocation["messages"][0],
            {
                "role": "system",
                "content": 'Signed-in rep context: {"name": "Alex Rivera", "email": "alex@example.com"}',
            },
        )
