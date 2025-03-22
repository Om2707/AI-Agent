from typing import Dict, Any, List, Optional
import os
import json
import re

class PDFParser:
    """
    Utility for parsing PDF resumes and job descriptions.
    In a real implementation, this would use libraries like PyPDF2, pdfminer, or pdfplumber.
    For the demo, we'll simulate parsing by reading from text files.
    """
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """
        Extract text content from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        # In a real implementation, this would use a PDF library
        # For the demo, we'll check if there's a text version with the same name
        text_path = pdf_path.replace('.pdf', '.txt')
        
        if os.path.exists(text_path):
            with open(text_path, 'r', encoding='utf-8') as file:
                return file.read()
        else:
            # If no text version exists, return a placeholder
            filename = os.path.basename(pdf_path)
            return f"[Simulated content for {filename}]"
    
    @staticmethod
    def parse_resume(pdf_path: str) -> Dict[str, Any]:
        """
        Parse a resume PDF into structured data
        
        Args:
            pdf_path: Path to the resume PDF
            
        Returns:
            Dictionary with structured resume data
        """
        # Extract text content
        text_content = PDFParser.extract_text_from_pdf(pdf_path)
        
        # In a real implementation, this would use NLP and regex to extract structured data
        # For the demo, we'll look for JSON with the same filename
        json_path = pdf_path.replace('.pdf', '.json')
        
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        
        # If no JSON exists, perform basic parsing with regex
        # This is a simplified simulation for demo purposes
        candidate_name = re.search(r'Name:?\s*([\w\s]+)', text_content)
        email = re.search(r'Email:?\s*([\w\.-]+@[\w\.-]+)', text_content)
        phone = re.search(r'Phone:?\s*(\+?\d[\d\s-]+)', text_content)
        
        skills_section = re.search(r'Skills:?\s*(.+?)(?:\n\n|\Z)', text_content, re.DOTALL)
        education_section = re.search(r'Education:?\s*(.+?)(?:\n\n|\Z)', text_content, re.DOTALL)
        experience_section = re.search(r'Experience:?\s*(.+?)(?:\n\n|\Z)', text_content, re.DOTALL)
        
        # Extract skills as a list
        skills = []
        if skills_section:
            skills_text = skills_section.group(1)
            # Split by commas, bullets, or newlines
            skills = [s.strip() for s in re.split(r'[,•\n]', skills_text) if s.strip()]
        
        return {
            "candidate_name": candidate_name.group(1) if candidate_name else "Unknown",
            "email": email.group(1) if email else "",
            "phone": phone.group(1) if phone else "",
            "raw_text": text_content,
            "skills": skills,
            "education": education_section.group(1).strip() if education_section else "",
            "experience": experience_section.group(1).strip() if experience_section else "",
            "filename": os.path.basename(pdf_path)
        }
    
    @staticmethod
    def parse_job_description(pdf_path: str) -> Dict[str, Any]:
        """
        Parse a job description PDF into structured data
        
        Args:
            pdf_path: Path to the job description PDF
            
        Returns:
            Dictionary with structured job description data
        """
        # Extract text content
        text_content = PDFParser.extract_text_from_pdf(pdf_path)
        
        # Check for JSON with the same filename
        json_path = pdf_path.replace('.pdf', '.json')
        
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        
        # If no JSON exists, perform basic parsing with regex
        job_title = re.search(r'Job Title:?\s*([\w\s]+)', text_content)
        department = re.search(r'Department:?\s*([\w\s]+)', text_content)
        location = re.search(r'Location:?\s*([\w\s,]+)', text_content)
        
        requirements_section = re.search(r'Requirements:?\s*(.+?)(?:\n\n|\Z)', text_content, re.DOTALL)
        responsibilities_section = re.search(r'Responsibilities:?\s*(.+?)(?:\n\n|\Z)', text_content, re.DOTALL)
        
        # Extract requirements as a list
        requirements = []
        if requirements_section:
            req_text = requirements_section.group(1)
            # Split by bullets or newlines
            requirements = [r.strip() for r in re.split(r'[•\n]', req_text) if r.strip()]
        
        # Extract responsibilities as a list
        responsibilities = []
        if responsibilities_section:
            resp_text = responsibilities_section.group(1)
            # Split by bullets or newlines
            responsibilities = [r.strip() for r in re.split(r'[•\n]', resp_text) if r.strip()]
        
        return {
            "job_title": job_title.group(1) if job_title else "Unknown",
            "department": department.group(1) if department else "",
            "location": location.group(1) if location else "",
            "raw_text": text_content,
            "requirements": requirements,
            "responsibilities": responsibilities,
            "filename": os.path.basename(pdf_path)
        }
    
    @staticmethod
    def batch_parse_resumes(directory_path: str) -> List[Dict[str, Any]]:
        """
        Parse all resume PDFs in a directory
        
        Args:
            directory_path: Path to directory containing resume PDFs
            
        Returns:
            List of parsed resume dictionaries
        """
        parsed_resumes = []
        
        if not os.path.exists(directory_path):
            return parsed_resumes
        
        for filename in os.listdir(directory_path):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(directory_path, filename)
                parsed_resume = PDFParser.parse_resume(file_path)
                parsed_resumes.append(parsed_resume)
        
        return parsed_resumes
    
    @staticmethod
    def batch_parse_job_descriptions(directory_path: str) -> List[Dict[str, Any]]:
        """
        Parse all job description PDFs in a directory
        
        Args:
            directory_path: Path to directory containing job description PDFs
            
        Returns:
            List of parsed job description dictionaries
        """
        parsed_jds = []
        
        if not os.path.exists(directory_path):
            return parsed_jds
        
        for filename in os.listdir(directory_path):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(directory_path, filename)
                parsed_jd = PDFParser.parse_job_description(file_path)
                parsed_jds.append(parsed_jd)
        
        return parsed_jds