from typing import Dict, Any, List, Optional
from models.llama_model import LlamaModel
from utils.email_sender import send_email

class EmailAutomation:
    """Agent for automating email communications in the recruitment process"""
    
    def __init__(self, llama_model: LlamaModel):
        """
        Initialize the Email Automation Agent
        
        Args:
            llama_model: Instance of the LlamaModel
        """
        self.model = llama_model
        
        # Email templates by type
        self.email_types = [
            "application_received", 
            "interview_invitation",
            "rejection",
            "offer_letter",
            "follow_up",
            "hiring_team_notification"
        ]
    
    def generate_email(self, email_type: str, recipient_name: str, 
                      job_title: str, company_name: str = "Our Company",
                      additional_info: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Generate a personalized email based on email type and recipient info
        
        Args:
            email_type: Type of email to generate
            recipient_name: Name of the recipient
            job_title: Job title
            company_name: Company name
            additional_info: Additional information for personalization
            
        Returns:
            Dictionary with subject and body
        """
        # Validate email type
        if email_type not in self.email_types:
            raise ValueError(f"Invalid email type. Choose from: {', '.join(self.email_types)}")
        
        # Prepare additional info string
        add_info_str = ""
        if additional_info:
            for key, value in additional_info.items():
                add_info_str += f"- {key.capitalize()}: {value}\n"
        
        # Create prompt for Llama
        prompt = f"""
You are an expert recruitment communication specialist. Generate a professional, personalized email for the following scenario:

Email Type: {email_type}
Recipient: {recipient_name}
Job Title: {job_title}
Company: {company_name}
Additional Information:
{add_info_str}

Write a professional email with the following requirements:
1. Create an appropriate subject line
2. Use a professional tone
3. Be concise but thorough
4. Include all necessary information
5. End with an appropriate call to action and signature

Output format:
Subject: [email subject]

[email body with signature]
"""
        
        # Generate email content
        response = self.model.generate(prompt, max_tokens=512, temperature=0.7)
        
        # Extract subject and body
        email_content = self._parse_email_content(response)
        
        return email_content
    
    def send_recruitment_email(self, email_type: str, recipient_email: str, 
                              recipient_name: str, job_title: str,
                              company_name: str = "Our Company", 
                              additional_info: Dict[str, Any] = None) -> bool:
        """
        Generate and send a recruitment email
        
        Args:
            email_type: Type of email to send
            recipient_email: Recipient's email address
            recipient_name: Recipient's name
            job_title: Job title
            company_name: Company name
            additional_info: Additional information for personalization
            
        Returns:
            Boolean indicating success
        """
        # Generate email content
        email_content = self.generate_email(
            email_type=email_type,
            recipient_name=recipient_name,
            job_title=job_title,
            company_name=company_name,
            additional_info=additional_info
        )
        
        # Send email (simulated or actual)
        success = send_email(
            to_email=recipient_email,
            subject=email_content["subject"],
            body=email_content["body"]
        )
        
        return success
    
    def _parse_email_content(self, text: str) -> Dict[str, str]:
        """
        Parse generated email text to extract subject and body
        
        Args:
            text: Generated email text
            
        Returns:
            Dictionary with 'subject' and 'body' keys
        """
        lines = text.strip().split("\n")
        subject = ""
        body = ""
        
        # Extract subject
        for i, line in enumerate(lines):
            if line.startswith("Subject:"):
                subject = line.replace("Subject:", "").strip()
                body = "\n".join(lines[i+1:]).strip()
                break
        
        # If no explicit subject found, find first line and use rest as body
        if not subject and lines:
            subject = lines[0].strip()
            body = "\n".join(lines[1:]).strip()
        
        return {
            "subject": subject,
            "body": body
        }