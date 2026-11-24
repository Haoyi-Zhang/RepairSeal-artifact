"""Small independently specified checks for the raw-timing reconciler."""
import unittest

import verify_counter_overhead_study as verification


class CounterOverheadVerificationTests(unittest.TestCase):
    def test_json_rejects_ambiguous_or_nonfinite_measurements(self):
        for text in ('{"n":1,"n":2}', '{"n":NaN}', '{"n":Infinity}', '{"n":1e999}'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                verification.decode(text)
        self.assertEqual(verification.decode('{"n":7,"done":true}'), {"n": 7, "done": True})

    def test_canonical_equality_keeps_scalar_types(self):
        for actual, expected in ((True, 1), (1.0, 1), ({"trace": [[0, True]]}, {"trace": [[0, 1]]})):
            with self.subTest(actual=actual), self.assertRaises(ValueError):
                verification.same(actual, expected, "canonical observation")
        verification.same({"trace": [[0, 1]], "input": [-1]},
                          {"trace": [[0, 1]], "input": [-1]}, "canonical observation")

    def test_nearest_rank_quantiles_are_explicit(self):
        self.assertEqual(verification.quantiles([100, 2, 4, 1, 3]),
                         {"p10": 1, "p25": 2, "p50": 3, "p75": 4, "p90": 100})

    def test_problem_ratio_uses_sums_of_request_medians(self):
        # Unequal baseline durations distinguish cluster sums from an average
        # of ratios: (20 + 60) / (10 + 90) is 0.8, not (2 + 2/3) / 2.
        rows = []
        for live, support in ((10.0, 20.0), (90.0, 60.0)):
            medians = {arm: live for arm in verification.ARMS}
            medians["support"] = support
            rows.append({"problem": "one", "status": "ACCEPT", "role": "cross_source",
                         "median_ns": medians, "ratios": verification.ratios(medians)})
        result = verification.aggregate(rows)
        self.assertEqual(result["request_comparisons"]["support_over_live"],
                         {"lower": 1, "equal": 0, "higher": 1})
        self.assertEqual(result["problem_ratios"][0]["ratios"]["support_over_live"], .8)
        self.assertEqual(result["problem_median_ratios"]["support_over_live"], .8)
        self.assertEqual(result["problem_comparisons"]["support_over_live"],
                         {"lower": 1, "equal": 0, "higher": 0})


if __name__ == "__main__":
    unittest.main()
