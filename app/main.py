import streamlit as st
import pandas as pd
from db import init_db,profile,save_profile,upsert_jobs,jobs,job,application,applications
from matcher import match
from sources import csv_jobs,rss_jobs

st.set_page_config(page_title="Job Auto-Apply Assistant",page_icon="💼",layout="wide")
init_db(); p=profile()
st.title("💼 Job Auto-Apply Assistant")
st.caption("Find → match → prepare → review → apply")

page=st.sidebar.radio("Menu",["Dashboard","Profile","Jobs","Prepare Application","Applications","Settings"])
st.sidebar.info("This starter app prepares and tracks applications. It does not bypass CAPTCHA, anti-bot controls, or site restrictions.")

# TODO (YOU): This Profile page is where the matcher gets its data from.
# The quality of your "best match" results depends entirely on how complete
# and accurate you make this. Fill in real, detailed values (especially
# Skills and Target roles below) once the app is running in the browser —
# there's nothing to edit in this file for that part.
if page=="Profile":
    st.header("Profile")
    with st.form("p"):
        name=st.text_input("Name",p["name"]); email=st.text_input("Email",p["email"])
        phone=st.text_input("Phone",p["phone"]); location=st.text_input("Preferred locations",p["location"])
        roles=st.text_area("Target roles",p["roles"],help="Example: Python Developer, Django Developer")
        skills=st.text_area("Skills",p["skills"],help="Comma-separated: Python, Django, SQL, Pandas, NumPy")
        ex=st.selectbox("Experience",["Fresher","0-1 years","1-2 years"],index=["Fresher","0-1 years","1-2 years"].index(p["experience"]) if p["experience"] in ["Fresher","0-1 years","1-2 years"] else 0)
        notice=st.text_input("Notice period",p["notice_period"]); salary=st.text_input("Expected salary",p["expected_salary"])
        resume=st.text_input("Resume path/name",p["resume_path"])
        if st.form_submit_button("Save Profile",type="primary"):
            save_profile(dict(name=name,email=email,phone=phone,location=location,roles=roles,skills=skills,
            experience=ex,notice_period=notice,expected_salary=salary,resume_path=resume)); st.success("Saved.")

# TODO (YOU): This is the ONLY way jobs get into the app right now:
#   1) CSV upload (see data/sample_jobs.csv for the exact column format
#      title,company,location,experience,salary,url,description,source,posted_at)
#   2) A public RSS/Atom feed URL (e.g. some job boards or company career
#      pages publish an RSS feed — search "<board name> RSS feed jobs").
# There is NO scraper/crawler for LinkedIn, Indeed, Naukri, etc. — that's
# intentional (see README: no CAPTCHA/anti-bot bypass). If you want more
# jobs to match against, you need to either:
#   - export/download job listings as CSV from a job board that allows it, or
#   - find a legitimate RSS feed and paste the URL here, or
#   - manually add rows to a CSV in the same column format as sample_jobs.csv
elif page=="Jobs":
    st.header("Import & Match Jobs")
    a,b=st.columns(2)
    with a:
        f=st.file_uploader("CSV file",type="csv")
        if f and st.button("Import CSV"):
            st.success(f"Imported/updated {upsert_jobs(csv_jobs(f))} jobs.")
    with b:
        url=st.text_input("Permitted RSS/Atom feed URL")
        if st.button("Fetch RSS"):
            try: st.success(f"Imported/updated {upsert_jobs(rss_jobs(url))} jobs.")
            except Exception as e: st.error(str(e))
    allj=jobs()
    if not allj: st.warning("Import data/sample_jobs.csv first.")
    else:
        # TODO (YOU): 70% default threshold. Lower this (e.g. to 40-50) if you
        # get zero/few results early on — matching against only a handful of
        # sample jobs will rarely score above 70%.
        threshold=st.slider("Minimum match %",0,100,70)
        rows=[]
        for j in allj:
            m=match(p,j)
            if m["score"]>=threshold: rows.append({**j,**m})
        st.write(f"Matching jobs: **{len(rows)}**")
        if rows:
            df=pd.DataFrame(rows)
            st.dataframe(df[["title","company","location","experience","salary","score","source"]].sort_values("score",ascending=False),use_container_width=True)
            choice=st.selectbox("Select job",[f'{x["id"]} — {x["title"]} — {x["company"]}' for x in rows])
            j=job(int(choice.split(" — ")[0])); m=match(p,j)
            st.subheader(j["title"]); st.write(f"**{j['company']}** · {j['location']} · {j['experience']}")
            st.metric("Match",f'{m["score"]}%')
            st.write("Matched skills:",", ".join(m["matched_skills"]) or "None detected")
            st.write(j["description"])
            if j["url"]: st.link_button("Open Job",j["url"])
            if st.button("Save Job"): application(j["id"],"Saved","Saved from Jobs page."); st.success("Saved.")

elif page=="Prepare Application":
    st.header("Prepare Application")
    js=jobs()
    if not js: st.info("Import jobs first.")
    else:
        choice=st.selectbox("Job",[f'{j["id"]} — {j["title"]} — {j["company"]}' for j in js])
        j=job(int(choice.split(" — ")[0])); m=match(p,j)
        st.metric("Match",f'{m["score"]}%')
        # TODO (YOU): This auto-generated summary is generic/template text.
        # Edit it in the text box in the browser before sending it anywhere —
        # a real cover-letter-style message referencing the specific job will
        # get you much better results than this boilerplate sentence.
        summary=f"I am applying for the {j['title']} role at {j['company']}. My skills include {p['skills']}. I am interested in this opportunity because the role aligns with my background in {p['roles']}."
        st.text_area("Application summary",summary,height=140)
        st.write("**Email:**",p["email"] or "Not set"); st.write("**Phone:**",p["phone"] or "Not set")
        st.write("**Resume:**",p["resume_path"] or "Not set")
        notes=st.text_area("Notes")
        if st.button("Mark Ready",type="primary"): application(j["id"],"Ready",notes); st.success("Ready to review and submit.")

elif page=="Applications":
    st.header("Application Tracker")
    apps=applications()
    if apps:
        st.dataframe(pd.DataFrame(apps)[["title","company","location","status","applied_at","notes"]],use_container_width=True)
        c=st.selectbox("Update",[f'{a["id"]} — {a["title"]} — {a["company"]}' for a in apps])
        a=next(x for x in apps if x["id"]==int(c.split(" — ")[0]))
        statuses=["Saved","Ready","Applied","Rejected","Interview","Offer"]
        s=st.selectbox("Status",statuses,index=statuses.index(a["status"]) if a["status"] in statuses else 0)
        n=st.text_area("Notes",a["notes"] or "")
        if st.button("Update"): application(a["job_id"],s,n); st.success("Updated.")
    else: st.info("No applications yet.")

elif page=="Settings":
    st.header("Settings")
    st.markdown("""### Data sources
Use CSV imports or RSS/Atom feeds you are permitted to access.

### Responsible automation
Do not bypass CAPTCHA, login controls, rate limits, robots restrictions, or anti-bot systems. For automatic submission, use an official API/integration that explicitly permits it.""")

else:
    st.header("Dashboard")
    js=jobs(); apps=applications()
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Jobs",len(js)); c2.metric("Applications",len(apps))
    c3.metric("Ready",sum(a["status"]=="Ready" for a in apps)); c4.metric("Applied",sum(a["status"]=="Applied" for a in apps))
    if js:
        scored=sorted([{**j,**match(p,j)} for j in js],key=lambda x:x["score"],reverse=True)[:10]
        st.subheader("Top matches")
        for j in scored:
            with st.container(border=True):
                x,y,z=st.columns([5,2,2])
                x.write(f"**{j['title']}** — {j['company']}")
                x.caption(f"{j['location']} · {j['experience']}")
                y.metric("Match",f'{j["score"]}%')
                if j["url"]: z.link_button("Open",j["url"])
    else: st.info("Open Profile, then import data/sample_jobs.csv from Jobs.")
