import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import beginner_toolkit as b


class BeginnerLiteTests(unittest.TestCase):
    def test_onboarding_asks_business_question_first(self):
        out = b.onboarding({})
        self.assertEqual(out["status"], "ONBOARDING_IN_PROGRESS")
        self.assertEqual(out["missing_fields"][0], "offer")
        self.assertFalse(out["external_writes"])

    def test_onboarding_ready(self):
        data = {k: "value" for k in ("offer", "customer", "goal", "market", "landing_url", "spend_limit", "measurement")}
        self.assertEqual(b.onboarding(data)["status"], "READY_FOR_STARTER_DRAFT")

    def test_budget_is_assumption_only(self):
        out = b.budget_scenarios({"currency": "TWD", "total_budget": 1000, "days": 10})
        self.assertEqual(out["status"], "ASSUMPTION_ONLY_NOT_APPROVED")
        self.assertFalse(out["external_writes"])

    def test_terminology_explains_context_hints_boundary(self):
        out = b.explain("context hints")
        self.assertTrue(out["known"])
        self.assertIn("不是精準", out["explanation"])

    def test_landing_unknown_requires_check(self):
        self.assertEqual(b.landing_readiness({})["status"], "CHECK_REQUIRED")

    def test_metrics_without_conversion_tracking_are_descriptive(self):
        out = b.translate_metrics({"clicks": 2, "impressions": 100, "spend": 10})
        self.assertEqual(out["status"], "DESCRIPTIVE_ONLY")
        self.assertFalse(out["reliable_conversion_conclusion"])

    def test_no_pro_operations_are_exposed(self):
        for name in ("validate_capability", "change_preview", "reconcile_partial_write", "check_state_drift"):
            self.assertFalse(hasattr(b, name))


if __name__ == "__main__":
    unittest.main()
