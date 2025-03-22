import os
from typing import Dict, Any, List, Tuple
from models.llama_model import LlamaModel
from utils.pdf_parser import extract_text_from_pdf

class ResumeRanker:
    """Agent for ranking resumes against a job description"""
    
    def __init__(self, llama_model: LlamaModel):
        """
        Initialize the Resume Ranker
        
        Args:
            llama_model: Instance of the LlamaModel
        """
        self.model = llama_model
    
    def rank_resumes(self, job_description: str, resume_paths: List[str], 
                     detailed_analysis: bool = False) -> List[Dict[str, Any]]:
        """
        Rank multiple resumes against a job description
        
        Args:
            job_description: The job description text
            resume_paths: List of paths to resume files
            detailed_analysis: Whether to include detailed analysis
            
        Returns:
            List of ranked resumes with scores and analysis
        """
        results = []
        
        for resume_path in resume_paths:
            # Extract text from resume
            resume_text = extract_text_from_pdf(resume_path)
            filename = os.path.basename(resume_path)
            
            # Get match score and analysis
            score, analysis = self._analyze_resume_match(job_description, resume_text, detailed_analysis)
            
            results.append({
                "filename": filename,
                "path": resume_path,
                "score": score,
                "analysis": analysis
            })
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results
    
    def _analyze_resume_match(self, job_description: str, resume_text: str, 
                             detailed: bool = False) -> Tuple[float, str]:
        """
        Analyze how well a resume matches a job description
        
        Args:
            job_description: The job description text
            resume_text: The resume text
            detailed: Whether to include detailed analysis
            
        Returns:
            Tuple of (score, analysis)
        """
        # Truncate texts if they're too long to fit in context
        max_length = 1500  # Approximate max length to fit in context with prompt
        job_desc_truncated = job_description[:max_length]
        resume_truncated = resume_text[:max_length]
        
        # Create prompt for Llama
        prompt = f"""
You are an expert AI recruitment assistant tasked with evaluating how well a candidate's resume matches a job description.

Job Description:
{job_desc_truncated}

Resume:
{resume_truncated}

Your task:
1. Identify key skills, experience, and qualifications from the job description
2. Evaluate how well the resume matches these requirements
3. Assign a match score from 0 to 100, where:
   - 0-20: Poor match, missing most key requirements
   - 21-40: Below average match, missing many key requirements
   - 41-60: Average match, meets some key requirements
   - 61-80: Good match, meets most key requirements
   - 81-100: Excellent match, meets all or nearly all key requirements
{"4. Provide a detailed analysis of strengths and weaknesses" if detailed else ""}

Output format:
Score: [numerical score between 0-100]
{"Analysis: [your detailed analysis]" if detailed else ""}
"""
        
        # Generate analysis
        response = self.model.generate(prompt, max_tokens=512, temperature=0.3)
        
        # Extract score from response
        score = self._extract_score(response)
        
        return score, response
    
    def _extract_score(self, text: str) -> float:
        """
        Extract numerical score from text response
        
        Args:
            text: Response text containing score
            
        Returns:
            Extracted score as float
        """
        try:
            # Look for "Score: X" pattern
            if "Score:" in text:
                score_line = [line for line in text.split("\n") if "Score:" in line][0]
                score_str = score_line.split("Score:")[1].strip().split()[0]
                score = float(score_str)
                return min(100, max(0, score))  # Ensure score is between 0-100
            
            # Fallback: look for any number between 0-100
            import re
            numbers = re.findall(r'\b\d+\b', text)
            for num in numbers:
                if 0 <= int(num) <= 100:
                    return float(num)
            
            # If no score found, return default
            return 50.0
        except Exception:
            # If parsing fails, return default
            return 50.0