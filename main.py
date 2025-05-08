from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth_routes, job_routes, interview_routes, candidate_routes, hiring_routes

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(job_routes.router)
app.include_router(interview_routes.router)
app.include_router(candidate_routes.router)
app.include_router(hiring_routes.router)

@app.get("/")
async def root():
    return {"message": "Welcome to WeHire API"} 