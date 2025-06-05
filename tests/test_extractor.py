from utils.keyword_extractor import extract_keywords_from_text

with open("../resumes/mechanical_engineer.txt", "r", encoding="utf-8") as f:
    resume_text = f.read()

keywords = extract_keywords_from_text(resume_text)

print("Extracted Keywords:")
for kw in keywords:
    print("-", kw)
