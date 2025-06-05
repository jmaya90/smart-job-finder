import spacy

# Expanded and normalized exclusion list
EXCLUDE_TERMS = {
    "project", "team", "work", "year", "email", "phone", "location", "new",
    "education", "learning", "experience", "college", "univ", "linkedin",
    "technical", "languages", "degree", "skills", "profile", "field", "area",
    "tools", "tasks", "support", "system", "development", "method", "part",
    "solution", "sebastian", "juan", "maya", "langara", "herragro", "makroing",
    "manizales", "national", "s.a.s", "pgwp", "canada", "b.sc", "post",
    "colombia", "westminster", "office", "order", "information", "design", "designer", "management",
    "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"
}


def extract_keywords_from_text(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    keywords = set()

    for token in doc:
        if (
            token.pos_ in {"NOUN", "PROPN"}
            and not token.is_stop
            and token.is_alpha
        ):
            word = token.lemma_.lower().strip()
            if len(word) > 2 and word not in EXCLUDE_TERMS:
                keywords.add(word)

    return sorted(keywords)
