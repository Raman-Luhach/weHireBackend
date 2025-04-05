from sqlalchemy.orm import Session
from datetime import date, timedelta
import logging

from . import models, auth

def seed_data(db: Session):
    try:
        # Check if data already exists
        users = db.query(models.User).all()
        jobs = db.query(models.Job).all()
        categories = db.query(models.InterviewCategory).all()
        
        if users and jobs and categories:
            logging.info("Database already contains seed data. Skipping seed.")
            return
        
        # Seed users (with different roles)
        users_data = [
            {"username": "hr_admin", "password": "password123", "role": "HR"},
            {"username": "hiring_manager1", "password": "password123", "role": "Hiring Manager"},
            {"username": "hiring_manager2", "password": "password123", "role": "Hiring Manager"},
            {"username": "employee1", "password": "password123", "role": "Employee"},
        ]
        
        for user_data in users_data:
            db_user = db.query(models.User).filter(models.User.username == user_data["username"]).first()
            if not db_user:
                hashed_password = auth.get_password_hash(user_data["password"])
                db_user = models.User(
                    username=user_data["username"],
                    hashed_password=hashed_password,
                    role=user_data["role"]
                )
                db.add(db_user)
        
        db.commit()
        
        # Get hiring managers for job assignments
        hiring_manager1 = db.query(models.User).filter(models.User.username == "hiring_manager1").first()
        hiring_manager2 = db.query(models.User).filter(models.User.username == "hiring_manager2").first()
        
        # Seed jobs
        today = date.today()
        jobs_data = [
            {
                "title": "Senior Backend Developer",
                "description": "We are looking for a Senior Backend Developer with experience in Python and FastAPI.",
                "requirements": "5+ years of experience in Python, Experience with FastAPI, PostgreSQL",
                "date_created": today,
                "end_date": today + timedelta(days=30),
                "assigned_to": hiring_manager1.id if hiring_manager1 else None,
                "status": "open",
                "location": "San Francisco, CA",
                "salary": 150000.0,
                "department": "Engineering"
            },
            {
                "title": "Frontend Developer",
                "description": "Frontend Developer with React.js experience needed for our growing team.",
                "requirements": "3+ years of experience in React.js, Experience with Redux, Knowledge of TypeScript",
                "date_created": today,
                "end_date": today + timedelta(days=15),
                "assigned_to": hiring_manager2.id if hiring_manager2 else None,
                "status": "open",
                "location": "Remote",
                "salary": 120000.0,
                "department": "Engineering"
            },
            {
                "title": "Product Manager",
                "description": "Experienced Product Manager to lead our product development efforts.",
                "requirements": "5+ years in product management, Experience with Agile methodologies",
                "date_created": today - timedelta(days=10),
                "end_date": today + timedelta(days=20),
                "assigned_to": hiring_manager1.id if hiring_manager1 else None,
                "status": "in_review",
                "location": "New York, NY",
                "salary": 140000.0,
                "department": "Product"
            }
        ]
        
        for job_data in jobs_data:
            db_job = models.Job(**job_data)
            db.add(db_job)
        
        db.commit()
        
        # Seed interview categories and questions
        categories_data = [
            {
                "name": "Technical Skills",
                "description": "Questions about technical knowledge and skills",
                "default_time": 45,
                "questions": [
                    "Explain the difference between a list and a dictionary in Python.",
                    "What is dependency injection and why is it useful?",
                    "Explain the concept of state management in frontend frameworks."
                ]
            },
            {
                "name": "Problem Solving",
                "description": "Questions to assess problem-solving abilities",
                "default_time": 60,
                "questions": [
                    "How would you design a URL shortening service?",
                    "Describe a challenging problem you faced and how you solved it.",
                    "How would you optimize a slow API endpoint?"
                ]
            },
            {
                "name": "Behavioral",
                "description": "Questions about work style and behavior",
                "default_time": 30,
                "questions": [
                    "Tell me about a time when you had to work under a tight deadline.",
                    "How do you handle conflicts in a team?",
                    "Describe a situation where you had to learn a new technology quickly."
                ]
            }
        ]
        
        for category_data in categories_data:
            questions = category_data.pop("questions")
            db_category = models.InterviewCategory(**category_data)
            db.add(db_category)
            db.flush()  # To get the category ID
            
            for question_text in questions:
                db_question = models.InterviewQuestion(text=question_text, category_id=db_category.id)
                db.add(db_question)
        
        db.commit()
        
        logging.info("Database seeded successfully!")
        
    except Exception as e:
        logging.error(f"Error seeding database: {e}")
        db.rollback()
        raise 