import re


def calculate_ats_score(resume_text):
    """
    Analyze a resume and calculate an ATS-style score.
    """

    text = resume_text.strip()
    text_lower = text.lower()

    score = 0
    checks = []

    # --------------------------------------------------
    # 1. Contact Information
    # --------------------------------------------------

    email_found = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    phone_found = re.search(
        r"(?:\+91[\s-]?)?[6-9]\d{9}",
        text
    )

    contact_score = 0

    if email_found:
        contact_score += 5

    if phone_found:
        contact_score += 5

    score += contact_score

    checks.append({
        "category": "Contact Information",
        "score": contact_score,
        "max_score": 10,
        "status": contact_score == 10
    })

    # --------------------------------------------------
    # 2. Resume Sections
    # --------------------------------------------------

    sections = {
        "Education": [
            "education",
            "academic",
            "qualification"
        ],

        "Experience": [
            "experience",
            "work experience",
            "employment",
            "internship"
        ],

        "Skills": [
            "skills",
            "technical skills",
            "skills & abilities"
        ],

        "Projects": [
            "projects",
            "project"
        ]
    }

    section_score = 0

    for section_name, keywords in sections.items():

        found = any(
            keyword in text_lower
            for keyword in keywords
        )

        if found:
            section_score += 5

    score += section_score

    checks.append({
        "category": "Resume Sections",
        "score": section_score,
        "max_score": 20,
        "status": section_score == 20
    })

    # --------------------------------------------------
    # 3. Resume Length
    # --------------------------------------------------

    word_count = len(text.split())

    if 300 <= word_count <= 1000:
        length_score = 10
    elif 200 <= word_count < 300:
        length_score = 7
    elif 100 <= word_count < 200:
        length_score = 4
    else:
        length_score = 2

    score += length_score

    checks.append({
        "category": "Resume Length",
        "score": length_score,
        "max_score": 10,
        "status": length_score >= 7
    })

    # --------------------------------------------------
    # 4. Action Keywords
    # --------------------------------------------------

    action_words = [
        "developed",
        "designed",
        "implemented",
        "created",
        "analyzed",
        "managed",
        "improved",
        "developed",
        "optimized",
        "automated",
        "built",
        "tested",
        "engineered",
        "implemented",
        "led"
    ]

    action_words_found = [
        word for word in action_words
        if re.search(r"\b" + word + r"\b", text_lower)
    ]

    if len(action_words_found) >= 8:
        action_score = 10
    elif len(action_words_found) >= 5:
        action_score = 7
    elif len(action_words_found) >= 3:
        action_score = 5
    else:
        action_score = 2

    score += action_score

    checks.append({
        "category": "Action Keywords",
        "score": action_score,
        "max_score": 10,
        "status": action_score >= 7
    })

    # --------------------------------------------------
    # 5. Technical Keywords
    # --------------------------------------------------

    technical_keywords = [
        "python",
        "c++",
        "c#",
        "java",
        "sql",
        "machine learning",
        "artificial intelligence",
        "data science",
        "flask",
        "html",
        "css",
        "javascript",
        "solidworks",
        "autocad",
        "ansys",
        "matlab",
        "plc",
        "arduino",
        "git",
        "github"
    ]

    technical_found = [
        skill for skill in technical_keywords
        if skill in text_lower
    ]

    if len(technical_found) >= 8:
        technical_score = 15
    elif len(technical_found) >= 5:
        technical_score = 12
    elif len(technical_found) >= 3:
        technical_score = 8
    else:
        technical_score = 4

    score += technical_score

    checks.append({
        "category": "Technical Keywords",
        "score": technical_score,
        "max_score": 15,
        "status": technical_score >= 8
    })

    # --------------------------------------------------
    # 6. Quantifiable Achievements
    # --------------------------------------------------

    numbers_found = re.findall(
        r"\b\d+(?:\.\d+)?%?\b",
        text
    )

    if len(numbers_found) >= 8:
        achievement_score = 10
    elif len(numbers_found) >= 5:
        achievement_score = 7
    elif len(numbers_found) >= 2:
        achievement_score = 5
    else:
        achievement_score = 2

    score += achievement_score

    checks.append({
        "category": "Quantifiable Results",
        "score": achievement_score,
        "max_score": 10,
        "status": achievement_score >= 7
    })

    # --------------------------------------------------
    # 7. Formatting / Readability
    # --------------------------------------------------

    formatting_score = 0

    if len(text.splitlines()) >= 10:
        formatting_score += 3

    if "@" in text:
        formatting_score += 2

    if any(char.isdigit() for char in text):
        formatting_score += 2

    if "linkedin" in text_lower:
        formatting_score += 2

    if "github" in text_lower:
        formatting_score += 1

    formatting_score = min(formatting_score, 10)

    score += formatting_score

    checks.append({
        "category": "ATS Readability",
        "score": formatting_score,
        "max_score": 10,
        "status": formatting_score >= 7
    })

    # --------------------------------------------------
    # Final Score
    # --------------------------------------------------

    score = min(score, 100)

    # --------------------------------------------------
    # Recommendations
    # --------------------------------------------------

    recommendations = []

    if not email_found:
        recommendations.append(
            "Add a professional email address."
        )

    if not phone_found:
        recommendations.append(
            "Add a valid phone number."
        )

    if "education" not in text_lower:
        recommendations.append(
            "Add a clearly labelled Education section."
        )

    if "skills" not in text_lower:
        recommendations.append(
            "Add a clearly labelled Skills section."
        )

    if "projects" not in text_lower:
        recommendations.append(
            "Add a Projects section to showcase practical work."
        )

    if len(action_words_found) < 5:
        recommendations.append(
            "Use stronger action words such as Designed, Developed, Implemented and Optimized."
        )

    if len(technical_found) < 5:
        recommendations.append(
            "Add relevant technical skills and tools related to your target role."
        )

    if len(numbers_found) < 5:
        recommendations.append(
            "Add measurable results such as percentages, quantities, time saved or performance improvements."
        )

    if "linkedin" not in text_lower:
        recommendations.append(
            "Consider adding your LinkedIn profile."
        )

    if "github" not in text_lower:
        recommendations.append(
            "Consider adding GitHub if you have relevant software projects."
        )

    # --------------------------------------------------
    # Score Message
    # --------------------------------------------------

    if score >= 80:
        message = "Excellent ATS readiness! Your resume is well structured and contains strong searchable content."

    elif score >= 60:
        message = "Good ATS readiness. A few improvements can make your resume more competitive."

    elif score >= 40:
        message = "Moderate ATS readiness. Several areas of your resume can be improved."

    else:
        message = "Your resume needs significant improvement for better ATS compatibility."

    return {
        "score": score,
        "message": message,
        "checks": checks,
        "recommendations": recommendations,
        "word_count": word_count,
        "technical_keywords": technical_found,
        "action_keywords": action_words_found
    }