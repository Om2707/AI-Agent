from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import sys
import logging
from pathlib import Path

# Set up paths to ensure imports work correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import your existing backend modules
from models.llama_model import LlamaModel
from agents.jd_generator import JDGenerator
from agents.resume_ranker import ResumeRanker
from agents.email_automation import EmailAutomation
from agents.interview_scheduler import InterviewScheduler
from agents.interview_agent import InterviewAgent
from agents.hire_recommendation import HireRecommendationAgent
from agents.sentiment_analyzer import SentimentAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global variable to store the model
llama_model = None

def initialize_model():
    """Initialize the Llama model and return the instance"""
    global llama_model
    
    if llama_model is not None:
        return llama_model
        
    try:
        # Get model path from environment variable or use default
        model_path = os.getenv("LLAMA_MODEL_PATH", "models/llama-2-7b-chat.Q4_K_M.gguf")
        logger.info(f"Initializing Llama model from path: {model_path}")
        
        # Initialize the model
        llama_model = LlamaModel(model_path=model_path)
        
        # Test if the model loaded successfully
        if llama_model.is_loaded():
            logger.info("Llama model initialized successfully")
            return llama_model
        else:
            logger.error("Llama model initialization returned False")
            return None
    except Exception as e:
        logger.error(f"Failed to initialize Llama model: {str(e)}")
        return None

# Routes
@app.route('/')
def home():
    """Render homepage"""
    return render_template('index.html')

@app.route('/jd-generator', methods=['GET', 'POST'])
def jd_generator():
    """JD Generator page and functionality"""
    if request.method == 'POST':
        # Get form data
        job_title = request.form.get('job_title')
        skills = request.form.get('skills')
        experience = request.form.get('experience')
        
        # Initialize model if not already initialized
        model = initialize_model()
        if model is None:
            return render_template('jd_generator.html', error="Failed to initialize the Llama model")
        
        # Generate JD
        jd_agent = JDGenerator(model)
        generated_jd = jd_agent.generate_job_description(job_title, skills, experience)
        
        return render_template('jd_generator.html', generated_jd=generated_jd)
    
    return render_template('jd_generator.html')

@app.route('/resume-ranker', methods=['GET', 'POST'])
def resume_ranker():
    """Resume Ranker page and functionality"""
    if request.method == 'POST':
        # Get form data
        job_description = request.form.get('job_description')
        
        # Check if files were uploaded
        if 'resumes' not in request.files:
            return render_template('resume_ranker.html', error="No resume files uploaded")
        
        files = request.files.getlist('resumes')
        
        # Save files temporarily
        temp_dir = Path("data/resumes/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Clear temp directory
        for file in temp_dir.glob("*"):
            file.unlink()
            
        resume_paths = []
        for file in files:
            if file.filename:
                file_path = temp_dir / file.filename
                file.save(file_path)
                resume_paths.append(str(file_path))
        
        # Initialize model
        model = initialize_model()
        if model is None:
            return render_template('resume_ranker.html', error="Failed to initialize the Llama model")
        
        # Rank resumes
        ranker = ResumeRanker(model)
        ranked_resumes = ranker.rank_resumes(job_description, resume_paths)
        
        return render_template('resume_ranker.html', ranked_resumes=ranked_resumes)
    
    return render_template('resume_ranker.html')

@app.route('/email-automation', methods=['GET', 'POST'])
def email_automation():
    """Email Automation page and functionality"""
    if request.method == 'POST':
        # Get form data
        email_type = request.form.get('email_type')
        recipient_name = request.form.get('recipient_name')
        recipient_email = request.form.get('recipient_email')
        job_title = request.form.get('job_title')
        custom_message = request.form.get('custom_message')
        
        # Initialize model
        model = initialize_model()
        if model is None:
            return render_template('email_automation.html', error="Failed to initialize the Llama model")
        
        # Generate and send email
        email_agent = EmailAutomation(model)
        email_result = email_agent.generate_email(
            email_type, recipient_name, recipient_email, job_title, custom_message
        )
        
        return render_template('email_automation.html', email_result=email_result)
    
    return render_template('email_automation.html')

@app.route('/interview-scheduler', methods=['GET', 'POST'])
def interview_scheduler():
    """Interview Scheduler page and functionality"""
    if request.method == 'POST':
        # Get form data
        candidate_name = request.form.get('candidate_name')
        candidate_email = request.form.get('candidate_email')
        interview_date = request.form.get('interview_date')
        interview_time = request.form.get('interview_time')
        interviewer_name = request.form.get('interviewer_name')
        interviewer_email = request.form.get('interviewer_email')
        job_title = request.form.get('job_title')
        
        # Initialize model
        model = initialize_model()
        if model is None:
            return render_template('interview_scheduler.html', error="Failed to initialize the Llama model")
        
        # Schedule interview
        scheduler = InterviewScheduler(model)
        schedule_result = scheduler.schedule_interview(
            candidate_name, candidate_email, interview_date, interview_time,
            interviewer_name, interviewer_email, job_title
        )
        
        return render_template('interview_scheduler.html', schedule_result=schedule_result)
    
    return render_template('interview_scheduler.html')

@app.route('/interview-agent', methods=['GET', 'POST'])
def interview_agent():
    """Interview Agent page and functionality"""
    if request.method == 'POST':
        # Get form data
        job_title = request.form.get('job_title')
        candidate_name = request.form.get('candidate_name')
        experience_level = request.form.get('experience_level')
        question = request.form.get('question')
        
        # Initialize model
        model = initialize_model()
        if model is None:
            return render_template('interview_agent.html', error="Failed to initialize the Llama model")
        
        # Generate interview question or response
        interview_bot = InterviewAgent(model)
        if 'generate_questions' in request.form:
            # Generate interview questions
            questions = interview_bot.generate_questions(job_title, experience_level)
            return render_template('interview_agent.html', questions=questions)
        else:
            # Process candidate's answer
            feedback = interview_bot.evaluate_answer(question, job_title, experience_level)
            return render_template('interview_agent.html', feedback=feedback)
    
    return render_template('interview_agent.html')

@app.route('/hire-recommendation', methods=['GET', 'POST'])
def hire_recommendation():
    """Hire Recommendation page and functionality"""
    if request.method == 'POST':
        # Get form data
        interview_transcript = request.form.get('interview_transcript')
        job_title = request.form.get('job_title')
        experience_required = request.form.get('experience_required')
        
        # Initialize model
        model = initialize_model()
        if model is None:
            return render_template('hire_recommendation.html', error="Failed to initialize the Llama model")
        
        # Generate recommendation
        recommender = HireRecommendationAgent(model)
        recommendation = recommender.generate_recommendation(
            interview_transcript, job_title, experience_required
        )
        
        return render_template('hire_recommendation.html', recommendation=recommendation)
    
    return render_template('hire_recommendation.html')

@app.route('/sentiment-analyzer', methods=['GET', 'POST'])
def sentiment_analyzer():
    """Sentiment Analyzer page and functionality"""
    if request.method == 'POST':
        # Get form data
        transcript = request.form.get('transcript')
        
        # Initialize model
        model = initialize_model()
        if model is None:
            return render_template('sentiment_analyzer.html', error="Failed to initialize the Llama model")
        
        # Analyze sentiment
        analyzer = SentimentAnalyzer(model)
        analysis = analyzer.analyze_sentiment(transcript)
        
        return render_template('sentiment_analyzer.html', analysis=analysis)
    
    return render_template('sentiment_analyzer.html')

if __name__ == '__main__':
    # Initialize the model at startup
    initialize_model()
    app.run(debug=True, host='0.0.0.0', port=5000)