from llama_cpp import Llama

# Set the correct model path
model_path = r"C:/Users/210303105587/AI-Agent/models/llama-2-7b-chat.Q4_K_M.gguf"

# Load the LLaMA model
llm = Llama(model_path=model_path)

# Test prompt
prompt = "Hey"

# Generate response
response = llm(prompt)

# Print output
print(response["choices"][0]["text"])
