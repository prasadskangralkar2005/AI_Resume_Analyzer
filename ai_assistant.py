import os

from dotenv import load_dotenv
from groq import Groq


# Load variables from .env
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY is not set. Please check your .env file."
    )

client = Groq(api_key=api_key)


def ask_ai(prompt):
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content
def analyze_resume_with_ai(resume_text, job_description):
    prompt = f"""
You are an expert AI career assistant and resume reviewer.

Analyze the candidate's resume against the provided job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Provide a professional analysis with these sections:

1. Resume Strengths
- Identify the strongest parts of the resume.

2. Resume Weaknesses
- Identify areas that need improvement.

3. Job Fit
- Explain how well the candidate fits the job.

4. Missing Skills
- Identify important skills from the job description that are missing
  or not clearly demonstrated in the resume.

5. Resume Improvements
- Give specific suggestions to improve the resume for this job.

6. Professional Summary
- Suggest an improved professional summary suitable for this job.

7. Project Improvements
- Suggest how the candidate can describe their projects more effectively.

Keep the recommendations practical and truthful.
Do not invent experience, skills, certifications, or achievements.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content
def ask_resume_question(resume_text, job_description, question):
    prompt = f"""
You are an expert AI career assistant.

You have access to the candidate's resume and the target job description.

Your job is to answer the candidate's question using the provided information.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

CANDIDATE QUESTION:
{question}

Instructions:
- Give a clear and professional answer.
- Personalize the answer using the resume and job description.
- If the question is about interview preparation, provide practical examples.
- If the question is about resume improvement, give specific suggestions.
- Do not invent skills, experience, certifications, projects, or achievements.
- If something is not present in the resume, clearly say that it is not mentioned.
- Keep the answer easy to understand.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content