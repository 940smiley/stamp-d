import re


def parse_title(title: str):
    """Extract probable year, country and denomination from an eBay title."""
    if not title:
        return "", "", ""

    # Find year like 1850, 1999, 2012 etc
    year_match = re.search(r"(18|19|20)\d{2}", title)
    year = year_match.group(0) if year_match else ""

    # Try to locate a denomination such as '5c', '10 p', '2.50$', etc.
    denom_pattern = (
        r"\b\d+(?:[.,]\d+)?\s?"
        r"(?:c|¢|p|d|fr|pf|\$|€|£|kr|sen|yen|mk|cts?|cent|cents)\b"
    )
    denom_match = re.search(denom_pattern, title, re.IGNORECASE)
    denom = denom_match.group(0).strip() if denom_match else ""

    # Guess country using words around the year/denomination
    country = ""
    if year_match:
        before = title[: year_match.start()]
        after = title[year_match.end():]
        before_words = [
            w for w in re.sub(r"[^A-Za-z ]+", " ", before).split() if w
        ]
        if before_words:
            filtered = [
                w
                for w in before_words
                if not re.match(r"^\d", w)
                and not re.fullmatch(
                    r"c|¢|p|d|fr|pf|kr|sen|yen|mk|cts?|cent|cents",
                    w.lower(),
                )
            ]
            if filtered:
                before_words = filtered
            country = " ".join(before_words[-3:])
        else:
            after_clean = re.sub(r"[^A-Za-z0-9 ]+", " ", after)
            after_tokens = after_clean.split()
            result_words: list[str] = []
            for w in after_tokens:
                if any(ch.isdigit() for ch in w):
                    break
                if w.lower() in {"stamp", "stamps"}:
                    break
                result_words.append(w)
                if len(result_words) >= 3:
                    break
            if result_words:
denom = denom_match.group(0).strip() if denom_match else ""

    # Guess country using words around the year/denomination
    country = extract_country(title, year_match, denom_match)

    if not country:
    elif denom_match:
        before = title[: denom_match.start()]
        before_words = [
            w for w in re.sub(r"[^A-Za-z ]+", " ", before).split() if w
        ]
        if before_words:
            filtered = [
                w
                for w in before_words
                if not re.match(r"^\d", w)
                and not re.fullmatch(
                    r"c|¢|p|d|fr|pf|kr|sen|yen|mk|cts?|cent|cents",
                    w.lower(),
                )
            ]
            if filtered:
                before_words = filtered
            country = " ".join(before_words[-3:])

    if not country:
        tokens = [
            t for t in re.sub(r"[^A-Za-z ]+", " ", title).split() if t
        ]
        if tokens:
            country = tokens[0]

    return year, country.title(), denom
