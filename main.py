import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


class QuestionRequest(BaseModel):
    question: str
    context: str | None = None


@app.post("/api/assist")
def ai_assist(req: QuestionRequest):
    q = (req.question or "").lower().strip()
    # Very simple rule-based helper as a placeholder
    if not q:
        return {"answer": "Please type a question about homework, exams, careers, or tools, and I'll help."}

    if any(k in q for k in ["gpa", "grade point", "cgpa"]):
        return {"answer": "To estimate GPA: convert each grade to points (A=4, B=3, C=2, D=1, F=0), multiply by credits, sum, then divide by total credits. Use the GPA tool in the Tools page for a quick calculation."}

    if any(k in q for k in ["resume", "cv"]):
        return {"answer": "Strong resumes highlight impact. Use bullet points with action verbs and numbers (e.g., 'Improved app performance by 30%'). Keep to 1 page if <10 years experience. Try the Resume Builder in Tools for a structured start."}

    if any(k in q for k in ["intern", "internship", "scholarship", "competition"]):
        return {"answer": "Browse the Opportunities page for curated internships, scholarships, and competitions. Filter by region and deadline, then follow the official links to learn more."}

    if any(k in q for k in ["career", "path", "job role", "guidance"]):
        return {"answer": "Think in 3 steps: explore roles (software, data, product, design), build a portfolio of 2–3 projects, and network (alumni, events). See the Career Guidance page for tracks and resources."}

    if any(k in q for k in ["study", "exam", "prepare", "revision"]):
        return {"answer": "Use spaced repetition and active recall. Break sessions into 50-minute focus blocks with 10-minute breaks. Make concise cheat sheets and a weekly timetable from the Tools page."}

    return {"answer": "Here's a general approach: break the problem into smaller parts, define the knowns/unknowns, and draft a plan. If you share details (topic, constraints, goal), I can offer step-by-step guidance."}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
