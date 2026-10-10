
def jaccard_similarity(set_a, set_b):
    """Return the Jaccard similarity of two sets.

    Formula: intersection / union
    """
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0

    intersection = set_a & set_b
    union = set_a | set_b

    # Avoid division by zero. The earlier checks already handle empty sets.
    return float(len(intersection) / len(union))
