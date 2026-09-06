import re


# ==========================================
# SKILL DATABASE
# ==========================================

SKILLS = [

    # Programming
    "Python",
    "C++",
    "C#",
    "Java",
    "SQL",
    "R",

    # Web Development
    "HTML",
    "CSS",
    "JavaScript",
    "Flask",
    "Django",

    # AI / ML
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Data Science",

    # Python Libraries
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "TensorFlow",
    "PyTorch",

    # Data / BI
    "Power BI",
    "Tableau",
    "Excel",

    # Engineering Software
    "AutoCAD",
    "SolidWorks",
    "CATIA",
    "ANSYS",
    "MATLAB",
    "RoboDK",
    "GD&T",

    # Automation / Electronics
    "PLC",
    "Arduino",
    "IoT",

    # Development Tools
    "Git",
    "GitHub",

]


# ==========================================
# EXTRACT SKILLS
# ==========================================

def extract_skills(text):

    detected_skills = []

    text_lower = text.lower()


    for skill in SKILLS:

        skill_lower = skill.lower()


        pattern = (
            r"(?<!\w)"
            + re.escape(skill_lower)
            + r"(?!\w)"
        )


        if re.search(pattern, text_lower):

            detected_skills.append(skill)


    return detected_skills