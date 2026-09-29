import os
import json
import re

import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
from groq import Groq


# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------

load_dotenv()

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY or API_KEY == "your_groq_api_key_here":
    st.error(
        "GROQ_API_KEY is missing. "
        "Open the .env file and add your real Groq API key."
    )
    st.stop()

client = Groq(api_key=API_KEY)

MODEL = "openai/gpt-oss-120b"


# ------------------------------------------------------------
# STYLING
# ------------------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        font-size: 40px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .subtitle {
        font-size: 18px;
        color: #888;
        margin-bottom: 24px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="main-title">'
    'AI Resume Analyzer & Job Matcher'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Analyze your resume against a job description using Generative AI.'
    '</div>',
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------

def extract_resume_text(uploaded_file):
    """
    Extract text from an uploaded PDF.
    """

    try:
        reader = PdfReader(uploaded_file)

        pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n".join(pages)

    except Exception as e:
        raise Exception(
            f"Unable to read PDF: {e}"
        )


def clean_text(text):
    """
    Collapse extra whitespace.
    """

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


def parse_json_response(content):
    """
    Safely extract a JSON object from the model response.
    """

    content = content.strip()

    # Remove ```json if the model returns a code block.
    content = re.sub(
        r"^```json\s*",
        "",
        content,
        flags=re.IGNORECASE
    )

    # Remove ``` if present.
    content = re.sub(
        r"^```\s*",
        "",
        content
    )

    # Remove closing ```
    content = re.sub(
        r"\s*```$",
        "",
        content
    )

    try:
        return json.loads(content)

    except json.JSONDecodeError:

        # Try to find the JSON object inside
        # any additional text returned by the model.
        start = content.find("{")
        end = content.rfind("}")

        if start != -1 and end != -1:

            json_text = content[
                start:end + 1
            ]

            try:
                return json.loads(json_text)

            except json.JSONDecodeError:
                raise ValueError(
                    "The AI returned invalid JSON. "
                    "Please try again."
                )

        raise ValueError(
            "The AI returned an invalid response. "
            "Please try again."
        )


def analyze_resume(resume_text, job_description):
    """
    Send resume + job description to the Groq LLM
    and return structured JSON.
    """

    prompt = f"""
You are an expert technical recruiter and ATS resume analyzer.

Analyze the candidate resume against the provided job description.

Your response MUST be valid JSON with exactly this structure:

{{
    "ats_score": 0,
    "candidate_summary": "",
    "matched_skills": [],
    "missing_skills": [],
    "partial_match_skills": [],
    "strengths": [],
    "weaknesses": [],
    "experience_match": "",
    "education_match": "",
    "project_match": "",
    "resume_improvements": [],
    "interview_questions": []
}}

Rules:

1. ats_score must be an integer between 0 and 100.

2. matched_skills must contain skills clearly present
   in both the resume and job description.

3. missing_skills must contain important job requirements
   absent from the resume.

4. partial_match_skills must contain skills that are
   related but not strongly demonstrated.

5. Do not invent candidate experience.

6. Base the analysis only on the provided resume
   and job description.

7. interview_questions must contain exactly 10
   relevant questions.

8. Keep the answer concise but useful.

9. Return JSON only.

RESUME:

{resume_text}

JOB DESCRIPTION:

{job_description}
"""

    try:

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional ATS resume analyzer. "
                        "Return valid JSON only."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "The AI returned an empty response."
            )

        return parse_json_response(content)

    except Exception as e:

        raise Exception(
            f"Unable to analyze resume: {e}"
        )


def generate_resume_tips(resume_text):
    """
    Generate general resume improvement tips.
    """

    prompt = f"""
Review this resume as a professional technical recruiter.

Provide 8 practical recommendations to improve it.

Focus on:

- ATS compatibility
- Technical skills
- Project descriptions
- Achievement statements
- Keywords
- Formatting
- Quantifiable results
- Professional summary

Resume:

{resume_text}

Return only a numbered list.
"""

    try:

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume coach."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:

        raise Exception(
            f"Unable to generate resume tips: {e}"
        )


def show_list(
    items,
    prefix="•",
    empty="Nothing identified."
):
    """
    Display a list of items.
    """

    if items:

        for item in items:

            st.write(
                f"{prefix} {item}"
            )

    else:

        st.write(empty)


def show_numbered(items):
    """
    Display numbered items.
    """

    if not items:

        st.write(
            "No information available."
        )

        return

    for i, item in enumerate(
        items,
        start=1
    ):

        st.write(
            f"{i}. {item}"
        )


# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------

with st.sidebar:

    st.header(
        "Project Information"
    )

    st.write(
        """
        This application uses Generative AI
        to compare a candidate's resume with
        a job description.
        """
    )

    st.divider()

    st.subheader(
        "Technology"
    )

    st.write(
        """
        - Python
        - Streamlit
        - Groq
        - LLM
        - PDF Processing
        - Prompt Engineering
        """
    )

    st.divider()

    st.subheader(
        "Analysis"
    )

    st.write(
        """
        - ATS Score
        - Matched Skills
        - Missing Skills
        - Partial Matches
        - Strengths
        - Weaknesses
        - Interview Questions
        """
    )


# ------------------------------------------------------------
# INPUTS
# ------------------------------------------------------------

col1, col2 = st.columns(2)


with col1:

    st.subheader(
        "1. Upload Resume"
    )

    uploaded_file = st.file_uploader(
        "Upload Resume PDF",
        type=["pdf"]
    )


with col2:

    st.subheader(
        "2. Job Description"
    )

    job_description = st.text_area(
        "Paste the job description here",
        height=250,
        placeholder="Paste the complete job description..."
    )


# ------------------------------------------------------------
# ANALYZE BUTTON
# ------------------------------------------------------------

st.divider()

analyze_button = st.button(
    "Analyze Resume",
    type="primary",
    use_container_width=True
)


# ------------------------------------------------------------
# PROCESS
# ------------------------------------------------------------

if analyze_button:

    # Check resume
    if uploaded_file is None:

        st.warning(
            "Please upload a resume PDF."
        )

        st.stop()

    # Check job description
    if not job_description.strip():

        st.warning(
            "Please enter a job description."
        )

        st.stop()

    with st.spinner(
        "Reading and analyzing resume..."
    ):

        try:

            # Extract text
            resume_text = extract_resume_text(
                uploaded_file
            )

            # Clean text
            resume_text = clean_text(
                resume_text
            )

            # Check extracted text
            if len(resume_text) < 100:

                st.error(
                    "Very little text was extracted. "
                    "Please upload a text-based PDF "
                    "(not a scanned image)."
                )

                st.stop()

            # Analyze resume
            analysis = analyze_resume(
                resume_text,
                job_description
            )

            # Store results
            st.session_state["analysis"] = analysis

            st.session_state["resume_text"] = (
                resume_text
            )

            # Clear old tips
            st.session_state.pop(
                "tips",
                None
            )

            st.success(
                "Resume analysis completed successfully!"
            )

        except Exception as e:

            st.error(
                f"Error: {e}"
            )

            st.stop()


# ------------------------------------------------------------
# RESULTS
# ------------------------------------------------------------

if "analysis" in st.session_state:

    result = st.session_state["analysis"]

    st.divider()

    st.header(
        "Resume Analysis Report"
    )


    # --------------------------------------------------------
    # ATS SCORE
    # --------------------------------------------------------

    try:

        score = int(
            result.get(
                "ats_score",
                0
            )
        )

    except (TypeError, ValueError):

        score = 0


    # Keep score between 0 and 100
    score = min(
        max(score, 0),
        100
    )


    m1, m2, m3 = st.columns(3)


    with m1:

        st.metric(
            "ATS Match Score",
            f"{score}%"
        )


    with m2:

        matched_skills = result.get(
            "matched_skills",
            []
        )

        st.metric(
            "Matched Skills",
            len(matched_skills)
        )


    with m3:

        missing_skills = result.get(
            "missing_skills",
            []
        )

        st.metric(
            "Missing Skills",
            len(missing_skills)
        )


    # Progress bar
    st.progress(
        score / 100
    )


    # --------------------------------------------------------
    # CANDIDATE SUMMARY
    # --------------------------------------------------------

    st.subheader(
        "Candidate Summary"
    )

    st.write(
        result.get(
            "candidate_summary",
            "No summary available."
        )
    )


    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------

    c1, c2 = st.columns(2)


    with c1:

        st.subheader(
            "Matched Skills"
        )

        show_list(
            result.get(
                "matched_skills",
                []
            ),
            "✓",
            "No strong matches identified."
        )


    with c2:

        st.subheader(
            "Missing Skills"
        )

        show_list(
            result.get(
                "missing_skills",
                []
            ),
            "•",
            "No major missing skills identified."
        )


    # --------------------------------------------------------
    # PARTIAL MATCH
    # --------------------------------------------------------

    st.subheader(
        "Partial Match Skills"
    )

    show_list(
        result.get(
            "partial_match_skills",
            []
        ),
        "~",
        "No partial matches identified."
    )


    # --------------------------------------------------------
    # STRENGTHS & WEAKNESSES
    # --------------------------------------------------------

    c1, c2 = st.columns(2)


    with c1:

        st.subheader(
            "Strengths"
        )

        show_list(
            result.get(
                "strengths",
                []
            ),
            "✓"
        )


    with c2:

        st.subheader(
            "Weaknesses"
        )

        show_list(
            result.get(
                "weaknesses",
                []
            ),
            "•"
        )


    # --------------------------------------------------------
    # EXPERIENCE
    # --------------------------------------------------------

    st.subheader(
        "Experience Match"
    )

    st.write(
        result.get(
            "experience_match",
            "Not available."
        )
    )


    # --------------------------------------------------------
    # EDUCATION
    # --------------------------------------------------------

    st.subheader(
        "Education Match"
    )

    st.write(
        result.get(
            "education_match",
            "Not available."
        )
    )


    # --------------------------------------------------------
    # PROJECT
    # --------------------------------------------------------

    st.subheader(
        "Project Match"
    )

    st.write(
        result.get(
            "project_match",
            "Not available."
        )
    )


    # --------------------------------------------------------
    # RESUME IMPROVEMENTS
    # --------------------------------------------------------

    st.subheader(
        "Resume Improvement Recommendations"
    )

    show_numbered(
        result.get(
            "resume_improvements",
            []
        )
    )


    # --------------------------------------------------------
    # INTERVIEW QUESTIONS
    # --------------------------------------------------------

    st.subheader(
        "AI-Generated Interview Questions"
    )

    show_numbered(
        result.get(
            "interview_questions",
            []
        )
    )


    # --------------------------------------------------------
    # GENERAL RESUME TIPS
    # --------------------------------------------------------

    with st.expander(
        "Generate General Resume Improvement Tips"
    ):

        if st.button(
            "Generate Tips"
        ):

            with st.spinner(
                "Generating recommendations..."
            ):

                try:

                    tips = generate_resume_tips(
                        st.session_state[
                            "resume_text"
                        ]
                    )

                    st.session_state[
                        "tips"
                    ] = tips

                except Exception as e:

                    st.error(
                        f"Unable to generate tips: {e}"
                    )


        if "tips" in st.session_state:

            st.write(
                st.session_state["tips"]
            )


# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------

st.divider()

st.caption(
    "AI Resume Analyzer | "
    "Python + Streamlit + Groq"
)