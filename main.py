#!/usr/bin/env python3
"""
Llama Agentic AI Recruitment App
Main entry point for the application that orchestrates all AI agents.
"""

import os
import argparse
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import agents
try:
    from agents.jd_generator import JDGenerator
    from agents.resume_ranker import ResumeRanker
    from agents.email_automation import EmailAutomation
    from agents.interview_scheduler import InterviewScheduler
    from agents.interview_agent import InterviewAgent
    from agents.hire_recommendation import HireRecommendationAgent
    from agents.sentiment_analyzer import SentimentAnalyzer
    from models.llama_model import LlamaModel
except ImportError as e:
    logger.error(f"Failed to import necessary modules: {str(e)}")
    logger.info("Make sure you've installed all dependencies from requirements.txt")
    exit(1)

def setup_environment():
    """Check and setup necessary directories and environment variables."""
    # Check for required directories
    required_dirs = ["data/job_descriptions", "data/resumes"]
    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Checked directory: {dir_path}")
    
    # Check for model availability
    model_path = os.getenv("LLAMA_MODEL_PATH", "models/llama-model")
    if not os.path.exists(model_path):
        logger.warning(f"Model directory not found at {model_path}. Please configure LLAMA_MODEL_PATH.")
    
    # Load configuration
    try:
        import config
        logger.info("Configuration loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        return False

def initialize_llama_model():
    """Initialize and return the Llama model instance."""
    try:
        model = LlamaModel()
        logger.info("Llama model initialized successfully")
        return model
    except Exception as e:
        logger.error(f"Failed to initialize Llama model: {str(e)}")
        return None

def list_available_agents():
    """Display a list of available agents in the system."""
    agents = [
        "JD Generator (jd)",
        "Resume Ranker (ranker)",
        "Email Automation (email)",
        "Interview Scheduler (scheduler)",
        "Interview Agent (interview)",
        "Hire Recommendation (recommendation)",
        "Sentiment Analyzer (sentiment)"
    ]
    
    print("\n=== Available Agents ===")
    for agent in agents:
        print(f"- {agent}")
    print("\nUse the command 'python main.py run <agent_shortname>' to run a specific agent")
    print("For example: 'python main.py run jd'")
    print("\nOr use 'python main.py run all' to run the complete workflow")

def run_jd_generator(model):
    """Run the JD Generator agent."""
    print("\n=== Running JD Generator ===")
    try:
        jd_agent = JDGenerator(model)
        job_title = input("Enter job title: ")
        skills = input("Enter required skills (comma separated): ")
        experience = input("Enter experience level: ")
        
        jd = jd_agent.generate_job_description(job_title, skills.split(','), experience)
        print("\nGenerated Job Description:")
        print(jd)
        
        # Save the job description
        save_option = input("\nSave this job description? (y/n): ")
        if save_option.lower() == 'y':
            filename = input("Enter filename (without extension): ")
            with open(f"data/job_descriptions/{filename}.txt", "w") as f:
                f.write(jd)
            print(f"Job description saved to data/job_descriptions/{filename}.txt")
        
        return True
    except Exception as e:
        logger.error(f"Error in JD Generator: {str(e)}")
        return False

def run_resume_ranker(model):
    """Run the Resume Ranker agent."""
    print("\n=== Running Resume Ranker ===")
    try:
        # List available job descriptions
        jd_dir = "data/job_descriptions"
        jd_files = [f for f in os.listdir(jd_dir) if os.path.isfile(os.path.join(jd_dir, f))]
        
        if not jd_files:
            print("No job descriptions found. Please create one using the JD Generator first.")
            return False
        
        print("Available job descriptions:")
        for i, jd_file in enumerate(jd_files):
            print(f"{i+1}. {jd_file}")
        
        jd_idx = int(input("Select job description (number): ")) - 1
        selected_jd = os.path.join(jd_dir, jd_files[jd_idx])
        
        with open(selected_jd, 'r') as f:
            job_description = f.read()
        
        # List available resumes
        resume_dir = "data/resumes"
        resume_files = [f for f in os.listdir(resume_dir) if os.path.isfile(os.path.join(resume_dir, f))]
        
        if not resume_files:
            print("No resumes found in the data/resumes directory.")
            print("Please add resume files before using this agent.")
            return False
        
        # Load and rank resumes
        ranker = ResumeRanker(model)
        resumes = []
        
        for resume_file in resume_files:
            file_path = os.path.join(resume_dir, resume_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    resumes.append({
                        'filename': resume_file,
                        'content': content
                    })
            except Exception as e:
                logger.warning(f"Could not read {resume_file}: {str(e)}")
        
        if not resumes:
            print("No readable resumes found.")
            return False
        
        ranked_resumes = ranker.rank_resumes(job_description, resumes)
        
        print("\n=== Ranked Resumes ===")
        for i, resume in enumerate(ranked_resumes):
            print(f"{i+1}. {resume['filename']} - Score: {resume['score']}")
        
        return True
    except Exception as e:
        logger.error(f"Error in Resume Ranker: {str(e)}")
        return False

def run_email_automation(model):
    """Run the Email Automation agent."""
    print("\n=== Running Email Automation ===")
    try:
        email_agent = EmailAutomation(model)
        recipient = input("Enter recipient email: ")
        subject = input("Enter email subject: ")
        template_type = input("Enter email type (invite/rejection/followup): ")
        
        candidate_name = input("Enter candidate name: ")
        job_title = input("Enter job title: ")
        company_name = input("Enter company name: ")
        
        email_content = email_agent.generate_email(
            template_type, 
            {
                'candidate_name': candidate_name,
                'job_title': job_title,
                'company_name': company_name
            }
        )
        
        print("\nGenerated Email:")
        print(f"To: {recipient}")
        print(f"Subject: {subject}")
        print(f"Body:\n{email_content}")
        
        send_option = input("\nSimulate sending this email? (y/n): ")
        if send_option.lower() == 'y':
            success = email_agent.send_email(recipient, subject, email_content)
            if success:
                print("Email sent successfully (simulated)")
            else:
                print("Failed to send email (simulated)")
        
        return True
    except Exception as e:
        logger.error(f"Error in Email Automation: {str(e)}")
        return False

def run_interview_scheduler(model):
    """Run the Interview Scheduler agent."""
    print("\n=== Running Interview Scheduler ===")
    try:
        scheduler = InterviewScheduler(model)
        
        candidate_email = input("Enter candidate email: ")
        interviewer_email = input("Enter interviewer email: ")
        interview_date = input("Enter preferred date (YYYY-MM-DD): ")
        interview_time = input("Enter preferred time (HH:MM): ")
        duration = input("Enter duration in minutes (default: 60): ") or "60"
        job_title = input("Enter job title: ")
        
        datetime_str = f"{interview_date} {interview_time}"
        
        success = scheduler.schedule_interview(
            candidate_email, 
            interviewer_email, 
            datetime_str, 
            int(duration), 
            job_title
        )
        
        if success:
            print("Interview scheduled successfully (simulated)")
            print("Calendar invitations have been sent (simulated)")
        else:
            print("Failed to schedule interview (simulated)")
        
        return True
    except Exception as e:
        logger.error(f"Error in Interview Scheduler: {str(e)}")
        return False

def run_interview_agent(model):
    """Run the Interview Agent to conduct a simulated interview."""
    print("\n=== Running Interview Agent ===")
    print("This agent will simulate a job interview.")
    try:
        job_title = input("Enter job title for the interview: ")
        years_experience = input("Enter years of experience (for question calibration): ")
        
        interview_agent = InterviewAgent(model)
        interview_agent.initialize_interview(job_title, years_experience)
        
        print("\nStarting interview simulation...")
        print("(Type 'quit' or 'exit' to end the interview)")
        
        transcript = []
        while True:
            question = interview_agent.get_next_question(transcript)
            print(f"\nInterviewer: {question}")
            
            answer = input("You (candidate): ")
            if answer.lower() in ['quit', 'exit']:
                break
            
            transcript.append({
                'question': question,
                'answer': answer
            })
            
            feedback = interview_agent.analyze_answer(question, answer)
            # We don't show the feedback to the candidate in a real interview
            
        print("\nInterview completed.")
        
        save_option = input("Save this interview transcript? (y/n): ")
        if save_option.lower() == 'y':
            candidate_name = input("Enter candidate name: ")
            filename = f"interview_{candidate_name.replace(' ', '_').lower()}_{job_title.replace(' ', '_').lower()}.txt"
            
            with open(f"data/interviews/{filename}", "w") as f:
                f.write(f"Interview for: {candidate_name}\n")
                f.write(f"Position: {job_title}\n")
                f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                
                for entry in transcript:
                    f.write(f"Q: {entry['question']}\n")
                    f.write(f"A: {entry['answer']}\n\n")
            
            print(f"Transcript saved to data/interviews/{filename}")
        
        return True
    except Exception as e:
        logger.error(f"Error in Interview Agent: {str(e)}")
        return False

def run_hire_recommendation(model):
    """Run the Hire Recommendation agent."""
    print("\n=== Running Hire Recommendation Agent ===")
    try:
        # Check if there are saved interviews
        interview_dir = "data/interviews"
        Path(interview_dir).mkdir(parents=True, exist_ok=True)
        
        interview_files = [f for f in os.listdir(interview_dir) if os.path.isfile(os.path.join(interview_dir, f))]
        
        transcript = ""
        if interview_files:
            print("Available interview transcripts:")
            for i, file in enumerate(interview_files):
                print(f"{i+1}. {file}")
            
            option = input("Select a transcript or enter 'n' to input manually: ")
            
            if option.lower() != 'n':
                idx = int(option) - 1
                with open(os.path.join(interview_dir, interview_files[idx]), 'r') as f:
                    transcript = f.read()
        
        if not transcript:
            print("Please provide interview details manually:")
            job_title = input("Enter job title: ")
            transcript = f"Position: {job_title}\n\n"
            
            print("Enter Q&A pairs (enter empty question to finish):")
            while True:
                question = input("Question: ")
                if not question:
                    break
                answer = input("Answer: ")
                transcript += f"Q: {question}\nA: {answer}\n\n"
        
        recommendation_agent = HireRecommendationAgent(model)
        recommendation = recommendation_agent.analyze_interview(transcript)
        
        print("\n=== Candidate Evaluation ===")
        print(f"Strengths: {', '.join(recommendation['strengths'])}")
        print(f"Weaknesses: {', '.join(recommendation['weaknesses'])}")
        print(f"Decision: {recommendation['decision']}")
        print(f"Justification: {recommendation['justification']}")
        
        return True
    except Exception as e:
        logger.error(f"Error in Hire Recommendation: {str(e)}")
        return False

def run_sentiment_analyzer(model):
    """Run the Sentiment Analyzer agent."""
    print("\n=== Running Sentiment Analyzer ===")
    try:
        sentiment_agent = SentimentAnalyzer(model)
        
        # Option to use saved interview or input manually
        option = input("Use saved interview transcript (y) or input text manually (n)? ")
        
        text_to_analyze = ""
        if option.lower() == 'y':
            interview_dir = "data/interviews"
            Path(interview_dir).mkdir(parents=True, exist_ok=True)
            
            interview_files = [f for f in os.listdir(interview_dir) if os.path.isfile(os.path.join(interview_dir, f))]
            
            if not interview_files:
                print("No saved interviews found.")
                return False
            
            print("Available interview transcripts:")
            for i, file in enumerate(interview_files):
                print(f"{i+1}. {file}")
            
            idx = int(input("Select a transcript: ")) - 1
            with open(os.path.join(interview_dir, interview_files[idx]), 'r') as f:
                text_to_analyze = f.read()
        else:
            print("Enter text to analyze (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if not line and lines and not lines[-1]:
                    break
                lines.append(line)
            text_to_analyze = "\n".join(lines)
        
        if not text_to_analyze:
            print("No text provided for analysis.")
            return False
        
        sentiment_results = sentiment_agent.analyze_sentiment(text_to_analyze)
        
        print("\n=== Sentiment Analysis Results ===")
        print(f"Overall Sentiment: {sentiment_results['overall_sentiment']}")
        print(f"Confidence Score: {sentiment_results['confidence']}%")
        print(f"Emotional Tone: {sentiment_results['emotional_tone']}")
        
        if 'key_sentiments' in sentiment_results:
            print("\nKey Sentiment Indicators:")
            for indicator in sentiment_results['key_sentiments']:
                print(f"- {indicator}")
        
        return True
    except Exception as e:
        logger.error(f"Error in Sentiment Analyzer: {str(e)}")
        return False

def run_complete_workflow(model):
    """Run the complete recruitment workflow using all agents."""
    print("\n=== Running Complete Recruitment Workflow ===")
    
    # Step 1: Generate Job Description
    print("\n--- Step 1: Generate Job Description ---")
    if not run_jd_generator(model):
        print("Job Description generation failed. Workflow stopped.")
        return False
    
    # Step 2: Rank Resumes
    print("\n--- Step 2: Rank Resumes ---")
    if not run_resume_ranker(model):
        print("Resume ranking failed. Workflow stopped.")
        return False
    
    # Step 3: Send Interview Invitation
    print("\n--- Step 3: Send Interview Invitation ---")
    if not run_email_automation(model):
        print("Email automation failed. Workflow stopped.")
        return False
    
    # Step 4: Schedule Interview
    print("\n--- Step 4: Schedule Interview ---")
    if not run_interview_scheduler(model):
        print("Interview scheduling failed. Workflow stopped.")
        return False
    
    # Step 5: Conduct Interview
    print("\n--- Step 5: Conduct Interview ---")
    if not run_interview_agent(model):
        print("Interview simulation failed. Workflow stopped.")
        return False
    
    # Step 6: Analyze Sentiment
    print("\n--- Step 6: Analyze Interview Sentiment ---")
    if not run_sentiment_analyzer(model):
        print("Sentiment analysis failed. Workflow stopped.")
        return False
    
    # Step 7: Generate Hire Recommendation
    print("\n--- Step 7: Generate Hire Recommendation ---")
    if not run_hire_recommendation(model):
        print("Hire recommendation failed. Workflow stopped.")
        return False
    
    print("\n=== Complete Recruitment Workflow Finished Successfully ===")
    return True

def main():
    """Main entry point for the application."""
    import datetime  # Import here to avoid issues if this import fails
    
    parser = argparse.ArgumentParser(description="Llama Agentic AI Recruitment App")
    parser.add_argument('action', choices=['run', 'list'], help='Action to perform')
    parser.add_argument('agent', nargs='?', help='Agent to run')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("     Llama Agentic AI Recruitment App")
    print("=" * 60)
    
    # Setup environment
    if not setup_environment():
        logger.error("Environment setup failed. Exiting.")
        return
    
    # Initialize Llama model
    model = initialize_llama_model()
    if not model and args.action == 'run' and args.agent != 'list':
        logger.error("Failed to initialize Llama model. Exiting.")
        return
    
    # Process command
    if args.action == 'list':
        list_available_agents()
        return
    
    if args.action == 'run':
        if not args.agent:
            print("Error: Agent name required with 'run' action")
            print("Use 'python main.py list' to see available agents")
            return
        
        if args.agent == 'jd':
            run_jd_generator(model)
        elif args.agent == 'ranker':
            run_resume_ranker(model)
        elif args.agent == 'email':
            run_email_automation(model)
        elif args.agent == 'scheduler':
            run_interview_scheduler(model)
        elif args.agent == 'interview':
            run_interview_agent(model)
        elif args.agent == 'recommendation':
            run_hire_recommendation(model)
        elif args.agent == 'sentiment':
            run_sentiment_analyzer(model)
        elif args.agent == 'all':
            run_complete_workflow(model)
        else:
            print(f"Unknown agent: {args.agent}")
            print("Use 'python main.py list' to see available agents")
    
    print("\nThank you for using Llama Agentic AI Recruitment App!")

if __name__ == "__main__":
    main()