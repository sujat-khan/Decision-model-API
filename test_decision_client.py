"""Unit and integration test script for OpenRouter Decision Models."""
import os
import unittest
from unittest.mock import patch, MagicMock
from src.schemas import (
    NoulQuestion,
    ChoiceQuestion,
    ScoreQuestion,
    SystemOneRequest,
    SystemOneResponse,
)
from src.client import DecisionClient, AuthenticationError, DecisionAPIError
from src.presets import PRESETS

class TestDecisionSchemas(unittest.TestCase):
    """Test schema validation and serialization."""

    def test_noul_question(self):
        q = NoulQuestion(
            instructions="Is this a bug?",
            criteria={"true": "Yes, broken behavior", "false": "No, expected"}
        )
        self.assertEqual(q.type, "noul")
        self.assertEqual(q.instructions, "Is this a bug?")

    def test_choice_question(self):
        q = ChoiceQuestion(
            instructions="Which team?",
            criteria={"billing": "Charges", "tech": "Bugs"}
        )
        self.assertEqual(q.type, "choice")
        self.assertIn("billing", q.criteria)

    def test_score_question(self):
        q = ScoreQuestion(
            instructions="How urgent?",
            criteria=["Low", "Medium", "High"]
        )
        self.assertEqual(q.type, "score")
        self.assertEqual(len(q.criteria), 3)

    def test_systemone_request_validation(self):
        preset = PRESETS["agent_guardrail"]
        req = SystemOneRequest(
            model="inception/mercury-decide:free",
            state=preset["state"],
            questions=preset["questions"],
        )
        self.assertEqual(req.model, "inception/mercury-decide:free")
        self.assertIn("is_destructive", req.questions)

class TestDecisionClient(unittest.TestCase):
    """Test DecisionClient behavior with mocks and validation."""

    def test_missing_api_key_raises(self):
        client = DecisionClient(api_key="")
        with self.assertRaises(AuthenticationError):
            client.evaluate(
                model="inception/mercury-decide:free",
                state="Test state",
                questions={"q": {"type": "noul", "instructions": "test"}}
            )

    @patch("requests.post")
    def test_successful_mock_evaluation(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": "gen-dec-12345",
            "model": "inception/mercury-decide:free",
            "provider": "Inception Labs",
            "answers": {
                "is_destructive": {
                    "type": "noul",
                    "noul": 0.94
                },
                "gate_approval": {
                    "type": "choice",
                    "choice": "require_confirmation",
                    "confidence": 0.88,
                    "probabilities": {
                        "allow": 0.04,
                        "require_confirmation": 0.88,
                        "block": 0.08
                    }
                }
            },
            "usage": {
                "input_tokens": 120,
                "output_tokens": 0,
                "cost": 0.0
            }
        }
        mock_post.return_value = mock_resp

        client = DecisionClient(api_key="test_dummy_key")
        result = client.evaluate(
            model="inception/mercury-decide:free",
            state="Delete database table",
            questions={"is_destructive": {"type": "noul", "instructions": "Destructive?"}}
        )

        self.assertEqual(result.model, "inception/mercury-decide:free")
        self.assertEqual(result.answers["is_destructive"]["noul"], 0.94)
        self.assertEqual(result.answers["gate_approval"]["choice"], "require_confirmation")
        self.assertGreater(result.latency_ms, 0)

if __name__ == "__main__":
    unittest.main()
