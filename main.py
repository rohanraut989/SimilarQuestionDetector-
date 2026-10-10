import itertools
import os
import sys

from preprocessing import create_word_set
from similarity import jaccard_similarity

THRESHOLD = 0.6


def parse_questions_file(file_path):
    """Read and validate the question bank file.

    Format:
    <count>
    <question_id> <question_text>
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.read().splitlines()
    except OSError as error:
        raise ValueError(f"Could not read the file: {error}")

    if not lines:
        raise ValueError("Input file is empty.")

    # First line is the total number of questions.
    try:
        count = int(lines[0].strip())
    except ValueError:
        raise ValueError("Invalid question count in the first line.")

    if count <= 0:
        raise ValueError("Question count must be greater than zero.")

    questions = []
    seen_ids = set()

    for line_number, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue

        parts = line.strip().split(None, 1)
        if len(parts) != 2:
            raise ValueError(f"Malformed line {line_number}: '{line}'")

        question_id, question_text = parts

        if question_id in seen_ids:
            raise ValueError(f"Duplicate question ID found: {question_id}")

        seen_ids.add(question_id)
        questions.append((question_id, question_text))

    if len(questions) != count:
        raise ValueError(
            f"Expected {count} questions, but found {len(questions)} valid entries."
        )

    return questions


def main():
    file_path = "questions.txt"

    try:
        questions = parse_questions_file(file_path)
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        return 1

    print("Question bank loaded successfully.")
    print("=" * 50)

    similar_pairs = []

    # Build word sets for each question and print them.
    word_sets = {}
    for question_id, text in questions:
        word_set = create_word_set(text)
        word_sets[question_id] = word_set
        print(f"{question_id} word set: {word_set}")

    print("\nPairwise Jaccard similarity:")

    # Compare every unique pair without repeating the same pair twice.
    for first_id, second_id in itertools.combinations(word_sets.keys(), 2):
        set_a = word_sets[first_id]
        set_b = word_sets[second_id]

        score = jaccard_similarity(set_a, set_b)
        is_similar = score >= THRESHOLD

        print(f"{first_id} vs {second_id}: {score:.4f} -> {'SIMILAR' if is_similar else 'NOT SIMILAR'}")

        if is_similar:
            similar_pairs.append((first_id, second_id, score))

    print("\nFinal similar question pairs:")
    if not similar_pairs:
        print("No similar pairs found.")
    else:
        for first_id, second_id, score in similar_pairs:
            print(f"SIMILAR {first_id} {second_id} {score:.2f}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
