from flask import Flask, render_template, request, redirect, url_for, session
import pymupdf
import bcrypt
from datetime import datetime, timedelta

from skill_extractor import extract_skills
from matcher import calculate_similarity
from skill_gap import analyze_skill_gaps
from ats_analyzer import calculate_ats_score
from resume_improver import generate_improvements

from ai_assistant import (
    analyze_resume_with_ai,
    ask_resume_question
)

from database import get_db_connection
from otp import generate_otp, send_otp


app = Flask(__name__)

# Used for Flask sessions
app.secret_key = "resume-ai-development-secret-key"


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():
    # Opening the application always starts with registration
    return redirect(url_for("register"))


# =========================================================
# UPLOAD PAGE
# =========================================================

@app.route("/upload")
def upload():
    # Resume upload is available only after login
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("upload.html")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    # -----------------------------------------------------
    # Validation
    # -----------------------------------------------------

    if not name:
        return render_template(
            "register.html",
            error="Please enter your name."
        )

    if not email:
        return render_template(
            "register.html",
            error="Please enter your email."
        )

    if not password:
        return render_template(
            "register.html",
            error="Please enter a password."
        )

    if len(password) < 8:
        return render_template(
            "register.html",
            error="Password must contain at least 8 characters."
        )

    # -----------------------------------------------------
    # Connect to MySQL
    # -----------------------------------------------------

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # Check whether email already exists
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT id, is_verified
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            if existing_user["is_verified"]:

                return render_template(
                    "register.html",
                    error="An account with this email already exists."
                )

            # Delete old unverified account
            cursor.execute(
                """
                DELETE FROM users
                WHERE email = %s
                """,
                (email,)
            )

            connection.commit()

        # -------------------------------------------------
        # Hash password
        # -------------------------------------------------

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # -------------------------------------------------
        # Generate OTP
        # -------------------------------------------------

        otp = generate_otp()

        otp_expiry = datetime.now() + timedelta(minutes=5)

        # -------------------------------------------------
        # Save user
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password_hash,
                is_verified,
                otp,
                otp_expiry
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                name,
                email,
                password_hash,
                False,
                otp,
                otp_expiry
            )
        )

        connection.commit()

        # -------------------------------------------------
        # Save email in session
        # -------------------------------------------------

        session["verification_email"] = email

        # -------------------------------------------------
        # Send OTP
        # -------------------------------------------------

        try:

            send_otp(
                email,
                otp
            )

        except Exception as e:

            # Remove user if email could not be sent
            cursor.execute(
                """
                DELETE FROM users
                WHERE email = %s
                """,
                (email,)
            )

            connection.commit()

            return render_template(
                "register.html",
                error=f"Could not send OTP: {str(e)}"
            )

        # -------------------------------------------------
        # Redirect to OTP verification
        # -------------------------------------------------

        return redirect(
            url_for("verify_otp")
        )

    except Exception as e:

        return render_template(
            "register.html",
            error=f"Registration error: {str(e)}"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# VERIFY OTP
# =========================================================

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():

    email = session.get("verification_email")

    if not email:
        return redirect(url_for("register"))

    if request.method == "POST":

        entered_otp = request.form.get("otp", "").strip()

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, otp, otp_expiry
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user:
            cursor.close()
            db.close()

            return render_template(
                "verify_otp.html",
                email=email,
                error="Account not found. Please register again."
            )

        # Check OTP
        if not entered_otp:
            cursor.close()
            db.close()

            return render_template(
                "verify_otp.html",
                email=email,
                error="Please enter the 6-digit OTP."
            )

        if entered_otp != user["otp"]:
            cursor.close()
            db.close()

            return render_template(
                "verify_otp.html",
                email=email,
                error="Invalid OTP. Please check your email and try again."
            )

        # Check OTP expiry
        if user["otp_expiry"] is None:
            cursor.close()
            db.close()

            return render_template(
                "verify_otp.html",
                email=email,
                error="OTP is invalid. Please request a new OTP."
            )

        from datetime import datetime

        if datetime.now() > user["otp_expiry"]:
            cursor.close()
            db.close()

            return render_template(
                "verify_otp.html",
                email=email,
                error="OTP has expired. Please request a new OTP."
            )

        # Verify user
        cursor.execute(
            """
            UPDATE users
            SET is_verified = TRUE,
                otp = NULL,
                otp_expiry = NULL
            WHERE id = %s
            """,
            (user["id"],)
        )

        db.commit()

        cursor.close()
        db.close()

        # Clear verification session
        session.pop("verification_email", None)

        # Send user to login page
        return redirect(
            url_for(
                "login",
                verified="1"
            )
        )

    return render_template(
        "verify_otp.html",
        email=email
    )


# =========================================================
# RESEND OTP
# =========================================================

@app.route("/resend-otp", methods=["POST"])
def resend_otp():

    email = session.get(
        "verification_email"
    )

    if not email:

        return redirect(
            url_for("register")
        )

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT id, is_verified
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user:

            return redirect(
                url_for("register")
            )

        if user["is_verified"]:

            return redirect(
                url_for("login")
            )

        # -------------------------------------------------
        # Generate new OTP
        # -------------------------------------------------

        otp = generate_otp()

        otp_expiry = (
            datetime.now()
            + timedelta(minutes=5)
        )

        # -------------------------------------------------
        # Update database
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE users
            SET
                otp = %s,
                otp_expiry = %s
            WHERE email = %s
            """,
            (
                otp,
                otp_expiry,
                email
            )
        )

        connection.commit()

        # -------------------------------------------------
        # Send new OTP
        # -------------------------------------------------

        send_otp(
            email,
            otp
        )

        return render_template(
            "verify_otp.html",
            email=email,
            success="A new OTP has been sent to your email."
        )

    except Exception as e:

        return render_template(
            "verify_otp.html",
            email=email,
            error=f"Could not resend OTP: {str(e)}"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    verified = request.args.get("verified")

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            return render_template(
                "login.html",
                error="Please enter your email and password."
            )

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if not user:
            return render_template(
                "login.html",
                error="Invalid email or password."
            )

        if not user["is_verified"]:
            session["verification_email"] = email

            return redirect(url_for("verify_otp"))

        if not bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        ):
            return render_template(
                "login.html",
                error="Invalid email or password."
            )

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]

        return redirect(url_for("dashboard"))

    success_message = None

    if verified == "1":
        success_message = "Email verified successfully! You can now log in."

    return render_template(
        "login.html",
        success=success_message
    )
# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = None
    cursor = None
    analyses = []

    total_analyses = 0
    average_ats = 0
    average_match = 0
    best_match = 0

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get user's analysis history
        cursor.execute(
            """
            SELECT
                id,
                resume_filename,
                ats_score,
                match_score,
                created_at
            FROM analyses
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (session["user_id"],)
        )

        analyses = cursor.fetchall()

        # Dashboard statistics
        total_analyses = len(analyses)

        if total_analyses > 0:

            ats_scores = [
                float(a["ats_score"])
                for a in analyses
                if a["ats_score"] is not None
            ]

            match_scores = [
                float(a["match_score"])
                for a in analyses
                if a["match_score"] is not None
            ]

            if ats_scores:
                average_ats = round(
                    sum(ats_scores) / len(ats_scores)
                )

            if match_scores:
                average_match = round(
                    sum(match_scores) / len(match_scores)
                )

                best_match = max(match_scores)

    except Exception as e:

        print("Dashboard database error:", e)

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return render_template(
        "dashboard.html",
        user_name=session.get("user_name"),
        user_email=session.get("user_email"),
        analyses=analyses,
        total_analyses=total_analyses,
        average_ats=average_ats,
        average_match=average_match,
        best_match=best_match
    )


# =========================================================
# VIEW SAVED ANALYSIS
# =========================================================

@app.route("/analysis/<int:analysis_id>")
def view_analysis(analysis_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                resume_filename,
                job_description,
                ats_score,
                match_score,
                detected_skills,
                missing_skills,
                ai_analysis,
                created_at
            FROM analyses
            WHERE id = %s
            AND user_id = %s
            """,
            (
                analysis_id,
                session["user_id"]
            )
        )

        analysis = cursor.fetchone()

        if not analysis:
            return redirect(url_for("dashboard"))

        detected_skills = []
        missing_skills = []

        if analysis["detected_skills"]:
            detected_skills = [
                skill.strip()
                for skill in analysis["detected_skills"].split(",")
                if skill.strip()
            ]

        if analysis["missing_skills"]:
            missing_skills = [
                skill.strip()
                for skill in analysis["missing_skills"].split(",")
                if skill.strip()
            ]

        return render_template(
            "view_analysis.html",
            analysis=analysis,
            detected_skills=detected_skills,
            missing_skills=missing_skills
        )

    except Exception as e:

        print("View analysis error:", e)

        return (
            "Unable to load analysis. "
            f"Error: {str(e)}"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# DELETE SAVED ANALYSIS
# =========================================================

@app.route(
    "/delete-analysis/<int:analysis_id>",
    methods=["POST"]
)
def delete_analysis(analysis_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM analyses
            WHERE id = %s
            AND user_id = %s
            """,
            (
                analysis_id,
                session["user_id"]
            )
        )

        connection.commit()

        print(
            f"Analysis {analysis_id} deleted successfully."
        )

        return redirect(url_for("dashboard"))

    except Exception as e:

        print("Delete analysis error:", e)

        return (
            "Unable to delete analysis. "
            f"Error: {str(e)}"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# =========================================================
# RESUME ANALYSIS
# =========================================================

@app.route("/analyze", methods=["POST"])
def analyze():

    # Resume analysis is available only to logged-in users
    if "user_id" not in session:
        return redirect(url_for("login"))

    if "resume" not in request.files:
        return "No resume file uploaded."

    resume = request.files["resume"]

    if resume.filename == "":
        return "No file selected."

    if not resume.filename.lower().endswith(".pdf"):
        return "Only PDF files are supported."

    try:
        # =====================================================
        # 1. EXTRACT TEXT FROM RESUME
        # =====================================================

        pdf = pymupdf.open(
            stream=resume.read(),
            filetype="pdf"
        )

    except Exception as e:
        return f"Unable to open PDF: {e}"

    resume_text = ""

    for page in pdf:
        resume_text += page.get_text()

    pdf.close()

    if resume_text.strip() == "":
        return "Could not extract text from this PDF."

    job_description = request.form.get(
        "job_description",
        ""
    ).strip()

    if job_description == "":
        return "Please enter a job description."

    # =====================================================
    # 2. SKILLS
    # =====================================================

    skills = extract_skills(
        resume_text
    )

    job_skills = extract_skills(
        job_description
    )

    resume_skill_set = {
        skill.lower()
        for skill in skills
    }

    job_skill_set = {
        skill.lower()
        for skill in job_skills
    }

    # =====================================================
    # 3. MATCHED SKILLS
    # =====================================================

    matched_skill_names = []

    for skill in job_skills:

        if skill.lower() in resume_skill_set:

            matched_skill_names.append(skill)

    # =====================================================
    # 4. MISSING SKILLS
    # =====================================================

    missing_skill_names = []

    for skill in job_skills:

        if skill.lower() not in resume_skill_set:

            missing_skill_names.append(skill)

    # =====================================================
    # 5. SKILL MATCH
    # =====================================================

    if len(job_skill_set) > 0:

        skill_match_percentage = round(
            (
                len(matched_skill_names)
                / len(job_skill_set)
            ) * 100
        )

    else:

        skill_match_percentage = 0

    # =====================================================
    # 6. TEXT SIMILARITY
    # =====================================================

    similarity_score = calculate_similarity(
        resume_text,
        job_description
    )

    # =====================================================
    # 7. OVERALL SCORE
    # =====================================================

    overall_score = round(
        (skill_match_percentage * 0.60)
        +
        (similarity_score * 0.40)
    )

    overall_score = max(
        0,
        min(100, overall_score)
    )

    # =====================================================
    # 8. SCORE MESSAGE
    # =====================================================

    if overall_score >= 80:

        score_message = (
            "Excellent match! Your resume strongly "
            "aligns with this job."
        )

    elif overall_score >= 60:

        score_message = (
            "Good match! A few improvements could "
            "make your resume stronger."
        )

    elif overall_score >= 40:

        score_message = (
            "Moderate match. Consider improving "
            "the missing skills below."
        )

    else:

        score_message = (
            "Your resume needs improvement for "
            "this particular role."
        )

    # =====================================================
    # 9. SKILL GAP
    # =====================================================

    skill_gaps = analyze_skill_gaps(
        missing_skill_names
    )

    # =====================================================
    # 10. ATS ANALYSIS
    # =====================================================

    ats_result = calculate_ats_score(
        resume_text
    )

    ats_score = ats_result["score"]
    ats_message = ats_result["message"]
    ats_checks = ats_result["checks"]
    ats_recommendations = ats_result["recommendations"]

    resume_word_count = (
        ats_result["word_count"]
    )

    ats_technical_keywords = (
        ats_result["technical_keywords"]
    )

    ats_action_keywords = (
        ats_result["action_keywords"]
    )

    # =====================================================
    # 11. RESUME IMPROVEMENT
    # =====================================================

    resume_improvements = generate_improvements(
        resume_text,
        job_description
    )

    # =====================================================
    # 12. GROQ AI
    # =====================================================

    try:

        ai_analysis = analyze_resume_with_ai(
            resume_text,
            job_description
        )

    except Exception as e:

        ai_analysis = (
            "AI analysis could not be completed "
            "at this time.\n\n"
            f"Error: {str(e)}"
        )

    # =====================================================
    # 13. SAVE ANALYSIS TO MYSQL
    # =====================================================

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        detected_skills_text = ", ".join(skills)

        missing_skills_text = ", ".join(
            missing_skill_names
        )

        insert_query = """
            INSERT INTO analyses (
                user_id,
                resume_filename,
                job_description,
                ats_score,
                match_score,
                detected_skills,
                missing_skills,
                ai_analysis
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """

        insert_values = (
            session["user_id"],
            resume.filename,
            job_description,
            ats_score,
            overall_score,
            detected_skills_text,
            missing_skills_text,
            ai_analysis
        )

        cursor.execute(
            insert_query,
            insert_values
        )

        connection.commit()

        print(
            "Analysis saved successfully. "
            f"Analysis ID: {cursor.lastrowid}"
        )

    except Exception as e:

        print(
            "Database save error:",
            e
        )

        # The user can still see the analysis even if
        # saving to the database fails.
        if connection:
            connection.rollback()

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

    # =====================================================
    # 14. RESULTS
    # =====================================================

    return render_template(

        "results.html",

        match_percentage=overall_score,

        skill_match_percentage=skill_match_percentage,

        similarity_score=similarity_score,

        score_message=score_message,

        skills=skills,

        job_skills=job_skills,

        matched_skills=matched_skill_names,

        missing_skills=missing_skill_names,

        skill_gaps=skill_gaps,

        ats_score=ats_score,

        ats_message=ats_message,

        ats_checks=ats_checks,

        ats_recommendations=ats_recommendations,

        resume_word_count=resume_word_count,

        ats_technical_keywords=ats_technical_keywords,

        ats_action_keywords=ats_action_keywords,

        resume_improvements=resume_improvements,

        ai_analysis=ai_analysis,

        resume_text=resume_text,

        job_description=job_description

    )


# =========================================================
# INTERACTIVE AI ASSISTANT
# =========================================================

@app.route("/ask-ai", methods=["POST"])
def ask_ai():

    # AI assistant is available only to logged-in users
    if "user_id" not in session:
        return redirect(url_for("login"))

    resume_text = request.form.get(
        "resume_text",
        ""
    )

    job_description = request.form.get(
        "job_description",
        ""
    )

    question = request.form.get(
        "question",
        ""
    )

    if not resume_text.strip():

        return "Resume information is missing."

    if not job_description.strip():

        return "Job description is missing."

    if not question.strip():

        return "Please enter a question."

    try:

        answer = ask_resume_question(
            resume_text,
            job_description,
            question
        )

    except Exception as e:

        return (
            "AI assistant could not complete "
            "your request.\n\n"
            f"Error: {str(e)}"
        )

    return render_template(

        "ai_answer.html",

        question=question,

        answer=answer
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )