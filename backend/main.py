from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from docx import Document
import sqlite3
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI(title="ResumeX AI")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
DB = "resumex.db"
UPLOAD = "uploads"
os.makedirs(UPLOAD, exist_ok=True)

# Database
conn = sqlite3.connect(DB, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS resumes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    content TEXT
)
""")

conn.commit()

# Models
class User(BaseModel):
    username: str
    password: str

class Job(BaseModel):
    title: str
    description: str


# Home
@app.get("/")
def home():
    return {"message": "ResumeX AI Backend Running"}


# Register
@app.post("/register")
def register(user: User):
    cursor.execute(
        "INSERT INTO users(username,password) VALUES(?,?)",
        (user.username, user.password)
    )
    conn.commit()
    return {"status": "registered"}


# Login
@app.post("/login")
def login(user: User):
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (user.username, user.password)
    )
    data = cursor.fetchone()

    return {"success": bool(data)}


# Add Job
@app.post("/job")
def create_job(job: Job):
    cursor.execute(
        "INSERT INTO jobs(title,description) VALUES(?,?)",
        (job.title, job.description)
    )
    conn.commit()

    return {"status": "job added"}


# Upload Resume
@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):

    path = os.path.join(UPLOAD, file.filename)

    content = await file.read()

    with open(path, "wb") as f:
        f.write(content)

    text = ""

    try:
        # TXT File
        if file.filename.lower().endswith(".txt"):
            text = content.decode(errors="ignore")

        # DOCX File
        elif file.filename.lower().endswith(".docx"):
            doc = Document(path)
            text = "\n".join([para.text for para in doc.paragraphs])

        else:
            text = content.decode(errors="ignore")

    except:
        text = ""

    # OLD RESUMES DELETE
    cursor.execute("DELETE FROM resumes")
    conn.commit()

    # NEW RESUME SAVE
    cursor.execute(
        "INSERT INTO resumes(filename,content) VALUES(?,?)",
        (file.filename, text)
    )

    conn.commit()

    return {"status": "uploaded successfully"}


# Match Resume
@app.get("/match/{job_id}")
def match(job_id: int):

    cursor.execute(
        "SELECT description FROM jobs WHERE id=?",
        (job_id,)
    )

    job = cursor.fetchone()

    if not job:
        return {"error": "job not found"}

    jd = job[0]

    cursor.execute(
        "SELECT filename,content FROM resumes"
    )

    resumes = cursor.fetchall()

    results = []

    for r in resumes:
        filename = r[0]
        resume_text = r[1]

        docs = [jd, resume_text]

        tfidf = TfidfVectorizer().fit_transform(docs)

        score = float(
            cosine_similarity(
                tfidf[0:1],
                tfidf[1:2]
            )[0][0]
        ) * 100

        results.append({
            "resume": filename,
            "score": round(score, 2)
        })

    results = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )

    return {"rankings": results}


# Run Server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)