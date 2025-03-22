from typing import List, Dict, Any, Optional
import uuid
import json
from datetime import datetime

class EmailSender:
    """
    Simulated email sending utility for the recruitment system.
    In a production environment, this would integrate with actual email services.
    """
    
    def __init__(self, sender_email: str = "recruitment@company.com", sender_name: str = "Recruitment Team"):
        """
        Initialize the email sender
        
        Args:
            sender_email: Default sender email address
            sender_name: Default sender name
        """
        self.sender_email = sender_email
        self.sender_name = sender_name
        self.email_history = []  # Stores sent email records for demo purposes
    
    def send_email(self, recipient_email: str, subject: str, body: str, 
                  recipient_name: Optional[str] = None, 
                  attachments: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Send an email (simulated)
        
        Args:
            recipient_email: Recipient's email address
            subject: Email subject line
            body: Email body content (HTML supported)
            recipient_name: Recipient's name (optional)
            attachments: List of attachment objects (optional)
            
        Returns:
            Email ID for tracking
        """
        email_id = str(uuid.uuid4())
        
        email_record = {
            "id": email_id,
            "sender": {
                "name": self.sender_name,
                "email": self.sender_email
            },
            "recipient": {
                "name": recipient_name or recipient_email.split('@')[0],
                "email": recipient_email
            },
            "subject": subject,
            "body": body,
            "attachments": attachments or [],
            "timestamp": datetime.now().isoformat(),
            "status": "sent"
        }
        
        # Store the email record
        self.email_history.append(email_record)
        
        # In a real implementation, this would use an email service API
        print(f"Email sent to {recipient_email}:")
        print(f"Subject: {subject}")
        print(f"Email ID: {email_id}")
        
        return email_id
    
    def send_bulk_email(self, recipients: List[Dict[str, str]], subject: str, 
                       body_template: str, personalize: bool = True) -> List[str]:
        """
        Send bulk emails with optional personalization
        
        Args:
            recipients: List of recipient dictionaries with 'email' and 'name' keys
            subject: Email subject line
            body_template: Email body template with placeholders for personalization
            personalize: Whether to personalize emails
            
        Returns:
            List of sent email IDs
        """
        email_ids = []
        
        for recipient in recipients:
            email = recipient.get("email")
            name = recipient.get("name", email.split('@')[0])
            
            if personalize:
                # Replace placeholders in template
                personalized_body = body_template.replace("{name}", name)
                personalized_subject = subject.replace("{name}", name)
            else:
                personalized_body = body_template
                personalized_subject = subject
            
            # Send the personalized email
            email_id = self.send_email(
                recipient_email=email,
                recipient_name=name,
                subject=personalized_subject,
                body=personalized_body
            )
            
            email_ids.append(email_id)
        
        return email_ids
    
    def get_email_status(self, email_id: str) -> Dict[str, Any]:
        """
        Get the status of a sent email
        
        Args:
            email_id: ID of the email to check
            
        Returns:
            Email status information
        """
        # In a real implementation, this would query the email service API
        for email in self.email_history:
            if email["id"] == email_id:
                return {
                    "id": email_id,
                    "status": email["status"],
                    "recipient": email["recipient"]["email"],
                    "sent_at": email["timestamp"]
                }
        
        return {"id": email_id, "status": "not_found"}
    
    def get_email_history(self, recipient_email: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get email sending history, optionally filtered by recipient
        
        Args:
            recipient_email: Filter by recipient email address
            
        Returns:
            List of email records
        """
        if recipient_email:
            return [email for email in self.email_history 
                   if email["recipient"]["email"] == recipient_email]
        return self.email_history