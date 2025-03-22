from typing import Dict, Any, List, Optional
from models.llama_model import LlamaModel

class SentimentAnalyzer:
    """Agent for analyzing sentiment in interview recordings/transcripts"""
    
    def __init__(self, llama_model: LlamaModel):
        """
        Initialize the Sentiment Analyzer
        
        Args:
            llama_model: Instance of the LlamaModel
        """
        self.model = llama_model
    
    def analyze_sentiment(self, transcript: str, speaker_labels: bool = True) -> Dict[str, Any]:
        """
        Analyze sentiment in interview transcript
        
        Args:
            transcript: Interview transcript text
            speaker_labels: Whether transcript has speaker labels
            
        Returns:
            Dictionary with sentiment analysis results
        """
        # Truncate transcript if too long
        max_length = 4000
        transcript_truncated = transcript[:max_length]
        
        # Create prompt for Llama
        prompt = f"""
You are an expert in analyzing emotional tone, confidence, and sentiment in interview transcripts.

Interview Transcript:
{transcript_truncated}

Perform a detailed sentiment analysis of this interview transcript. Your analysis should include:

1. Overall Candidate Sentiment: Positive, Neutral, or Negative
2. Confidence Level: Rate from 1-10 with specific examples
3. Emotional Indicators: Identify specific emotions (enthusiasm, nervousness, etc.) with examples
4. Language Patterns: Analyze use of assertive vs. tentative language
5. Key Moments: Identify turning points or significant emotional shifts
6. Speaker Dynamics: Analyze interaction patterns if multiple speakers

For each aspect, provide specific examples from the transcript to support your analysis.
Format your response as a structured report with relevant sections and quotations.
"""
        
        # Generate sentiment analysis
        analysis = self.model.generate(prompt, max_tokens=1024, temperature=0.4)
        
        # Extract structured data 
        sentiment_score = self._extract_sentiment_score(analysis)
        confidence_score = self._extract_confidence_score(analysis)
        
        return {
            "detailed_analysis": analysis,
            "sentiment_score": sentiment_score,
            "confidence_score": confidence_score,
            "transcript_length": len(transcript)
        }
    
    def analyze_sentiment_by_topic(self, transcript: str, topics: List[str]) -> Dict[str, Any]:
        """
        Analyze sentiment for specific topics in the transcript
        
        Args:
            transcript: Interview transcript text
            topics: List of topics to analyze sentiment for
            
        Returns:
            Dictionary with topic-based sentiment analysis
        """
        # Truncate transcript if too long
        max_length = 4000
        transcript_truncated = transcript[:max_length]
        
        # Format topics
        topics_str = "\n".join([f"- {topic}" for topic in topics])
        
        # Create prompt for Llama
        prompt = f"""
You are an expert in analyzing emotional tone, confidence, and sentiment in interview transcripts.

Interview Transcript:
{transcript_truncated}

Focus your analysis on the following specific topics:
{topics_str}

For each topic, provide:
1. Sentiment (Positive, Neutral, or Negative)
2. Confidence Level (1-10)
3. Specific examples from the transcript
4. Emotional indicators when discussing this topic

Format your analysis by topic, with clear headings and examples for each.
"""
        
        # Generate topic-based sentiment analysis
        analysis = self.model.generate(prompt, max_tokens=1024, temperature=0.4)
        
        # Structure results by topic (in a real implementation, parse this more robustly)
        topic_results = {}
        for topic in topics:
            topic_results[topic] = {
                "sentiment": "Neutral",  # Default
                "confidence": 5,  # Default
                "examples": []
            }
        
        return {
            "detailed_analysis": analysis,
            "topic_results": topic_results,
            "transcript_length": len(transcript)
        }
    
    def analyze_interview_progression(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze how sentiment changes throughout the interview
        
        Args:
            transcript: Interview transcript text
            
        Returns:
            Dictionary with sentiment progression analysis
        """
        # Truncate transcript if too long
        max_length = 4000
        transcript_truncated = transcript[:max_length]
        
        # Create prompt for Llama
        prompt = f"""
You are an expert in analyzing emotional progression and sentiment changes throughout interviews.

Interview Transcript:
{transcript_truncated}

Analyze how the candidate's sentiment, confidence, and emotional state change throughout the interview.

Your analysis should include:
1. Beginning Phase: Sentiment and confidence in first 25% of interview
2. Middle Phase: Sentiment and confidence in middle 50% of interview
3. Ending Phase: Sentiment and confidence in final 25% of interview
4. Key Turning Points: Identify specific moments where sentiment shifted
5. Overall Progression: Did confidence increase, decrease, or fluctuate?
6. Topic Correlation: Did certain topics trigger sentiment changes?

For each phase and turning point, provide specific examples from the transcript.
Format your response as a structured analysis with clear sections and evidence.
"""
        
        # Generate progression analysis
        analysis = self.model.generate(prompt, max_tokens=1024, temperature=0.4)
        
        # Extract progression data (simplified)
        phases = {
            "beginning": {"sentiment": "Neutral", "confidence": 5},
            "middle": {"sentiment": "Neutral", "confidence": 5},
            "ending": {"sentiment": "Neutral", "confidence": 5}
        }
        
        return {
            "detailed_analysis": analysis,
            "phases": phases,
            "transcript_length": len(transcript)
        }
    
    def _extract_sentiment_score(self, analysis: str) -> str:
        """
        Extract overall sentiment from analysis text
        
        Args:
            analysis: Generated analysis text
            
        Returns:
            "Positive", "Neutral", or "Negative"
        """
        analysis_lower = analysis.lower()
        
        # Check for explicit sentiment indicators
        if "sentiment: positive" in analysis_lower or "overall sentiment: positive" in analysis_lower:
            return "Positive"
        elif "sentiment: negative" in analysis_lower or "overall sentiment: negative" in analysis_lower:
            return "Negative"
        elif "sentiment: neutral" in analysis_lower or "overall sentiment: neutral" in analysis_lower:
            return "Neutral"
        
        # Count sentiment words
        positive_words = ["positive", "enthusiastic", "confident", "excited", "interested", "engaged"]
        negative_words = ["negative", "nervous", "anxious", "hesitant", "uncomfortable", "uncertain"]
        
        positive_count = sum(1 for word in positive_words if word in analysis_lower)
        negative_count = sum(1 for word in negative_words if word in analysis_lower)
        
        # Determine sentiment based on word count
        if positive_count > negative_count:
            return "Positive"
        elif negative_count > positive_count:
            return "Negative"
        else:
            return "Neutral"
    
    def _extract_confidence_score(self, analysis: str) -> int:
        """
        Extract confidence score from analysis text
        
        Args:
            analysis: Generated analysis text
            
        Returns:
            Confidence score from 1-10
        """
        analysis_lower = analysis.lower()
        
        # Look for explicit confidence scores
        import re
        confidence_patterns = [
            r"confidence[:\s]+(\d+)/10",
            r"confidence[:\s]+(\d+) out of 10",
            r"confidence level[:\s]+(\d+)",
            r"confidence score[:\s]+(\d+)"
        ]
        
        for pattern in confidence_patterns:
            matches = re.findall(pattern, analysis_lower)
            if matches:
                try:
                    score = int(matches[0])
                    return min(10, max(1, score))  # Ensure score is between 1-10
                except ValueError:
                    pass
        
        # If no explicit score, estimate from language
        high_confidence_words = ["confident", "assertive", "strong", "assured", "definitive"]
        low_confidence_words = ["uncertain", "hesitant", "tentative", "unsure", "doubtful"]
        
        high_count = sum(1 for word in high_confidence_words if word in analysis_lower)
        low_count = sum(1 for word in low_confidence_words if word in analysis_lower)
        
        # Calculate score
        if high_count > low_count:
            return 7 + min(3, high_count - low_count)  # 7-10 range
        elif low_count > high_count:
            return 4 - min(3, low_count - high_count)  # 1-4 range
        else:
            return 5  # Neutral confidence