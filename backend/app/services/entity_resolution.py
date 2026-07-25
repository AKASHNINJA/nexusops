import re
from typing import Optional
from thefuzz import fuzz

def normalize_company_name(name: str) -> str:
    """Strip common legal suffixes and punctuation for clean matching."""
    cleaned = name.lower()
    cleaned = re.sub(r'\b(inc|inc\.|llc|corp|corp\.|corporation|ltd|ltd\.|technologies|tech|group|co|co\.)\b', '', cleaned)
    cleaned = re.sub(r'[^\w\s]', '', cleaned)
    return cleaned.strip()

def calculate_entity_match_score(
    name_a: str,
    domain_a: Optional[str],
    name_b: str,
    domain_b: Optional[str]
) -> float:
    """
    Calculate a match confidence score (0.0 to 1.0) between two enterprise records.
    Combines domain equality and fuzzy ratio of company names.
    """
    # Direct domain match is a strong signal (95% confidence)
    if domain_a and domain_b and domain_a.lower() == domain_b.lower():
        return 0.96

    norm_a = normalize_company_name(name_a)
    norm_b = normalize_company_name(name_b)

    if norm_a == norm_b:
        return 0.98

    # Fuzzy string matching (Token Sort Ratio)
    ratio = fuzz.token_sort_ratio(norm_a, norm_b) / 100.0

    # Boost score if domains match top-level domain prefix
    if domain_a and domain_b:
        dom_a_prefix = domain_a.split('.')[0]
        dom_b_prefix = domain_b.split('.')[0]
        if dom_a_prefix == dom_b_prefix:
            ratio = min(1.0, ratio + 0.15)

    return round(ratio, 2)
