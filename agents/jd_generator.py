from typing import Dict, Any, List
from models.llama_model import LlamaModel

class JDGenerator:
    """Agent for generating job descriptions"""
    
    def __init__(self, llama_model: LlamaModel):
        """
        Initialize the JD Generator
        
        Args:
            llama_model: Instance of the LlamaModel
        """
        self.model = llama_model
    
    def generate_job_description(self, title: str, skills: List[str], 
                                experience_level: str, 
                                additional_info: Dict[str, Any] = None) -> str:
        """
        Generate a job description based on provided information
        
        Args:
            title: Job title
            skills: List of required skills
            experience_level: Required experience level (e.g., "Entry-level", "Mid-level", "Senior")
            additional_info: Additional information (company, location, etc.)
            
        Returns:
            Generated job description
        """
        # Format skills as a comma-separated list
        skills_str = ", ".join(skills)
        
        # Prepare additional info
        add_info_str = ""
        if additional_info:
            for key, value in additional_info.items():
                add_info_str += f"{key.capitalize()}: {value}\n"
        
        # Create prompt for Llama
        prompt = f"""
You are an expert recruitment specialist tasked with creating a professional, detailed job description.

Job Details:
- Title: {title}
- Required Skills: {skills_str}
- Experience Level: {experience_level}
{add_info_str}

Generate a comprehensive job description with the following sections:
1. Company Overview (create a fictional tech company if not specified)
2. Role Overview
3. Key Responsibilities
4. Required Qualifications
5. Preferred Qualifications
6. Benefits and Perks

Format the job description professionally with appropriate headings. 
Make it informative yet concise, focusing on clarity and relevance.
"""
        
        # Generate job description
        response = self.model.generate(prompt, max_tokens=1024, temperature=0.7)
        
        return response
    
    def refine_job_description(self, job_description: str, feedback: str) -> str:
        """
        Refine an existing job description based on feedback
        
        Args:
            job_description: Existing job description
            feedback: Feedback to incorporate
            
        Returns:
            Refined job description
        """
        prompt = f"""
You are an expert recruitment specialist tasked with refining a job description based on specific feedback.

Original Job Description:
{job_description}

Feedback to Address:
{feedback}

Please produce an improved version of the job description that addresses all the feedback points while maintaining a professional tone and comprehensive coverage of all required sections.
"""
        
        # Generate refined job description
        response = self.model.generate(prompt, max_tokens=1024, temperature=0.7)
        
        return response