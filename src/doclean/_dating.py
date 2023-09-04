import dateparser.search


def find_likely_dates(text: str):
    """Find likely dates in text."""
    return dateparser.search.search_dates(
        text, languages=["de"], settings={"STRICT_PARSING": True}
    )
