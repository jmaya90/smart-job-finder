from resume.resume_tailor import tailor_resume
import pandas as pd

# Load your resume
with open("../resumes/mechanical_engineer.txt", "r", encoding="utf-8") as f:
    resume_text = f.read()

# Load ranked jobs and pick one
df = pd.read_csv("data/ranked_jobs.csv")
selected_job = df.iloc[0]  # Top match

# Tailor resume
tailored = tailor_resume(resume_text, selected_job["summary"])

# Save the result
with open("../resumes/tailored_resume.txt", "w", encoding="utf-8") as f:
    f.write(tailored)

print("Tailored resume created: resumes/tailored_resume.txt")
