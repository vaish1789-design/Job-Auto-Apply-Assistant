# Job Auto-Apply Assistant

A beginner-friendly Python + Streamlit job matching and application tracker.

## Features
- Profile and skill management
- CSV job import
- Permitted RSS/Atom feed import
- TF-IDF + skill-keyword matching
- Match percentage and matched skills
- Location filtering
- Application preparation
- Application status tracking
- Local SQLite database

## Run
Windows:
1. Install Python 3.11+
2. `python -m venv .venv`
3. `.venv\Scripts\activate`
4. `pip install -r requirements.txt`
5. `streamlit run app/main.py`

macOS/Linux:
`python3 -m venv .venv`
`source .venv/bin/activate`
`pip install -r requirements.txt`
`streamlit run app/main.py`

Start by opening Profile, then import `data/sample_jobs.csv` from Jobs.

Important: this version does not bypass CAPTCHA, login controls, rate limits, anti-bot systems, or site restrictions, and does not automatically submit to third-party sites. For automatic submission, use an official API/integration that explicitly permits it.

## Things you need to customize (see `# TODO (YOU)` comments in the code)
1. **`data/sample_jobs.csv`** — this only has 4 placeholder rows. Replace/add
   rows with real jobs, keeping the same header row:
   `title,company,location,experience,salary,url,description,source,posted_at`
2. **Profile page (in the running app)** — fill in real, detailed Skills and
   Target roles. Match quality depends directly on this.
3. **`app/matcher.py`** — the `.7`/`.3` keyword/semantic weighting decides how
   "best match" is scored. It does not factor in salary or location; add that
   yourself if you want it.
4. **`app/main.py` → Jobs page** — 70% default match threshold; lower it if
   you're not seeing results with only a few imported jobs.
5. **`app/main.py` → Prepare Application page** — the auto-generated summary
   is generic boilerplate; personalize it per job before using it.
6. **Job sources (`app/sources.py`)** — only CSV upload and RSS/Atom feed URLs
   are supported, intentionally (no scraping/login automation). Find real RSS
   feeds from job boards/company career pages, or export CSVs where allowed.
