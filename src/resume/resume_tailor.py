import re

def tailor_resume(resume_text, job_summary, keywords=None):
    if keywords is None:
        # Extract terms from job description
        words = re.findall(r'\b\w+\b', job_summary.lower())
        keywords = [w for w in words if len(w) > 3]  # filter short words

    # Weight terms based on frequency
    word_freq = {w: keywords.count(w) for w in set(keywords)}

    # Score each line of resume by match with keywords
    tailored_lines = []
    for line in resume_text.split("\n"):
        score = sum(word_freq.get(w.lower(), 0) for w in line.split())
        tailored_lines.append((score, line))

    # Sort and return lines by descending relevance
    tailored_lines.sort(reverse=True)
    sorted_resume = "\n".join(line for score, line in tailored_lines if line.strip())

    return sorted_resume
