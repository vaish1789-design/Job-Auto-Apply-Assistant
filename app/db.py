import sqlite3
from pathlib import Path
from datetime import datetime

DB = Path(__file__).resolve().parent.parent / "data" / "jobs.db"

def conn():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS profile(
      id INTEGER PRIMARY KEY CHECK(id=1), name TEXT DEFAULT '', email TEXT DEFAULT '',
      phone TEXT DEFAULT '', location TEXT DEFAULT '', roles TEXT DEFAULT '',
      skills TEXT DEFAULT '', experience TEXT DEFAULT 'Fresher',
      notice_period TEXT DEFAULT 'Immediate', expected_salary TEXT DEFAULT '',
      resume_path TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS jobs(
      id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, company TEXT NOT NULL,
      location TEXT DEFAULT '', experience TEXT DEFAULT '', salary TEXT DEFAULT '',
      url TEXT UNIQUE, description TEXT DEFAULT '', source TEXT DEFAULT '',
      posted_at TEXT DEFAULT '', created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS applications(
      id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INTEGER NOT NULL UNIQUE,
      status TEXT DEFAULT 'Saved', notes TEXT DEFAULT '', applied_at TEXT,
      updated_at TEXT NOT NULL
    );
    """)
    c.execute("INSERT OR IGNORE INTO profile(id) VALUES(1)")
    c.commit(); c.close()

def profile():
    c=conn(); r=c.execute("SELECT * FROM profile WHERE id=1").fetchone(); c.close(); return dict(r)

def save_profile(p):
    c=conn()
    c.execute("""UPDATE profile SET name=?,email=?,phone=?,location=?,roles=?,skills=?,
    experience=?,notice_period=?,expected_salary=?,resume_path=? WHERE id=1""",
    (p["name"],p["email"],p["phone"],p["location"],p["roles"],p["skills"],
     p["experience"],p["notice_period"],p["expected_salary"],p["resume_path"]))
    c.commit(); c.close()

def upsert_jobs(items):
    c=conn(); n=0
    for j in items:
        url=j.get("url") or f"local:{j.get('title','')}:{j.get('company','')}"
        c.execute("""INSERT INTO jobs(title,company,location,experience,salary,url,description,source,posted_at,created_at)
        VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(url) DO UPDATE SET
        title=excluded.title,company=excluded.company,location=excluded.location,
        experience=excluded.experience,salary=excluded.salary,description=excluded.description,
        source=excluded.source,posted_at=excluded.posted_at""",
        (j.get("title",""),j.get("company",""),j.get("location",""),j.get("experience",""),
         j.get("salary",""),url,j.get("description",""),j.get("source",""),j.get("posted_at",""),
         datetime.now().isoformat(timespec="seconds")))
        n+=1
    c.commit(); c.close(); return n

def jobs():
    c=conn(); r=c.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall(); c.close(); return [dict(x) for x in r]

def job(jid):
    c=conn(); r=c.execute("SELECT * FROM jobs WHERE id=?",(jid,)).fetchone(); c.close(); return dict(r) if r else None

def application(job_id,status="Saved",notes=""):
    now=datetime.now().isoformat(timespec="seconds")
    applied=now if status=="Applied" else None
    c=conn()
    c.execute("""INSERT INTO applications(job_id,status,notes,applied_at,updated_at)
    VALUES(?,?,?,?,?) ON CONFLICT(job_id) DO UPDATE SET status=excluded.status,
    notes=excluded.notes, applied_at=CASE WHEN excluded.status='Applied'
    THEN COALESCE(applications.applied_at,excluded.applied_at) ELSE applications.applied_at END,
    updated_at=excluded.updated_at""",(job_id,status,notes,applied,now))
    c.commit(); c.close()

def applications():
    c=conn()
    r=c.execute("""SELECT a.*,j.title,j.company,j.location,j.url FROM applications a
    JOIN jobs j ON j.id=a.job_id ORDER BY a.updated_at DESC""").fetchall()
    c.close(); return [dict(x) for x in r]
