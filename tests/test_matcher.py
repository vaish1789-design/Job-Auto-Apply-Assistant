from app.matcher import match
def test_match():
    p={"skills":"Python, Django, SQL","roles":"Python Developer","experience":"Fresher","location":"Pune"}
    j={"title":"Django Developer","description":"Python Django SQL REST API","experience":"0-1 years","location":"Pune"}
    r=match(p,j)
    assert r["score"]>0
    assert "python" in r["matched_skills"]
