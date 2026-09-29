def verify_evidence(question, evidence):
    question_words = set(question.lower().split())

    verified = []

    for item in evidence:
        title = item.get("title", "").lower()
        text = item.get("text", "").lower()

        combined_text = title + " " + text

        matching_words = 0

        for word in question_words:
            if len(word) > 3 and word in combined_text:
                matching_words += 1

        if matching_words > 0:
            verified.append(item)

    return verified