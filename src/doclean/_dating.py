import dateparser.search


def find_likely_dates(text: str):
    """Find likely dates in text."""
    return dateparser.search.search_dates(
        text, languages=["de"], settings={"STRICT_PARSING": True}
    )


if __name__ == "__main__":
    print(find_likely_dates("Dies war am 13. Juni 2023 und dann trafen sie sich."))
