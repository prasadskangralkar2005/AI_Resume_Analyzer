import re


# =========================================================
# ACTION WORD IMPROVEMENTS
# =========================================================

ACTION_REPLACEMENTS = {
    "worked on": "Developed and implemented",
    "worked with": "Utilized",
    "helped": "Contributed to",
    "made": "Designed and developed",
    "did": "Executed",
    "used": "Utilized",
    "responsible for": "Managed and executed",
    "involved in": "Contributed to",
    "participated in": "Collaborated on",
}


# =========================================================
# WEAK PHRASES
# =========================================================

WEAK_PHRASES = [
    "hardworking",
    "good communication skills",
    "quick learner",
    "team player",
    "self motivated",
    "passionate",
    "dedicated",
]


# =========================================================
# SECTION DETECTION
# =========================================================

def detect_sections(resume_text):

    text = resume_text.lower()

    sections = {
        "summary": False,
        "education": False,
        "experience": False,
        "skills": False,
        "projects": False,
        "certifications": False,
        "achievements": False,
    }

    section_keywords = {

        "summary": [
            "summary",
            "profile",
            "objective",
            "career objective",
        ],

        "education": [
            "education",
            "academic",
            "qualification",
        ],

        "experience": [
            "experience",
            "work experience",
            "employment",
            "internship",
        ],

        "skills": [
            "skills",
            "technical skills",
        ],

        "projects": [
            "projects",
            "project",
        ],

        "certifications": [
            "certification",
            "certifications",
            "certificate",
        ],

        "achievements": [
            "achievement",
            "achievements",
            "awards",
        ],
    }

    for section, keywords in section_keywords.items():

        for keyword in keywords:

            if keyword in text:
                sections[section] = True
                break

    return sections


# =========================================================
# ACTION WORD ANALYSIS
# =========================================================

def analyze_action_words(resume_text):

    text_lower = resume_text.lower()

    improvements = []

    for weak_phrase, replacement in ACTION_REPLACEMENTS.items():

        if weak_phrase in text_lower:

            improvements.append({
                "type": "Action Language",
                "issue": f'Weak phrase detected: "{weak_phrase}"',
                "suggestion": (
                    f'Replace it with stronger wording such as '
                    f'"{replacement}".'
                )
            })

    return improvements


# =========================================================
# WEAK PHRASE ANALYSIS
# =========================================================

def analyze_weak_phrases(resume_text):

    text_lower = resume_text.lower()

    improvements = []

    for phrase in WEAK_PHRASES:

        if phrase in text_lower:

            improvements.append({
                "type": "Resume Language",
                "issue": f'Generic phrase detected: "{phrase}"',
                "suggestion": (
                    "Replace generic statements with specific evidence, "
                    "projects, technical skills or measurable achievements."
                )
            })

    return improvements


# =========================================================
# SECTION ANALYSIS
# =========================================================

def analyze_sections(resume_text):

    sections = detect_sections(resume_text)

    improvements = []

    if not sections["summary"]:

        improvements.append({
            "type": "Professional Summary",
            "issue": (
                "No professional summary or career objective detected."
            ),
            "suggestion": (
                "Add a 2-4 line summary highlighting your education, "
                "technical skills, projects and target role."
            )
        })

    if not sections["education"]:

        improvements.append({
            "type": "Education",
            "issue": (
                "Education section was not clearly detected."
            ),
            "suggestion": (
                "Add a clearly labelled Education section with your "
                "degree, institution, CGPA/percentage and graduation year."
            )
        })

    if not sections["skills"]:

        improvements.append({
            "type": "Skills",
            "issue": (
                "Skills section was not clearly detected."
            ),
            "suggestion": (
                "Create a dedicated Technical Skills section containing "
                "relevant programming languages, software and tools."
            )
        })

    if not sections["projects"]:

        improvements.append({
            "type": "Projects",
            "issue": (
                "Projects section was not clearly detected."
            ),
            "suggestion": (
                "Add relevant academic or personal projects and describe "
                "your contribution, technologies used and outcomes."
            )
        })

    if not sections["experience"]:

        improvements.append({
            "type": "Experience",
            "issue": (
                "Experience or internship section was not detected."
            ),
            "suggestion": (
                "If you have internship, training or practical experience, "
                "add it using clear role descriptions and achievements."
            )
        })

    if not sections["certifications"]:

        improvements.append({
            "type": "Certifications",
            "issue": (
                "No certification section was detected."
            ),
            "suggestion": (
                "Add relevant certifications, courses or technical "
                "training that support the target role."
            )
        })

    return improvements


# =========================================================
# JOB KEYWORD ANALYSIS
# =========================================================

def analyze_job_keywords(resume_text, job_description):

    resume_lower = resume_text.lower()
    job_lower = job_description.lower()

    common_keywords = [

        "python",
        "c++",
        "c#",
        "java",
        "sql",
        "flask",
        "django",

        "machine learning",
        "deep learning",
        "artificial intelligence",
        "data science",

        "pandas",
        "numpy",
        "scikit-learn",
        "tensorflow",
        "pytorch",

        "html",
        "css",
        "javascript",

        "git",
        "github",

        "excel",
        "power bi",
        "tableau",

        "autocad",
        "solidworks",
        "catia",
        "ansys",
        "matlab",

        "plc",
        "arduino",
        "iot",
    ]

    missing_keywords = []

    for keyword in common_keywords:

        if keyword in job_lower and keyword not in resume_lower:

            missing_keywords.append(keyword)

    improvements = []

    if missing_keywords:

        improvements.append({
            "type": "Job Keywords",
            "issue": (
                "Important keywords from the job description are missing."
            ),
            "suggestion": (
                "Consider adding relevant skills only if you genuinely "
                "have experience with them: "
                + ", ".join(missing_keywords)
                + "."
            )
        })

    return improvements


# =========================================================
# MEASURABLE ACHIEVEMENT ANALYSIS
# =========================================================

def analyze_achievements(resume_text):

    numbers = re.findall(
        r"\b\d+(?:\.\d+)?%?\b",
        resume_text
    )

    improvements = []

    if len(numbers) < 5:

        improvements.append({
            "type": "Achievements",
            "issue": (
                "Few measurable results were detected."
            ),
            "suggestion": (
                "Add measurable outcomes where possible, such as "
                "percentage improvement, time saved, cost reduction, "
                "accuracy, efficiency or project scale."
            )
        })

    return improvements


# =========================================================
# PROJECT DESCRIPTION ANALYSIS
# =========================================================

def analyze_projects(resume_text):

    text_lower = resume_text.lower()

    improvements = []

    if "projects" in text_lower or "project" in text_lower:

        project_action_words = [

            "designed",
            "developed",
            "implemented",
            "built",
            "created",
            "analyzed",
            "automated",
            "optimized",

        ]

        found = [

            word
            for word in project_action_words
            if word in text_lower

        ]

        if len(found) < 2:

            improvements.append({
                "type": "Project Description",
                "issue": (
                    "Project descriptions may not contain enough "
                    "strong action words."
                ),
                "suggestion": (
                    "Describe each project using the format: "
                    "Action + Technology + Purpose + Result."
                )
            })

    return improvements


# =========================================================
# GENERATE IMPROVEMENTS
# =========================================================

def generate_improvements(
    resume_text,
    job_description=""
):

    improvements = []

    # Action words
    improvements.extend(
        analyze_action_words(resume_text)
    )

    # Weak/generic phrases
    improvements.extend(
        analyze_weak_phrases(resume_text)
    )

    # Resume sections
    improvements.extend(
        analyze_sections(resume_text)
    )

    # Measurable achievements
    improvements.extend(
        analyze_achievements(resume_text)
    )

    # Project descriptions
    improvements.extend(
        analyze_projects(resume_text)
    )

    # Job-specific keywords
    if job_description.strip():

        improvements.extend(
            analyze_job_keywords(
                resume_text,
                job_description
            )
        )

    # -----------------------------------------------------
    # Remove duplicate issues
    # -----------------------------------------------------

    unique_improvements = []

    seen = set()

    for improvement in improvements:

        issue = improvement["issue"]

        if issue not in seen:

            seen.add(issue)

            unique_improvements.append(
                improvement
            )

    return unique_improvements