from operator import itemgetter
from typing import Sequence


def levenhstein_get_closest_matches(word:str, word_list: Sequence[str], threshold=0.6, max_item: int = 2):
    """
    Find the closest matches to a given word from a list of words using
    Levenshtein distance.

    Args:
        word (str): The word to find matches for
        word_list (list): List of words to search through
        threshold (float): Similarity threshold between 0 and 1 (higher is more similar)

    Returns:
        list: Top 2 matching words that exceed the threshold, sorted by similarity
    """
    try:
        import Levenshtein
    except ImportError as err:
        print(err)
        raise ImportError("Please install the Levenshtein package: pip install levenshtein")

    # Calculate similarities
    similarities = []
    for candidate in word_list:
        # Calculate Levenshtein distance
        distance = Levenshtein.ratio(word, candidate)

        # Convert to similarity score (0 to 1)
        max_len = max(len(word), len(candidate))
        if max_len == 0:  # Handle empty strings
            similarity = 1.0 if len(word) == len(candidate) else 0.0
        else:
            similarity = 1.0 - (distance / max_len)

        similarities.append((candidate, similarity))

    # Filter by threshold and sort by similarity (highest first)
    filtered_matches = [match for match in similarities if match[1] >= threshold]
    if not filtered_matches:
        return [m[0] for m in sorted(similarities, key=itemgetter(1))]
    sorted_matches = sorted(filtered_matches, key=lambda x: x[1], reverse=True)

    # Return the top 2 matches (or fewer if not enough matches meet the threshold)
    return [match[0] for match in sorted_matches[:max_item]]