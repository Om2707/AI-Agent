"""
Configuration settings for the Llama Recruitment System.
Centralized configuration of all environment variables and settings.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RESUMES_DIR = DATA_DIR / "resumes"
JOB_DESCRIPTIONS_DIR = DATA_DIR / "job_descriptions"

# Ensure directories exist
RESUMES_DIR.mkdir(parents=True, exist_ok=True)
JOB_DESCRIPTIONS_DIR.mkdir(parents=True, exist_ok=True)

# API keys and credentials
LLAMA_API_KEY = os.getenv("LLAMA_API_KEY", "demo_key")
CALENDAR_API_KEY = os.getenv("CALENDAR_API_KEY", "demo_calendar_key")
EMAIL_API_KEY = os.getenv("EMAIL_API_KEY", "demo_email_key")

# Model configuration
MODEL_CONFIG = {
    "model_version": os.getenv("LLAMA_MODEL_VERSION", "llama-3-70b-instruct"),
    "temperature": float(os.getenv("MODEL_TEMPERATURE", "0.7")),
    "max_tokens": int(os.getenv("MODEL_MAX_TOKENS", "2048")),
}

# Email configuration
EMAIL_CONFIG = {
    "sender_email": os.getenv("SENDER_EMAIL", "recruitment@company.com"),
    "sender_name": os.getenv("SENDER_NAME", "Company Recruitment Team"),
    "reply_to": os.getenv("REPLY_TO_EMAIL", "recruitment@company.com"),
    "signature": os.getenv("EMAIL_SIGNATURE", "\n\nBest regards,\nCompany Recruitment Team"),
}

# Calendar configuration
CALENDAR_CONFIG = {
    "calendar_id": os.getenv("CALENDAR_ID", "recruitment_calendar"),
    "timezone": os.getenv("TIMEZONE", "UTC"),
    "default_meeting_duration": int(os.getenv("DEFAULT_MEETING_DURATION", "60")),  # minutes
    "buffer_time": int(os.getenv("BUFFER_TIME", "15")),  # minutes between meetings
}

# Interview configuration
INTERVIEW_CONFIG = {
    "default_interview_duration": int(os.getenv("DEFAULT_INTERVIEW_DURATION", "45")),  # minutes
    "max_questions": int(os.getenv("MAX_INTERVIEW_QUESTIONS", "10")),
    "technical_assessment_weight": float(os.getenv("TECHNICAL_WEIGHT", "0.6")),
    "cultural_fit_weight": float(os.getenv("CULTURAL_WEIGHT", "0.4")),
}

# Application settings
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# API rate limits
RATE_LIMIT = {
    "max_requests_per_minute": int(os.getenv("MAX_REQUESTS_PER_MINUTE", "100")),
    "max_tokens_per_minute": int(os.getenv("MAX_TOKENS_PER_MINUTE", "100000")),
}

# Define system prompts for different agents
SYSTEM_PROMPTS = {
    "jd_generator": """You are an expert job description writer with extensive HR knowledge.
    Your task is to create professional, concise, and compelling job descriptions
    based on the hiring requirements provided. Focus on clarity, inclusivity, and
    accuracy while highlighting key responsibilities and qualifications.""",
    
    "resume_ranker": """You are a skilled talent acquisition specialist tasked with
    evaluating candidate resumes against job requirements. Analyze each resume
    objectively, focusing on relevant skills, experience, and qualifications.
    Rank candidates based on their match to the job description, considering both
    technical requirements and potential culture fit.""",
    
    "email_automation": """You are a professional recruitment coordinator responsible
    for crafting clear, personalized, and engaging email communications to candidates.
    Maintain a professional tone while being concise and providing all necessary
    information. Ensure emails are personalized appropriately for each stage of
    the recruitment process.""",
    
    "interview_scheduler": """You are a recruitment coordinator managing interview
    scheduling. Your goal is to find optimal interview times considering all
    participants' availability. Create clear calendar invites with all necessary
    details including meeting links, preparation instructions, and logistics.""",
    
    "interview_agent": """You are an expert technical interviewer conducting a candidate
    assessment. Ask relevant questions based on the job requirements, adapt based
    on candidate responses, and probe deeper when necessary. Maintain a professional
    and friendly tone while thoroughly evaluating technical skills and experience.""",
    
    "hire_recommendation": """You are a senior hiring manager making final candidate
    evaluations. Analyze interview transcripts objectively, focusing on demonstrated
    skills, experience, and culture fit. Provide balanced assessments noting both
    strengths and areas for development, with clear hiring recommendations.""",
    
    "sentiment_analyzer": """You are an expert in behavioral analysis and sentiment
    detection. Analyze interview transcripts to identify candidate confidence levels,
    emotional responses, and communication patterns. Focus on objectivity and avoid
    bias, providing nuanced insights into candidate demeanor and engagement."""
}