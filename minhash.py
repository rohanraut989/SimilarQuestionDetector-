"""Create and compare MinHash signatures for question word sets.

MinHash compresses a word set into a fixed-length list of integers. The
fraction of matching positions in two signatures estimates their Jaccard
similarity.
"""

import hashlib
import random


# A large prime used by the simple universal hash functions below.
_PRIME = (1 << 61) - 1

# Real hash values are always smaller than this value, so it marks empty sets.
_EMPTY_VALUE = _PRIME


class MinHasher:
    """Generate reproducible signatures using a fixed family of hash functions.

    Create one MinHasher and reuse it for every question. Its seeded parameters
    ensure that each question is measured using the same hash functions.
    """

    def __init__(self, num_hashes=128, seed=42):
        if not isinstance(num_hashes, int) or num_hashes < 1:
            raise ValueError("num_hashes must be a positive integer.")

        self.num_hashes = num_hashes
        generator = random.Random(seed)

        # Each hash function is h(x) = (a*x + b) mod prime.
        self._parameters = [
            (generator.randrange(1, _PRIME), generator.randrange(0, _PRIME))
            for _ in range(num_hashes)
        ]

        # Cache each word's stable integer hash to avoid hashing it repeatedly.
        self._word_hashes = {}

    def _word_to_integer(self, word):
        """Convert a word to a stable integer (unlike Python's hash())."""
        if word not in self._word_hashes:
            digest = hashlib.blake2b(word.encode("utf-8"), digest_size=8).digest()
            self._word_hashes[word] = int.from_bytes(digest, "big") % _PRIME
        return self._word_hashes[word]

    def signature(self, word_set):
        """Return a MinHash signature list for a set of words."""
        if not word_set:
            # Keep the signature length consistent, even for empty questions.
            return [_EMPTY_VALUE] * self.num_hashes

        word_values = [self._word_to_integer(word) for word in word_set]
        signature = []

        # For each hash function, keep its minimum value over all words.
        for a, b in self._parameters:
            signature.append(min((a * value + b) % _PRIME for value in word_values))

        return signature


def generate_signature(word_set, num_hashes=128, seed=42):
    """Convenience function to create one reproducible signature.

    For processing multiple questions, instantiate MinHasher once and call its
    signature() method for every question so they all use the same parameters.
    """
    return MinHasher(num_hashes=num_hashes, seed=seed).signature(word_set)


def estimate_jaccard(signature_a, signature_b):
    """Estimate Jaccard similarity as the fraction of equal positions.

    Two empty-set signatures estimate to 1.0. One empty-set signature compared
    with a non-empty signature estimates to 0.0.
    """
    if len(signature_a) != len(signature_b):
        raise ValueError("Signatures must have the same length.")
    if not signature_a:
        raise ValueError("Signatures must not be empty.")

    a_is_empty = all(value == _EMPTY_VALUE for value in signature_a)
    b_is_empty = all(value == _EMPTY_VALUE for value in signature_b)
    if a_is_empty and b_is_empty:
        return 1.0
    if a_is_empty or b_is_empty:
        return 0.0

    matches = sum(a == b for a, b in zip(signature_a, signature_b))
    return matches / len(signature_a)


def _run_demo():
    """Run small reproducible checks when this file is executed directly."""
    hasher = MinHasher(num_hashes=128, seed=42)
    identical = {"explain", "stack", "operations", "example"}
    similar = {"explain", "queue", "operations", "example"}
    dissimilar = {"database", "normalization", "entity"}

    identical_signature = hasher.signature(identical)
    similar_signature = hasher.signature(similar)
    dissimilar_signature = hasher.signature(dissimilar)

    assert identical_signature == hasher.signature(identical)
    assert estimate_jaccard(identical_signature, identical_signature) == 1.0

    similar_score = estimate_jaccard(identical_signature, similar_signature)
    dissimilar_score = estimate_jaccard(identical_signature, dissimilar_signature)
    assert similar_score > dissimilar_score

    print("MinHash demonstration (128 hash functions, seed 42)")
    print("Identical sets, matching positions: 128/128")
    print("Similar sets, estimated Jaccard:   %.4f" % similar_score)
    print("Dissimilar sets, estimated Jaccard: %.4f" % dissimilar_score)
    print("Demo checks passed.")


if __name__ == "__main__":
    _run_demo()
