from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models
from .database import engine, get_db
from .routes import auth_routes, job_routes, interview_routes, hiring_routes
from .seed import seed_data

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="We Hire API",
    description="Backend API for We Hire Application",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://we-hire1-uyqy.vercel.app",  # Your frontend domain
        "http://localhost:3000",  # For local development
        "http://localhost:5173",  # For Vite local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(job_routes.router)
app.include_router(interview_routes.router)
app.include_router(hiring_routes.router)

@app.get("/")
async def root():
    return {"message": "Welcome to We Hire API"}

@app.on_event("startup")
async def startup_event():
    # Seed initial data
    db = next(get_db())
    seed_data(db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 