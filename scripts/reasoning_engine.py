
import re


def get_relevant_evidence(question, evidence):
    question_lower = question.lower()

    years = re.findall(
        r"\b(?:19|20)\d{2}\b",
        question_lower
    )

    keywords = [
        word for word in question_lower.split()
        if len(word) > 3
    ]

    scored = []

    for item in evidence:
        title = item.get("title", "").lower()
        text = item.get("text", "").lower()

        combined = title + " " + text
        score = 0

        for year in years:
            if year in title:
                score += 20
            elif year in text:
                score += 5

        for keyword in keywords:
            if keyword in title:
                score += 5
            elif keyword in text:
                score += 1

        if score > 10:
            scored.append((score, item))

    scored.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        item for score, item in scored[:5]
    ]


def extract_winner(text):
    match = re.search(
        r"gold:\s*([A-Za-zÀ-ÿ .'-]+?)(?:\s+goldNOC|\s+silver:|\s+silverNOC|$)",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    return None


def reason(question, evidence):
    relevant = get_relevant_evidence(
        question,
        evidence
    )

    if not relevant:
        return "I could not find sufficiently relevant evidence."

    answers = []

    for item in relevant:
        winner = extract_winner(
            item.get("text", "")
        )

        if winner:
            answers.append(
                item.get("title", "") +
                ": " +
                winner
            )

    if answers:
        return "Comparison:\n\n" + "\n".join(answers)

    return (
        "Relevant sources:\n\n" +
        "\n".join(
            item.get("title", "")
            for item in relevant
        )
    )