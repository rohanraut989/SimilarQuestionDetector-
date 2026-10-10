import re


def create_word_set(text):
    """Convert a question text into a set of unique lowercase words.

    Steps:
    1. Convert to lowercase.
    2. Remove punctuation.
    3. Split into words.
    4. Store words in a set to remove duplicates.
    5. Return an empty set if the text is empty.
    """
    if text is None:
        return set()

    cleaned_text = text.strip()
    if cleaned_text == "":
        return set()

    # Lowercase all text, replace punctuation with spaces, then split.
    cleaned_text = cleaned_text.lower()
    cleaned_text = re.sub(r"[^a-z0-9\s]", " ", cleaned_text)
    words = cleaned_text.split()

    # A set removes duplicates automatically.
    return set(words)
