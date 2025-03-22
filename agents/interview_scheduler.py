from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
from models.llama_model import LlamaModel
from utils.calendar_api import create_calendar_event, get_available_slots

class InterviewScheduler:
    """Agent for scheduling interviews and managing calendar events"""
    
    def __init__(self, llama_model: LlamaModel):
        """
        Initialize the Interview Scheduler
        
        Args:
            llama_model: Instance of the LlamaModel
        """
        self.model = llama_model
    
    def find_available_slots(self, interviewer_ids: List[str], 
                           candidate_availability: List[Dict[str, Any]],
                           duration_minutes: int = 60,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Find available interview slots based on interviewer and candidate availability
        
        Args:
            interviewer_ids: List of interviewer IDs
            candidate_availability: List of candidate's available time windows
            duration_minutes: Interview duration in minutes
            start_date: Start date for search window (defaults to today)
            end_date: End date for search window (defaults to 14 days from start)
            
        Returns:
            List of available time slots
        """
        if start_date is None:
            start_date = datetime.now()
        
        if end_date is None:
            end_date = start_date + timedelta(days=14)
        
        # Get interviewer availability
        interviewer_slots = []
        for interviewer_id in interviewer_ids:
            slots = get_available_slots(interviewer_id, start_date, end_date)
            interviewer_slots.append(slots)
        
        # Find common available slots
        common_slots = self._find_common_slots(interviewer_slots, candidate_availability, 
                                             duration_minutes)
        
        return common_slots
    
    def schedule_interview(self, candidate_name: str, job_title: str, 
                         interviewer_names: List[str], datetime_slot: datetime,
                         duration_minutes: int = 60, location: str = "Virtual",
                         additional_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Schedule an interview and create calendar events
        
        Args:
            candidate_name: Name of the candidate
            job_title: Job title being interviewed for
            interviewer_names: List of interviewer names
            datetime_slot: Selected interview date and time
            duration_minutes: Interview duration in minutes
            location: Interview location or meeting link
            additional_info: Additional details for the interview
            
        Returns:
            Dictionary with event details
        """
        # Generate interview title and description
        event_details = self._generate_interview_details(candidate_name, job_title, 
                                                     interviewer_names, location, 
                                                     additional_info)
        
        # Calculate end time
        end_time = datetime_slot + timedelta(minutes=duration_minutes)
        
        # Create calendar event (simulated)
        event_id = str(uuid.uuid4())
        event = {
            "id": event_id,
            "title": event_details["title"],
            "description": event_details["description"],
            "start": datetime_slot,
            "end": end_time,
            "location": location,
            "attendees": [{"name": name} for name in interviewer_names] + [{"name": candidate_name}]
        }
        
        # In a real implementation, we would call the calendar API
        # create_calendar_event(event)
        
        return event
    
    def generate_interview_preparation(self, job_title: str, candidate_resume: str, 
                                     interview_type: str = "technical") -> Dict[str, Any]:
        """
        Generate interview questions and preparation materials
        
        Args:
            job_title: Job title for the interview
            candidate_resume: Text of the candidate's resume
            interview_type: Type of interview (technical, behavioral, etc.)
            
        Returns:
            Dictionary with interview preparation materials
        """
        # Truncate resume if too long
        max_length = 1500
        resume_truncated = candidate_resume[:max_length]
        
        # Create prompt for Llama
        prompt = f"""
You are an expert recruitment specialist preparing for a {interview_type} interview for a {job_title} position.

Candidate's Resume:
{resume_truncated}

Generate a comprehensive interview preparation guide including:
1. 8-10 specific questions based on the candidate's background and the job requirements
2. Key areas to explore based on the candidate's experience
3. Skills to verify during the interview
4. Red flags to watch for
5. Recommended interview structure

Format the output clearly with appropriate sections and numbering.
"""
        
        # Generate preparation guide
        response = self.model.generate(prompt, max_tokens=1024, temperature=0.7)
        
        return {
            "job_title": job_title,
            "interview_type": interview_type,
            "preparation_guide": response
        }
    
    def _generate_interview_details(self, candidate_name: str, job_title: str,
                                  interviewer_names: List[str], location: str,
                                  additional_info: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Generate interview event title and description
        
        Args:
            candidate_name: Name of the candidate
            job_title: Job title
            interviewer_names: List of interviewer names
            location: Interview location
            additional_info: Additional details
            
        Returns:
            Dictionary with title and description
        """
        # Format interviewer names
        interviewers_str = ", ".join(interviewer_names)
        
        # Additional info formatting
        add_info_str = ""
        if additional_info:
            for key, value in additional_info.items():
                add_info_str += f"{key.capitalize()}: {value}\n"
        
        # Generate calendar event details
        title = f"Interview: {candidate_name} for {job_title} position"
        
        description = f"""
Interview for {job_title} position

Candidate: {candidate_name}
Interviewers: {interviewers_str}
Location: {location}

{add_info_str}
"""
        
        return {
            "title": title,
            "description": description.strip()
        }
    
    def _find_common_slots(self, interviewer_slots: List[List[Dict[str, datetime]]], 
                         candidate_slots: List[Dict[str, datetime]],
                         duration_minutes: int) -> List[Dict[str, Any]]:
        """
        Find common available time slots
        
        This is a simplified implementation for demo purposes
        """
        # In a real implementation, this would find overlapping availability
        # For this demo, we'll return some dummy slots
        
        # Get current date and time
        now = datetime.now()
        
        # Generate some sample slots for the next week
        common_slots = []
        for i in range(1, 6):  # Next 5 business days
            day = now + timedelta(days=i)
            # Morning slot at 10 AM
            morning = datetime(day.year, day.month, day.day, 10, 0)
            # Afternoon slot at 2 PM
            afternoon = datetime(day.year, day.month, day.day, 14, 0)
            
            common_slots.append({
                "start": morning,
                "end": morning + timedelta(minutes=duration_minutes)
            })
            
            common_slots.append({
                "start": afternoon,
                "end": afternoon + timedelta(minutes=duration_minutes)
            })

        return common_slots