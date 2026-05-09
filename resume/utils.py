import re
import pdfplumber

# ================= CONFIG =================

SKILL_KEYWORDS = [
    "python", "django", "flask", "java", "c++",
    "html", "css", "javascript", "react",
    "sql", "mysql", "mongodb", "postgresql",
    "git", "docker", "aws", "rest api"
]

JOB_TITLES = [
    "software engineer", "python developer", "django developer",
    "web developer", "backend developer", "frontend developer",
    "full stack developer", "data analyst", "intern", "trainee"
]

EDUCATION_KEYWORDS = [
    "b.tech", "btech", "b.e", "be",
    "b.sc", "bsc", "m.sc", "msc",
    "mca", "mba", "phd", "diploma",
    "computer science", "information technology",
    "engineering", "university", "college", "institute"
]
# ================= TEXT =================

def extract_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

# ================= NAME =================

def extract_name(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:12]:
        if not re.match(r"^[A-Za-z ]+$", line):
            continue
        words = line.split()
        if not 2 <= len(words) <= 4:
            continue
        lower = line.lower()
        if any(j in lower for j in JOB_TITLES):
            continue
        if any(w in lower for w in ["developer", "engineer", "intern"]):
            continue
        return line
    return ""

# ================= JOB TITLE =================

def extract_job_title(text):
    lower = text.lower()
    for title in JOB_TITLES:
        if title in lower:
            return title.title()
    return ""

# ================= CONTACT =================

def extract_email(text):
    m = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return m.group(0) if m else ""

def extract_phone(text):
    m = re.search(r"(\+?\d[\d\s\-]{8,}\d)", text)
    return m.group(0) if m else ""

# ================= SKILLS =================

def extract_skills(text):
    text = text.lower()
    return [s for s in SKILL_KEYWORDS if re.search(rf"\b{s}\b", text)]

# ================= EXPERIENCE =================

def extract_experience(text):
    text = text.lower()
    if re.search(r"\bfresher\b|\bentry level\b", text):
        return {"type": "fresher", "years": "0"}
    years = re.findall(r"(\d+\+?\s*(?:years?|yrs?))", text)
    if years:
        return {"type": "experienced", "years": ", ".join(set(years))}
    return {"type": "", "years": ""}

# ================= PROJECTS =================

def extract_projects(text):
    projects = []
    for line in text.splitlines():
        l = line.lower()
        if len(line.split()) >= 4 and any(w in l for w in ["project", "developed", "built"]):
            projects.append(line.strip())
    return list(dict.fromkeys(projects))



# ================= EDUCATION =================

def extract_education(text):
    education = []
    for line in text.splitlines():
        l = line.lower()

        # must contain degree or institute keyword
        if any(k in l for k in EDUCATION_KEYWORDS):
            # avoid skill lines
            if len(line.split()) < 4:
                continue

            # clean bullets/symbols
            clean = re.sub(r"^[•\-\*]+", "", line).strip()

            if clean and clean not in education:
                education.append(clean)

    return education

# ================= MAIN =================

def parse_resume(file):
    text = extract_text(file)
    exp = extract_experience(text)
    return {
        "name": extract_name(text),
        "job_title": extract_job_title(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "experience_type": exp["type"],
        "experience_years": exp["years"],
        "projects": extract_projects(text),
        "education": extract_education(text),
    }

def calculate_ats(data):
    score = 0
    missing = []

    if data["name"]: score += 10
    else: missing.append("name")

    if data["job_title"]: score += 10
    else: missing.append("job_title")

    if data["email"]: score += 10
    else: missing.append("email")

    if data["phone"]: score += 10
    else: missing.append("phone")

    score += min(len(data["skills"]) * 5, 30)
    if not data["skills"]: missing.append("skills")

    if data["experience_type"]: score += 20
    else: missing.append("experience")

    if data["projects"]: score += 10
    else: missing.append("projects")

    if data.get("education"):
        score += 15
    else:
        missing.append("education")

    return {"score": score, "missing": missing}