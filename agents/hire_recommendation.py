from typing import Dict, Any, List, Optional
from models.llama_model import LlamaModel

class HireRecommendationAgent:
    """Agent for analyzing interviews and making hiring recommendations"""
    
    def __init__(self, llama_model: LlamaModel):
        """
        Initialize the Hire Recommendation Agent
        
        Args:
            llama_model: Instance of the LlamaModel
        """
        self.model = llama_model
    
    def analyze_interview(self, job_description: str, interview_transcript: str, 
                        resume: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze interview transcript and provide hiring recommendation
        
        Args:
            job_description: Description of the job
            interview_transcript: Full interview transcript
            resume: Candidate's resume (optional)
            
        Returns:
            Dictionary with analysis and recommendation
        """
        # Truncate inputs if they're too long
        max_length = 2000
        job_desc_truncated = job_description[:max_length]
        interview_truncated = interview_transcript[:max_length]
        resume_truncated = resume[:max_length] if resume else ""
        
        # Create context string
        context = f"""
Job Description:
{job_desc_truncated}

"""
        if resume:
            context += f"""
Candidate Resume:
{resume_truncated}

"""
        
        context += f"""
Interview Transcript:
{interview_truncated}
"""
        
        # Create prompt for Llama
        prompt = f"""
You are an expert hiring consultant analyzing an interview transcript to make a hiring recommendation.

{context}

Based on the provided information, conduct a thorough analysis and provide:

1. Candidate Strengths: Identify 3-5 key strengths demonstrated during the interview, with specific examples
2. Areas of Concern: Identify 3-5 potential weaknesses or areas for improvement, with specific examples
3. Technical Competency: Evaluate the candidate's technical skills relevant to the position (Scale: 1-10)
4. Cultural Fit: Assess how well the candidate would fit within the company culture (Scale: 1-10)
5. Communication Skills: Evaluate the candidate's communication abilities (Scale: 1-10)
6. Overall Recommendation: Provide a clear HIRE or NO-HIRE recommendation with justification
7. Development Areas: If hired, what areas should the candidate focus on developing

Format your analysis as a structured report with clear sections and specific examples from the interview.
"""
        
        # Generate recommendation
        recommendation = self.model.generate(prompt, max_tokens=1024, temperature=0.3)
        
        # Extract the hire/no-hire decision
        decision = self._extract_hire_decision(recommendation)
        
        return {
            "detailed_analysis": recommendation,
            "recommendation": decision,
            "job_description": job_description[:100] + "..." if len(job_description) > 100 else job_description
        }
    
    def compare_candidates(self, job_description: str, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple candidates and rank them
        
        Args:
            job_description: Description of the job
            candidates: List of candidate dictionaries with 'name', 'recommendation', and 'detailed_analysis'
            
        Returns:
            Comparison analysis and ranking
        """
        # Create candidate summaries
        candidates_text = ""
        for i, candidate in enumerate(candidates, 1):
            candidates_text += f"""
Candidate {i}: {candidate['name']}
Recommendation: {candidate['recommendation']}
Analysis Summary: {candidate['detailed_analysis'][:300]}...

"""
        
        # Create prompt for Llama
        prompt = f"""
You are an expert hiring consultant comparing multiple candidates for a position.

Job Description:
{job_description[:1000]}

Candidate Information:
{candidates_text}

Compare these candidates and provide:
1. A comparative analysis of their strengths and weaknesses
2. A ranking of the candidates from most to least suitable
3. Justification for the ranking
4. Final recommendation on which candidate(s) to hire

Format your response as a structured report with clear sections and specific justifications.
"""
        
        # Generate comparison
        comparison = self.model.generate(prompt, max_tokens=1024, temperature=0.3)
        
        # Extract rankings (in a real implementation, parse this more robustly)
        ranking = [c["name"] for c in candidates]  # Default to input order
        
        return {
            "comparison": comparison,
            "ranking": ranking,
            "job_description": job_description[:100] + "..." if len(job_description) > 100 else job_description
        }
    
    def _extract_hire_decision(self, analysis: str) -> str:
        """
        Extract hire/no-hire decision from analysis text
        
        Args:
            analysis: Generated analysis text
            
        Returns:
            "HIRE" or "NO-HIRE" decision
        """
        analysis_lower = analysis.lower()
        
        # Look for recommendation section
        if "recommendation" in analysis_lower:
            # Check for hire indicators
            if ("hire: yes" in analysis_lower or 
                "recommendation: hire" in analysis_lower or 
                "decision: hire" in analysis_lower):
                return "HIRE"
            
            # Check for no-hire indicators
            if ("hire: no" in analysis_lower or 
                "recommendation: no" in analysis_lower or 
                "decision: no" in analysis_lower or
                "do not hire" in analysis_lower or
                "no-hire" in analysis_lower):
                return "NO-HIRE"
        
        # If unclear, make a best guess based on overall text
        hire_indicators = ["excellent", "outstanding", "strong", "impressive", "recommend"]
        no_hire_indicators = ["concerns", "insufficient", "weak", "poor", "not recommend"]
        
        hire_count = sum(1 for word in hire_indicators if word in analysis_lower)
        no_hire_count = sum(1 for word in no_hire_indicators if word in analysis_lower)
        
        # Default to more conservative NO-HIRE if unclear
        return "HIRE" if hire_count > no_hire_count else "NO-HIRE"