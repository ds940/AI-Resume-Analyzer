# AI-Resume-Analyzer
AI-powered resume analyzer that matches a PDF resume against a job description and generates an ATS score, skill gaps, and interview questions using Groq LLM and Streamlit.

# AI Resume Analyzer & Job Matcher


Compares a resume (PDF) with a job description using Generative AI (Groq LLM) and produces an ATS-style report.

## Features
- Resume PDF upload and text extraction
- ATS match score
- Matched / missing / partial-match skills
- Strengths and weaknesses
- Experience, education and project match
- Resume improvement recommendations
- 10 interview questions
- General resume tips

## Tech Stack
Python, Streamlit, Groq, PyPDF, python-dotenv, Prompt Engineering

## Setup (Windows)
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Put your key in `.env`:
```env
GROQ_API_KEY=gsk_xxxxxxxx
```

## Run
```bash
streamlit run app.py
```
Opens at [https://ai-resume-analyzer-nikwthnaef3xgnzmp7dm2n.streamlit.app/]

## Structure
```text
AI_Resume_Analyzer/
├── app.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── sample_job_description.txt
└── README.md
```
