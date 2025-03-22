import unittest
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Import all agents
from agents.jd_generator import JDGenerator
from agents.resume_ranker import ResumeRanker
from agents.email_automation import EmailAutomation
from agents.interview_scheduler import InterviewScheduler
from agents.interview_agent import InterviewAgent
from agents.hire_recommendation import HireRecommendationAgent
from agents.sentiment_analyzer import SentimentAnalyzer

# Import utilities and models
from models.llama_model import LlamaModel
from utils.pdf_parser import PDFParser
from utils.email_sender import EmailSender
from utils.calendar_api import create_calendar_event, get_available_slots

class TestJDGenerator(unittest.TestCase):
    """Tests for the Job Description Generator agent"""
    
    def setUp(self):
        # Mock the LlamaModel to avoid actual API calls during testing
        self.model_patcher = patch('models.llama_model.LlamaModel')
        self.mock_model = self.model_patcher.start()
        
        # Configure the mock model's generate_structured_output method
        self.mock_model.return_value.generate_structured_output.return_value = {
            "job_title": "Senior Software Engineer",
            "department": "Engineering",
            "location": "Remote",
            "summary": "We are seeking a Senior Software Engineer to join our team...",
            "responsibilities": [
                "Design and develop scalable software solutions",
                "Collaborate with cross-functional teams"
            ],
            "requirements": [
                "5+ years of experience in software development",
                "Proficiency in Python and JavaScript"
            ],
            "benefits": [
                "Competitive salary and benefits package",
                "Remote work flexibility"
            ]
        }
        
        # Create the JD Generator with the mocked model
        self.jd_generator = JDGenerator(llama_model=self.mock_model.return_value)
    
    def tearDown(self):
        self.model_patcher.stop()
    
    def test_generate_job_description(self):
        """Test that job description generation works correctly"""
        # Define test inputs
        job_title = "Senior Software Engineer"
        skills = ["Python", "JavaScript", "AWS", "Docker"]
        experience_level = "Senior"
        
        # Call the method being tested
        result = self.jd_generator.generate_job_description(
            job_title=job_title,
            skills=skills,
            experience_level=experience_level,
            department="Engineering",
            location="Remote"
        )
        
        # Verify the result contains expected fields
        self.assertEqual(result["job_title"], "Senior Software Engineer")
        self.assertIn("responsibilities", result)
        self.assertIn("requirements", result)
        self.assertIsInstance(result["responsibilities"], list)
        self.assertIsInstance(result["requirements"], list)
        
        # Verify the model was called with correct parameters
        self.mock_model.return_value.generate_structured_output.assert_called_once()


class TestResumeRanker(unittest.TestCase):
    """Tests for the Resume Ranker agent"""
    
    def setUp(self):
        # Mock the LlamaModel
        self.model_patcher = patch('models.llama_model.LlamaModel')
        self.mock_model = self.model_patcher.start()
        
        # Configure mock return value for ranking
        self.mock_model.return_value.generate_structured_output.return_value = {
            "ranked_candidates": [
                {
                    "candidate_id": "1",
                    "name": "Jane Smith",
                    "match_score": 92,
                    "strengths": ["Python expertise", "5 years experience"],
                    "gaps": ["No AWS experience"]
                },
                {
                    "candidate_id": "2",
                    "name": "John Doe",
                    "match_score": 85,
                    "strengths": ["Strong problem-solving skills"],
                    "gaps": ["Limited Python experience"]
                }
            ],
            "summary": "2 candidates evaluated. Top candidate has strong technical skills."
        }
        
        # Mock the PDFParser
        self.pdf_parser_patcher = patch('utils.pdf_parser.PDFParser')
        self.mock_pdf_parser = self.pdf_parser_patcher.start()
        
        # Configure the mock PDF parser's batch_parse_resumes method
        self.mock_pdf_parser.batch_parse_resumes.return_value = [
            {
                "candidate_name": "Jane Smith",
                "email": "jane@example.com",
                "skills": ["Python", "JavaScript", "SQL"],
                "experience": "5 years software development experience",
                "filename": "jane_smith.pdf"
            },
            {
                "candidate_name": "John Doe",
                "email": "john@example.com",
                "skills": ["Java", "C++", "Problem Solving"],
                "experience": "3 years software development experience",
                "filename": "john_doe.pdf"
            }
        ]
        
        # Create the Resume Ranker with the mocked dependencies
        self.resume_ranker = ResumeRanker(llama_model=self.mock_model.return_value)
    
    def tearDown(self):
        self.model_patcher.stop()
        self.pdf_parser_patcher.stop()
    
    def test_rank_resumes(self):
        """Test that resume ranking works correctly"""
        # Define a sample job description
        job_description = {
            "job_title": "Software Engineer",
            "requirements": ["Python", "JavaScript", "AWS"],
            "responsibilities": ["Develop web applications", "Work in agile teams"]
        }
        
        # Define the path to sample resumes
        resumes_dir = "data/resumes"
        
        # Mock the batch_parse_resumes method to use our test fixture
        with patch('utils.pdf_parser.PDFParser.batch_parse_resumes',
                  return_value=self.mock_pdf_parser.batch_parse_resumes.return_value):
            # Call the method being tested
            result = self.resume_ranker.rank_resumes(job_description, resumes_dir)
        
        # Verify the result structure
        self.assertIn("ranked_candidates", result)
        self.assertIn("summary", result)
        self.assertEqual(len(result["ranked_candidates"]), 2)
        
        # Verify the ranking - first candidate should be the top match
        self.assertEqual(result["ranked_candidates"][0]["name"], "Jane Smith")
        self.assertTrue(result["ranked_candidates"][0]["match_score"] > 
                        result["ranked_candidates"][1]["match_score"])


class TestEmailAutomation(unittest.TestCase):
    """Tests for the Email Automation agent"""
    
    def setUp(self):
        # Mock the LlamaModel
        self.model_patcher = patch('models.llama_model.LlamaModel')
        self.mock_model = self.model_patcher.start()
        
        # Configure mock return value for email generation
        self.mock_model.return_value.generate_completion.return_value = """
        Subject: Interview Invitation: Software Engineer Position at Company
        
        Dear {name},
        
        Thank you for applying to the Software Engineer position at Company. We were impressed with your qualifications and would like to invite you for an interview.
        
        Best regards,
        Recruitment Team
        """
        
        # Mock the EmailSender
        self.email_sender_patcher = patch('utils.email_sender.EmailSender')
        self.mock_email_sender = self.email_sender_patcher.start()
        
        # Configure the mock send_email method
        self.mock_email_sender.return_value.send_email.return_value = "email_123"
        self.mock_email_sender.return_value.send_bulk_email.return_value = ["email_123", "email_124"]
        
        # Create the Email Automation agent with the mocked dependencies
        self.email_automation = EmailAutomation(
            llama_model=self.mock_model.return_value,
            email_sender=self.mock_email_sender.return_value
        )
    
    def tearDown(self):
        self.model_patcher.stop()
        self.email_sender_patcher.stop()
    
    def test_send_interview_invitation(self):
        """Test sending an interview invitation email"""
        # Define test inputs
        candidate = {
            "name": "Jane Smith",
            "email": "jane@example.com"
        }
        job_title = "Software Engineer"
        
        # Call the method being tested
        result = self.email_automation.send_interview_invitation(
            candidate=candidate,
            job_title=job_title,
            company_name="Company",
            interview_date=datetime.now() + timedelta(days=5),
            interview_duration=45,
            interview_type="Video"
        )
        
        # Verify the result
        self.assertIn("email_id", result)
        self.assertIn("status", result)
        self.assertEqual(result["status"], "sent")
        
        # Verify the model and email sender were called correctly
        self.mock_model.return_value.generate_completion.assert_called_once()
        self.mock_email_sender.return_value.send_email.assert_called_once_with(
            recipient_email=candidate["email"],
            recipient_name=candidate["name"],
            subject=unittest.mock.ANY,  # We don't know the exact subject from the mock
            body=unittest.mock.ANY      # We don't know the exact body from the mock
        )
    
    def test_send_bulk_status_update(self):
        """Test sending bulk status update emails"""
        # Define test inputs
        candidates = [
            {"name": "Jane Smith", "email": "jane@example.com"},
            {"name": "John Doe", "email": "john@example.com"}
        ]
        
        # Call the method being tested
        result = self.email_automation.send_bulk_status_update(
            candidates=candidates,
            status_update="Application Received",
            job_title="Software Engineer",
            company_name="Company",
            next_steps="We will review your application within the next week."
        )
        
        # Verify the result
        self.assertIn("email_ids", result)
        self.assertIn("status", result)
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["email_ids"]), 2)
        
        # Verify the model and email sender were called correctly
        self.mock_model.return_value.generate_completion.assert_called_once()
        self.mock_email_sender.return_value.send_bulk_email.assert_called_once()


class TestInterviewScheduler(unittest.TestCase):
    """Tests for the Interview Scheduler agent"""
    
    def setUp(self):
        # Mock the calendar API functions
        self.calendar_patcher = patch('utils.calendar_api.get_available_slots')
        self.mock_get_slots = self.calendar_patcher.start()
        
        # Configure mock available slots
        tomorrow = datetime.now() + timedelta(days=1)
        self.mock_get_slots.return_value = [
            {
                'start': tomorrow.replace(hour=10, minute=0),
                'end': tomorrow.replace(hour=11, minute=0)
            },
            {
                'start': tomorrow.replace(hour=14, minute=0),
                'end': tomorrow.replace(hour=15, minute=0)
            }
        ]
        
        # Mock create_calendar_event
        self.create_event_patcher = patch('utils.calendar_api.create_calendar_event')
        self.mock_create_event = self.create_event_patcher.start()
        self.mock_create_event.return_value = "event_123"
        
        # Mock the EmailAutomation agent
        self.email_patcher = patch('agents.email_automation.EmailAutomation')
        self.mock_email = self.email_patcher.start()
        self.mock_email.return_value.send_interview_invitation.return_value = {
            "email_id": "email_123",
            "status": "sent"
        }
        
        # Create the Interview Scheduler with mocked dependencies
        self.interview_scheduler = InterviewScheduler(
            email_automation=self.mock_email.return_value
        )
    
    def tearDown(self):
        self.calendar_patcher.stop()
        self.create_event_patcher.stop()
        self.email_patcher.stop()
    
    def test_schedule_interview(self):
        """Test scheduling an interview"""
        # Define test inputs
        candidate = {
            "name": "Jane Smith",
            "email": "jane@example.com"
        }
        interviewers = [
            {"name": "HR Manager", "email": "hr@company.com"},
            {"name": "Tech Lead", "email": "tech@company.com"}
        ]
        job_title = "Software Engineer"
        
        # Call the method being tested
        start_date = datetime.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=5)
        
        result = self.interview_scheduler.schedule_interview(
            candidate=candidate,
            interviewers=interviewers,
            job_title=job_title,
            company_name="Company",
            interview_type="Technical",
            interview_duration=45,
            start_date=start_date,
            end_date=end_date
        )
        
        # Verify the result
        self.assertIn("event_id", result)
        self.assertIn("interview_time", result)
        self.assertIn("status", result)
        self.assertEqual(result["status"], "scheduled")
        
        # Verify calendar and email functions were called correctly
        self.mock_get_slots.assert_called_once()
        self.mock_create_event.assert_called_once()
        self.mock_email.return_value.send_interview_invitation.assert_called_once()


class TestInterviewAgent(unittest.TestCase):
    """Tests for the Interview Agent"""
    
    def setUp(self):
        # Mock the LlamaModel
        self.model_patcher = patch('models.llama_model.LlamaModel')
        self.mock_model = self.model_patcher.start()
        
        # Configure mock for generating questions
        self.mock_model.return_value.generate_structured_output.return_value = {
            "questions": [
                {
                    "question": "Can you describe your experience with Python?",
                    "purpose": "Technical assessment",
                    "follow_ups": ["What Python libraries have you used?"]
                },
                {
                    "question": "How do you approach problem-solving?",
                    "purpose": "Soft skills assessment",
                    "follow_ups": ["Can you provide an example?"]
                }
            ]
        }
        
        # Configure mock for analyzing responses
        self.mock_model.return_value.generate_completion.return_value = """
        The candidate demonstrated strong Python knowledge, particularly in data processing.
        They had good problem-solving approaches but could improve communication clarity.
        """
        
        # Create the Interview Agent with mocked model
        self.interview_agent = InterviewAgent(llama_model=self.mock_model.return_value)
    
    def tearDown(self):
        self.model_patcher.stop()
    
    def test_generate_interview_questions(self):
        """Test generating interview questions"""
        # Define job details
        job_description = {
            "job_title": "Software Engineer",
            "requirements": ["Python", "JavaScript", "Problem-solving"],
            "responsibilities": ["Develop applications", "Debug issues"]
        }
        interview_type = "Technical"
        
        # Call the method being tested
        result = self.interview_agent.generate_interview_questions(
            job_description=job_description,
            candidate_resume={"skills": ["Python", "Java"]},
            interview_type=interview_type,
            question_count=5
        )
        
        # Verify the result
        self.assertIn("questions", result)
        self.assertIsInstance(result["questions"], list)
        self.assertTrue(len(result["questions"]) > 0)
        
        # Verify each question has the required fields
        for question in result["questions"]:
            self.assertIn("question", question)
            self.assertIn("purpose", question)
            self.assertIn("follow_ups", question)
    
    def test_analyze_candidate_response(self):
        """Test analyzing candidate responses"""
        # Define a candidate response
        question = "Can you describe your experience with Python?"
        response = "I've used Python for 3 years, mainly for data processing with pandas and scikit-learn."
        
        # Call the method being tested
        result = self.interview_agent.analyze_candidate_response(
            question=question,
            response=response,
            job_requirements=["Python", "Data science"],
            assessment_criteria={"technical_skills": 0.7, "communication": 0.3}
        )
        
        # Verify the result
        self.assertIn("analysis", result)
        self.assertIn("strengths", result)
        self.assertIn("areas_for_improvement", result)
        self.assertIn("follow_up_suggestions", result)


class TestHireRecommendationAgent(unittest.TestCase):
    """Tests for the Hire Recommendation Agent"""
    
    def setUp(self):
        # Mock the LlamaModel
        self.model_patcher = patch('models.llama_model.LlamaModel')
        self.mock_model = self.model_patcher.start()
        
        # Configure mock return value for recommendation
        self.mock_model.return_value.generate_structured_output.return_value = {
            "candidate_name": "Jane Smith",
            "recommendation": "Hire",
            "confidence_score": 85,
            "strengths": [
                "Strong technical skills in Python and data science",
                "Excellent problem-solving abilities"
            ],
            "weaknesses": [
                "Limited experience with cloud technologies",
                "Could improve communication of complex concepts"
            ],
            "fit_for_role": "The candidate's skills align well with the job requirements",
            "summary": "Jane demonstrated strong technical capabilities and would be a valuable addition to the team."
        }
        
        # Create the Hire Recommendation Agent with mocked model
        self.hire_agent = HireRecommendationAgent(llama_model=self.mock_model.return_value)
    
    def tearDown(self):
        self.model_patcher.stop()
    
    def test_generate_hire_recommendation(self):
        """Test generating a hire recommendation"""
        # Define test inputs
        job_description = {
            "job_title": "Data Scientist",
            "requirements": ["Python", "Machine Learning", "Statistics"],
            "responsibilities": ["Build ML models", "Data analysis"]
        }
        
        interview_transcript = """
        Interviewer: Can you describe your experience with Python?
        Candidate: I've used Python for 5 years, mainly for data science projects.
        
        Interviewer: How do you approach a new machine learning problem?
        Candidate: I start by understanding the data and business requirements...
        """
        
        # Call the method being tested
        result = self.hire_agent.generate_hire_recommendation(
            candidate_name="Jane Smith",
            job_description=job_description,
            interview_transcript=interview_transcript,
            candidate_resume={"skills": ["Python", "Machine Learning"]}
        )
        
        # Verify the result
        self.assertIn("recommendation", result)
        self.assertIn("confidence_score", result)
        self.assertIn("strengths", result)
        self.assertIn("weaknesses", result)
        
        # Verify the recommendation is one of the expected values
        self.assertIn(result["recommendation"], ["Hire", "No Hire", "Consider"])


class TestSentimentAnalyzer(unittest.TestCase):
    """Tests for the Sentiment Analyzer agent"""
    
    def setUp(self):
        # Mock the LlamaModel
        self.model_patcher = patch('models.llama_model.LlamaModel')
        self.mock_model = self.model_patcher.start()
        
        # Configure mock return value for sentiment analysis
        self.mock_model.return_value.generate_structured_output.return_value = {
            "overall_sentiment": "Positive",
            "confidence_score": 78,
            "key_moments": [
                {
                    "timestamp": "00:05:30",
                    "topic": "Python experience",
                    "sentiment": "Very positive",
                    "indicators": ["Enthusiastic tone", "Detailed explanations"]
                },
                {
                    "timestamp": "00:12:45",
                    "topic": "Team collaboration",
                    "sentiment": "Neutral",
                    "indicators": ["Brief responses", "Limited examples"]
                }
            ],
            "communication_style": {
                "clarity": "High",
                "engagement": "Medium",
                "authenticity": "High"
            },
            "summary": "The candidate showed high enthusiasm when discussing technical topics but was more reserved when discussing team experiences."
        }
        
        # Create the Sentiment Analyzer with mocked model
        self.sentiment_analyzer = SentimentAnalyzer(llama_model=self.mock_model.return_value)
    
    def tearDown(self):
        self.model_patcher.stop()
    
    def test_analyze_interview_sentiment(self):
        """Test analyzing interview sentiment"""
        # Define a sample interview transcript
        transcript = """
        [00:05:30] Interviewer: Can you tell me about your experience with Python?
        [00:05:35] Candidate: I've been working with Python for over 5 years now. I absolutely love the language because of its versatility and readability. I've used it for everything from data analysis to web development with Django.
        
        [00:12:45] Interviewer: How do you approach team collaboration?
        [00:12:50] Candidate: I work well with teams. I've been part of several team projects.
        """
        
        # Call the method being tested
        result = self.sentiment_analyzer.analyze_interview_sentiment(
            interview_transcript=transcript,
            job_title="Software Engineer",
            key_topics=["Python experience", "Team collaboration"]
        )
        
        # Verify the result
        self.assertIn("overall_sentiment", result)
        self.assertIn("confidence_score", result)
        self.assertIn("key_moments", result)
        self.assertIsInstance(result["key_moments"], list)
        
        # Verify the overall sentiment is one of the expected values
        self.assertIn(result["overall_sentiment"], ["Positive", "Negative", "Neutral", "Mixed"])


if __name__ == '__main__':
    unittest.main()