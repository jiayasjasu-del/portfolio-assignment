# AI Career Roadmap & Skill Gap Finder

A beginner-friendly Streamlit prototype for Task 2, Problem 4. It sends a student's profile to Gemini and displays a personalized skill assessment, an eight-week learning plan, and three portfolio project ideas.

## Project structure

```text
ai-career-roadmap/
├── app.py                 # Streamlit interface
├── roadmap.py             # Gemini request, response schema, and text report
├── requirements.txt       # Python packages
├── .gitignore             # Keeps API keys and generated files out of Git
└── .streamlit/
    └── config.toml        # App theme
```

## Run on Windows

1. Install Python 3.11 or newer.
2. Open PowerShell in this folder and create a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey). Create `.streamlit/secrets.toml` and put this in it:

   ```toml
   GEMINI_API_KEY = "paste-your-key-here"
   ```

   Keep this file private. It is excluded from Git. You can also set `GEMINI_API_KEY` as an environment variable.

4. Start the app:

   ```powershell
   streamlit run app.py
   ```

## Deploy to Streamlit Community Cloud

1. Push this folder to a GitHub repository without `.streamlit/secrets.toml`.
2. In [Streamlit Community Cloud](https://share.streamlit.io/), choose **Create app** and select the repository, branch, and `app.py`.
3. In the app's advanced settings, add `GEMINI_API_KEY = "your-key"` in Secrets, then deploy.

## How it works

- `app.py` collects the student's education, existing skills, target role, level, and weekly study time. It shows the generated skill table, week-by-week plan, project cards, and a `.txt` download.
- `roadmap.py` asks Gemini for JSON that follows a Pydantic schema. It validates that there are eight consecutive weeks and exactly three projects before showing the result.
- The key is read from Streamlit secrets or an environment variable; it is never stored in source code.

The plan is AI-generated guidance. Students should compare it with current job descriptions and adapt it to their goals.
