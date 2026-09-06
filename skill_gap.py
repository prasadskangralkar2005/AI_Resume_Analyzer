# =========================================================
# SKILL GAP ANALYSIS
# =========================================================

def analyze_skill_gaps(missing_skills):

    recommendations = {

        "Python":
            "Strengthen Python programming through practical projects.",

        "C++":
            "Practice C++ programming, OOP and problem solving.",

        "C#":
            "Learn C# fundamentals, OOP and .NET development.",

        "Java":
            "Learn Java programming, OOP and application development.",

        "SQL":
            "Practice SQL queries, joins, subqueries and database design.",

        "HTML":
            "Improve HTML by building responsive web pages.",

        "CSS":
            "Practice modern CSS, Flexbox, Grid and responsive design.",

        "JavaScript":
            "Learn JavaScript fundamentals, DOM manipulation and APIs.",

        "Flask":
            "Build Python web applications using Flask and REST APIs.",

        "Django":
            "Learn Django fundamentals and build database-driven web applications.",

        "Machine Learning":
            "Study supervised and unsupervised learning and build ML projects.",

        "Deep Learning":
            "Learn neural networks and frameworks such as TensorFlow or PyTorch.",

        "Artificial Intelligence":
            "Strengthen AI fundamentals and build practical AI applications.",

        "Data Science":
            "Learn data analysis, visualization and statistical techniques.",

        "Pandas":
            "Practice data cleaning, manipulation and analysis using Pandas.",

        "NumPy":
            "Learn NumPy arrays, mathematical operations and numerical computing.",

        "Scikit-learn":
            "Build machine learning models using Scikit-learn.",

        "TensorFlow":
            "Learn TensorFlow and build basic neural-network projects.",

        "PyTorch":
            "Learn PyTorch for deep learning and neural-network development.",

        "Git":
            "Learn Git commands, branching, commits and version control.",

        "GitHub":
            "Practice GitHub repositories, pull requests and collaborative development.",

        "Power BI":
            "Learn Power BI dashboards, data modeling and visualization.",

        "Tableau":
            "Practice creating interactive dashboards using Tableau.",

        "Excel":
            "Improve Excel skills including formulas, PivotTables and data analysis.",

        "AutoCAD":
            "Practice 2D drafting, 3D modeling and engineering drawings in AutoCAD.",

        "SolidWorks":
            "Practice 3D CAD modeling, assemblies and engineering drawings in SolidWorks.",

        "CATIA":
            "Learn 3D modeling, assemblies and surface design using CATIA.",

        "ANSYS":
            "Practice finite element analysis and engineering simulations using ANSYS.",

        "MATLAB":
            "Practice MATLAB programming, numerical analysis and engineering simulations.",

        "RoboDK":
            "Learn robotic simulation, programming and offline robot programming using RoboDK.",

        "GD&T":
            "Study geometric dimensioning and tolerancing standards and applications.",

        "PLC":
            "Learn PLC programming, ladder logic and industrial automation.",

        "Arduino":
            "Build Arduino-based electronics and automation projects.",

        "IoT":
            "Learn IoT architecture, sensors, communication protocols and cloud integration."
    }


    skill_gap_data = []


    for skill in missing_skills:

        recommendation = recommendations.get(
            skill,
            f"Develop practical knowledge and complete a project using {skill}."
        )

        skill_gap_data.append({

            "skill": skill,

            "importance": "High",

            "recommendation": recommendation

        })


    return skill_gap_data