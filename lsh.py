"""Locality-Sensitive Hashing (LSH) candidate generation for MinHash signatures.

LSH divides each signature into bands. Questions with an identical band share
a bucket and become a candidate pair. This is a probabilistic filter: it can
miss similar questions, so candidate pairs still need exact verification later.
"""

from itertools import combinations


class LSH:
    """Group IDs by matching MinHash bands and generate unique candidate pairs.

    `candidate_pairs(question_ids, signatures)` returns a sorted list of
    `(id_a, id_b)` tuples. IDs in each tuple are ordered deterministically;
    only pairs that share at least one full band are included.

    All signatures must have length `bands * rows`. IDs should be unique
    strings, as in the question-bank input format.
    """

    def __init__(self, bands, rows):
        if type(bands) is not int or bands < 1:
            raise ValueError("bands must be a positive integer.")
        if type(rows) is not int or rows < 1:
            raise ValueError("rows must be a positive integer.")

        self.bands = bands
        self.rows = rows

    def candidate_pairs(self, question_ids, signatures):
        """Return deterministic, duplicate-free candidate ID pairs.

        `question_ids[i]` belongs to `signatures[i]`. Each signature is sliced
        into `bands` consecutive pieces of `rows` values. A bucket key consists
        of its band number and the tuple of values in that band.
        """
        if len(question_ids) != len(signatures):
            raise ValueError("Provide exactly one signature for each question ID.")
        if not question_ids:
            return []

        seen_ids = set()
        for question_id in question_ids:
            if not isinstance(question_id, str):
                raise ValueError("Question IDs must be strings.")
            if question_id in seen_ids:
                raise ValueError("Question IDs must be unique: %r." % question_id)
            seen_ids.add(question_id)

        signature_length = len(signatures[0])
        if signature_length == 0:
            raise ValueError("Signatures must not be empty.")
        if self.bands * self.rows != signature_length:
            raise ValueError(
                "bands * rows must equal signature length (%d * %d != %d)."
                % (self.bands, self.rows, signature_length)
            )
        if any(len(signature) != signature_length for signature in signatures):
            raise ValueError("All signatures must have the same length.")

        buckets = {}
        for question_id, signature in zip(question_ids, signatures):
            for band_index in range(self.bands):
                start = band_index * self.rows
                end = start + self.rows
                # Dict keys group identical band tuples into the same bucket.
                bucket_key = (band_index, tuple(signature[start:end]))
                buckets.setdefault(bucket_key, []).append(question_id)

        # A set ensures that a pair sharing multiple bands appears only once.
        candidates = set()
        for members in buckets.values():
            if len(members) > 1:
                for id_a, id_b in combinations(sorted(members), 2):
                    candidates.add((id_a, id_b))

        # Return a predictable order independent of dictionary/bucket iteration.
        return sorted(candidates)


def _run_demo():
    """Demonstrate LSH using signatures from the project's MinHasher."""
    from minhash import MinHasher

    questions = [
        ("R1", {"explain", "stack", "operations", "with", "example"}),
        ("R2", {"explain", "queue", "operations", "with", "example"}),
        ("R3", {"define", "normalization"}),
        ("R4", {"explain", "stack", "operations", "with", "example"}),
    ]

    # Use the same MinHasher so every question is signed by the same functions.
    hasher = MinHasher(num_hashes=128, seed=42)
    question_ids = [question_id for question_id, _ in questions]
    signatures = [hasher.signature(words) for _, words in questions]

    # Two rows per band makes this small demo likely to include R1/R2.
    lsh = LSH(bands=64, rows=2)
    candidates = lsh.candidate_pairs(question_ids, signatures)

    print("LSH demonstration (128-value signatures, 64 bands x 2 rows)")
    print("Candidate ID pairs:")
    if candidates:
        for id_a, id_b in candidates:
            print("%s %s" % (id_a, id_b))
    else:
        print("No candidates")
    print("LSH creates candidates only; it does not guarantee every similar pair is found.")


if __name__ == "__main__":
    _run_demo()
