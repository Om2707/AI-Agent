import os
from typing import Dict, Any, List, Optional
from llama_cpp import Llama

class LlamaModel:
    """Wrapper for Llama 3.x model integration"""
    
    def __init__(self, model_path: str, context_size: int = 4096, n_gpu_layers: int = -1):
        """
        Initialize the Llama model
        
        Args:
            model_path: Path to the Llama model file
            context_size: Maximum context size
            n_gpu_layers: Number of layers to offload to GPU (-1 for all)
        """
        self.model = Llama(
            model_path=model_path,
            n_ctx=context_size,
            n_gpu_layers=n_gpu_layers
        )
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7, 
                 top_p: float = 0.95, stop: Optional[List[str]] = None) -> str:
        """
        Generate text using the Llama model
        
        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            stop: List of strings to stop generation
            
        Returns:
            Generated text
        """
        response = self.model.create_completion(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=stop
        )
        
        return response["choices"][0]["text"]
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        return self.model.embed(text)
    
    def similarity_score(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts based on embeddings
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        # Get embeddings
        embedding1 = self.get_embedding(text1)
        embedding2 = self.get_embedding(text2)
        
        # Calculate cosine similarity
        return self._cosine_similarity(embedding1, embedding2)
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        """
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 * magnitude2 == 0:
            return 0
            
        return dot_product / (magnitude1 * magnitude2)