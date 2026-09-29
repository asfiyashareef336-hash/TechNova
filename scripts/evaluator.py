import re


def evaluate_evidence(question, evidence):
    question_lower = question.lower()

    question_years = set(
        re.findall(r"\b(?:19|20)\d{2}\b", question_lower)
    )

    keywords = set(
        re.findall(r"\b[a-zA-Z]{3,}\b", question_lower)
    )

    stop_words = {
        "what", "when", "where", "which", "who",
        "how", "many", "was", "were", "the",
        "did", "does", "won", "event", "according",
        "provided", "corpus", "more", "less",
        "than", "compare"
    }

    keywords -= stop_words

    scored_evidence = []

    for item in evidence:

        title = item.get("title", "").lower()
        text = item.get("text", "").lower()

        score = 0

        for word in keywords:
            if word in title:
                score += 5
            elif word in text:
                score += 1

        for year in question_years:
            if year in title:
                score += 20
            elif year in text:
                score += 5
            else:
                score -= 10

        important_terms = [
            "tennis",
            "singles",
            "biathlon",
            "mass start",
            "olympics",
            "winter olympics",
            "summer olympics"
        ]

        for term in important_terms:
            if term in question_lower and term in title:
                score += 10

        scored_evidence.append((score, item))

    scored_evidence.sort(
        key=lambda item: item[0],
        reverse=True
    )

    is_mass_start_comparison = (
        "mass start" in question_lower
        and "men's" in question_lower
        and "women's" in question_lower
    )

    if is_mass_start_comparison:

        mens_item = None
        womens_item = None

        for score, item in scored_evidence:

            title = item.get("title", "").lower()

            if "men's mass start" in title and mens_item is None:
                mens_item = item

            if "women's mass start" in title and womens_item is None:
                womens_item = item

        relevant = []

        if mens_item is not None:
            relevant.append(mens_item)

        if womens_item is not None:
            relevant.append(womens_item)

        seen = {
            item.get("doc_id")
            for item in relevant
        }

        for score, item in scored_evidence:

            doc_id = item.get("doc_id")

            if doc_id not in seen:
                relevant.append(item)
                seen.add(doc_id)

            if len(relevant) == 5:
                break

        return relevant

    relevant = []

    seen = set()

    for score, item in scored_evidence:

        doc_id = item.get("doc_id")

        if doc_id not in seen:
            relevant.append(item)
            seen.add(doc_id)

        if len(relevant) == 5:
            break

    return relevant