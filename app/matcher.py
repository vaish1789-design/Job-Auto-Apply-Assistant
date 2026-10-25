import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def skill_list(text):
    return [x.strip().lower() for x in re.split(r"[,\n]+",text or "") if x.strip()]

def match(profile,job):
    skills=skill_list(profile.get("skills",""))
    jd=" ".join([job.get("title",""),job.get("description",""),job.get("experience",""),job.get("location","")]).lower()
    matched=[s for s in skills if re.search(r"(?<!\w)"+re.escape(s)+r"(?!\w)",jd)]
    keyword=100*len(matched)/len(skills) if skills else 0
    ptext=" ".join([profile.get("roles",""),profile.get("skills",""),profile.get("experience","")])
    jtext=" ".join([job.get("title",""),job.get("description",""),job.get("experience","")])
    semantic=0
    try:
        m=TfidfVectorizer(stop_words="english",ngram_range=(1,2)).fit_transform([ptext,jtext])
        semantic=float(cosine_similarity(m[0:1],m[1:2])[0][0]*100)
    except ValueError: pass
    # TODO (YOU): This 0.7 / 0.3 weighting decides what "best match" means.
    # - Higher weight on keyword score = rewards exact skill-word matches
    #   (good if you want strict fit to your listed Skills).
    # - Higher weight on semantic score = rewards jobs that are conceptually
    #   similar even without exact keyword overlap (looser, broader matches).
    # Tune these two numbers (they must sum to 1) if the ranking feels off.
    # Also note: this does NOT consider salary, location preference, or
    # company reputation as ranking factors — only text similarity to your
    # Skills/Roles. If "best opportunity" should also mean highest salary or
    # a preferred location, you'd need to add that logic here yourself, e.g.
    # a bonus/penalty term based on job.get("salary") or job.get("location")
    # vs profile.get("location").
    return {"score":round(.7*keyword+.3*semantic,1),"keyword_score":round(keyword,1),
            "semantic_score":round(semantic,1),"matched_skills":matched}
