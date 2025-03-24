from typing import Dict, Any, List, Optional, Tuple
from models.llama_model import LlamaModel
import datetime

class InterviewAgent:
    """Agent for conducting interactive AI-driven interviews"""
    
    def __init__(self, llama_model: LlamaModel):
        """
        Initialize the Interview Agent
        
        Args:
            llama_model: Instance of the LlamaModel
        """
        self.model = llama_model
        self.context = ""
        self.conversation_history = []
        self.current_stage = "introduction"
        self.candidate_evaluation = {}
    
    def initialize_interview(self, job_title: str, candidate_name: str, 
                           job_description: str, interview_type: str = "technical",
                           interview_duration_minutes: int = 45) -> str:
        """
        Initialize a new interview session
        
        Args:
            job_title: Title of the job position
            candidate_name: Name of the candidate
            job_description: Description of the job
            interview_type: Type of interview (technical, behavioral, etc.)
            interview_duration_minutes: Expected duration of the interview
            
        Returns:
            Introduction message to start the interview
        """
        # Reset conversation state
        self.conversation_history = []
        self.candidate_evaluation = {}
        
        # Truncate job description if too long
        max_length = 1500
        job_desc_truncated = job_description[:max_length]
        
        # Create context for the interview
        self.context = f"""
Job Title: {job_title}
Candidate: {candidate_name}
Interview Type: {interview_type}
Interview Duration: {interview_duration_minutes} minutes

Job Description:
{job_desc_truncated}
"""
        
        # Set initial stage
        self.current_stage = "introduction"
        
        # Generate introduction
        prompt = f"""
You are an AI interviewer conducting a {interview_type} interview for a {job_title} position.

Interview Context:
{self.context}

Generate a professional and friendly introduction to start the interview. Include:
1. A greeting and introduction of yourself as the interviewer
2. A brief overview of the company and position
3. An explanation of how the interview will proceed
4. A friendly ice-breaker question to start the conversation

Keep it concise and engaging.
"""
        
        introduction = self.model.generate(prompt, max_tokens=512, temperature=0.7)
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "interviewer",
            "message": introduction
        })
        
        return introduction
    
    def generate_next_question(self, candidate_response: str = None) -> Tuple[str, bool]:
        """
        Generate the next interview question based on conversation history
        
        Args:
            candidate_response: Candidate's response to previous question
            
        Returns:
            Tuple of (question_text, is_interview_complete)
        """
        # If candidate provided a response, add it to history
        if candidate_response:
            self.conversation_history.append({
                "role": "candidate",
                "message": candidate_response
            })
        
        # Determine next stage based on current stage and conversation length
        self._update_interview_stage()
        
        # Check if interview should end
        if self.current_stage == "conclusion":
            return self._generate_conclusion(), True
        
        # Format conversation history
        history_text = self._format_conversation_history()
        
        # Create prompt for next question
        prompt = f"""
You are an AI interviewer conducting a professional job interview.

Interview Context:
{self.context}

Current Stage: {self.current_stage}

Conversation History:
{history_text}

Based on the conversation so far and the current stage, generate the next interview question.
The question should:
1. Flow naturally from the previous exchange
2. Be relevant to the {self.current_stage} stage
3. Dig deeper into the candidate's experience and skills
4. Adapt based on the candidate's previous answers
5. Be open-ended to encourage detailed responses

Output only the next question or comment to continue the interview. Be conversational and engaging.
"""
        
        next_question = self.model.generate(prompt, max_tokens=512, temperature=0.7)
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "interviewer",
            "message": next_question
        })
        
        return next_question, False
    
    def analyze_candidate_response(self, question: str, response: str) -> Dict[str, Any]:
        """
        Analyze a candidate's response to a specific question
        
        Args:
            question: The question asked
            response: The candidate's response
            
        Returns:
            Analysis of the response
        """
        prompt = f"""
You are an expert recruitment analyst evaluating a candidate's interview response.

Question: {question}

Candidate Response: {response}

Analyze the response and provide the following:
1. Relevance: How relevant was the response to the question (1-10)
2. Clarity: How clear and articulate was the response (1-10)
3. Depth: How in-depth and thorough was the response (1-10)
4. Key Insights: What are the key takeaways from this response
5. Red Flags: Any concerning aspects of the response
6. Overall Assessment: Brief overall assessment of this response

Keep your analysis objective and fair.
"""
        
        analysis = self.model.generate(prompt, max_tokens=512, temperature=0.3)
        
        # Store analysis in candidate evaluation
        if "responses" not in self.candidate_evaluation:
            self.candidate_evaluation["responses"] = []
        
        self.candidate_evaluation["responses"].append({
            "question": question,
            "response": response,
            "analysis": analysis
        })
        
        # Parse structured analysis
        # (In a real implementation, you would parse the values more robustly)
        analysis_dict = {
            "raw_analysis": analysis,
            "question": question,
            "response": response
        }
        
        return analysis_dict
    
    def _update_interview_stage(self) -> None:
        """Update the current stage of the interview based on progress"""
        # Count candidate responses
        response_count = sum(1 for msg in self.conversation_history if msg["role"] == "candidate")
        
        # Define stage transitions based on number of exchanges
        if response_count == 0:
            self.current_stage = "introduction"
        elif response_count < 3:
            self.current_stage = "background"
        elif response_count < 6:
            self.current_stage = "technical_skills"
        elif response_count < 9:
            self.current_stage = "behavioral"
        elif response_count < 11:
            self.current_stage = "candidate_questions"
        else:
            self.current_stage = "conclusion"
    
    def _generate_conclusion(self) -> str:
        """Generate conclusion for the interview"""
        # Format conversation history
        history_text = self._format_conversation_history()
        
        prompt = f"""
You are an AI interviewer concluding a job interview.

Interview Context:
{self.context}

Conversation History:
{history_text}

Generate a professional and friendly conclusion to the interview. Include:
1. A thank you for the candidate's time
2. A brief appreciation for their responses
3. Information about next steps in the process
4. An opportunity for any final questions
5. A professional sign-off

Keep it warm and professional.
"""
        
        conclusion = self.model.generate(prompt, max_tokens=512, temperature=0.7)
        
        return conclusion
    
    def _format_conversation_history(self) -> str:
        """Format conversation history for inclusion in prompts"""
        # Limit history if too long
        max_history = 10
        recent_history = self.conversation_history[-max_history:] if len(self.conversation_history) > max_history else self.conversation_history
        
        # Format history
        history_text = ""
        for entry in recent_history:
            role = "Interviewer" if entry["role"] == "interviewer" else "Candidate"
            history_text += f"{role}: {entry['message']}\n\n"
        
        return history_text
    
    def generate_interview_transcript(self) -> str:
        """
        Generate a formatted transcript of the entire interview
        
        Returns:
            Formatted interview transcript
        """
        transcript = f"Interview Transcript\n{'='*20}\n\n"
        job_title = self.context.split('Job Title:')[1].split('\n')[0].strip()
        transcript += f"Job Position: {job_title}\n"

        transcript += f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"

        for entry in self.conversation_history:
            role = "Interviewer" if entry["role"] == "interviewer" else "Candidate"
            transcript += f"{role}: {entry['message']}\n\n"

        return transcript