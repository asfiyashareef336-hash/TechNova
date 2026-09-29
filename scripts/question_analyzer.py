import re


def analyze_question(question):
    question_lower = question.lower()

    question_type = "general"

    if any(word in question_lower for word in [
        "compare", "difference", "versus", "vs"
    ]):
        question_type = "comparison"

    elif any(word in question_lower for word in [
        "how many", "count", "number of"
    ]):
        question_type = "count"

    elif any(word in question_lower for word in [
        "who won", "winner", "champion", "gold medal"
    ]):
        question_type = "winner"

    years = re.findall(
        r"\b(?:19|20)\d{2}\b",
        question_lower
    )

    return {
        "question": question,
        "question_type": question_type,
        "years": years,
        "keywords": question_lower.split()
    }