# 📄 AI Resume Analyzer

A beginner-friendly Streamlit app that analyzes your PDF resume in seconds.

## Features
- **PDF text extraction** via PyPDF2
- **Skill detection** from 60+ predefined keywords across 6 categories
- **ATS score** (rule-based, out of 100) with a clear scoring breakdown
- **Best-fit role suggestion** from: Data Analyst, ML Intern, Software Engineer, Web Developer, Cloud Intern
- **Actionable tips** to improve your resume
- Clean dark-mode UI — no external datasets required

## Quick Start

```bash
# 1. Clone / download this folder
# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

Then open http://localhost:8501 in your browser and upload a PDF resume.

## ATS Score Breakdown

| Component              | Max Points |
|------------------------|-----------|
| Skills coverage        | 50        |
| Resume length          | 15        |
| Section keywords       | 20        |
| Contact information    | 10        |
| Quantified achievements| 5         |
| **Total**              | **100**   |

## Project Structure

```
ai_resume_analyzer/
├── app.py            ← all code lives here
├── requirements.txt
└── README.md
```

## Requirements
- Python 3.9+
- streamlit
- PyPDF2

No external datasets, no API keys, no internet connection needed after install.
