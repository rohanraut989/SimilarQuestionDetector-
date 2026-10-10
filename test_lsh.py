"""Small standard-library tests for lsh.py.

Run with: python3 -m unittest -v test_lsh
"""

import unittest

from lsh import LSH


class TestLSH(unittest.TestCase):
    def test_duplicate_signatures_make_candidate(self):
        signatures = [[1, 2, 3, 4], [1, 2, 3, 4]]
        self.assertEqual(
            LSH(bands=2, rows=2).candidate_pairs(["R1", "R2"], signatures),
            [("R1", "R2")],
        )

    def test_empty_input_returns_empty_list(self):
        self.assertEqual(LSH(bands=2, rows=2).candidate_pairs([], []), [])

    def test_pairs_are_unique_sorted_and_have_no_self_pairs(self):
        # R1 and R2 share both bands; R3 shares the first band with both.
        signatures = [
            [1, 1, 7, 7],
            [1, 1, 7, 7],
            [1, 1, 9, 9],
            [5, 5, 5, 5],
        ]
        self.assertEqual(
            LSH(bands=2, rows=2).candidate_pairs(
                ["R1", "R2", "R3", "R4"], signatures
            ),
            [("R1", "R2"), ("R1", "R3"), ("R2", "R3")],
        )

    def test_pairs_do_not_depend_on_input_order(self):
        lsh = LSH(bands=1, rows=2)
        expected = [("A", "B"), ("A", "C"), ("B", "C")]
        signatures = [[8, 9], [8, 9], [8, 9]]
        self.assertEqual(
            lsh.candidate_pairs(["C", "A", "B"], signatures), expected
        )

    def test_invalid_band_or_row_count(self):
        for bands, rows in ((0, 2), (2, 0), (-1, 2), (True, 2)):
            with self.subTest(bands=bands, rows=rows):
                with self.assertRaises(ValueError):
                    LSH(bands, rows)

    def test_incompatible_configuration(self):
        with self.assertRaises(ValueError):
            LSH(bands=3, rows=2).candidate_pairs(["A"], [[1, 2, 3, 4]])

    def test_mismatched_signature_lengths(self):
        with self.assertRaises(ValueError):
            LSH(bands=1, rows=2).candidate_pairs(
                ["A", "B"], [[1, 2], [1, 2, 3]]
            )

    def test_id_and_signature_counts_must_match(self):
        with self.assertRaises(ValueError):
            LSH(bands=1, rows=2).candidate_pairs(["A"], [])

    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError):
            LSH(bands=1, rows=2).candidate_pairs(
                ["A", "A"], [[1, 2], [1, 2]]
            )

    def test_zero_length_signature_rejected(self):
        with self.assertRaises(ValueError):
            LSH(bands=1, rows=1).candidate_pairs(["A"], [[]])


if __name__ == "__main__":
    unittest.main()
