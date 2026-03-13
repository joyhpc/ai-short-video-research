"""Mathematical metric utilities — distance and similarity functions.

Lightweight implementations used by quality checks and the aggregator.
"""

from __future__ import annotations

import math
from typing import Sequence


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Compute cosine similarity between two vectors.

    Args:
        a: First vector.
        b: Second vector (must be same length as *a*).

    Returns:
        Cosine similarity in [-1.0, 1.0].

    Raises:
        ValueError: If the vectors have different lengths or are zero-length.
    """
    if len(a) != len(b):
        raise ValueError(
            f"Vector length mismatch: {len(a)} vs {len(b)}"
        )
    if len(a) == 0:
        raise ValueError("Cannot compute cosine similarity of empty vectors.")

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot / (norm_a * norm_b)


def weighted_average(
    values: Sequence[float],
    weights: Sequence[float],
) -> float:
    """Compute a weighted average.

    Args:
        values: Sequence of values.
        weights: Corresponding weights (must be same length).

    Returns:
        Weighted average.  Returns 0.0 if total weight is zero.

    Raises:
        ValueError: If lengths differ.
    """
    if len(values) != len(weights):
        raise ValueError(
            f"Length mismatch: {len(values)} values vs {len(weights)} weights."
        )

    total_weight = sum(weights)
    if total_weight == 0.0:
        return 0.0

    return sum(v * w for v, w in zip(values, weights)) / total_weight


def bhattacharyya_distance(
    hist_a: Sequence[float],
    hist_b: Sequence[float],
) -> float:
    """Compute Bhattacharyya distance between two normalized histograms.

    Lower values indicate more similar distributions.

    Args:
        hist_a: First normalized histogram.
        hist_b: Second normalized histogram (same length).

    Returns:
        Bhattacharyya distance (non-negative float).
    """
    if len(hist_a) != len(hist_b):
        raise ValueError(
            f"Histogram length mismatch: {len(hist_a)} vs {len(hist_b)}"
        )

    bc = sum(math.sqrt(a * b) for a, b in zip(hist_a, hist_b))
    bc = max(0.0, min(bc, 1.0))  # clamp for numerical stability

    if bc == 0.0:
        return float("inf")

    return -math.log(bc)


def hamming_distance(a: int, b: int) -> int:
    """Compute Hamming distance between two integers (bitwise XOR popcount).

    Used for comparing perceptual hashes (pHash, aHash, dHash).

    Args:
        a: First hash value.
        b: Second hash value.

    Returns:
        Number of differing bits.
    """
    return bin(a ^ b).count("1")
