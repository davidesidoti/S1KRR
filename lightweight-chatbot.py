import os
import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

class LightweightChatbot:
    def __init__(self, model_name="TheBloke/TinyLlama-1.1B-Chat-v1.0-GPTQ"):
        """
        Initialize a lightweight chatbot model for testing.
        
        Args:
            model_name: Name or path of the model to use
        """
        self.model_name = model_name
        self.conversation_history = []
        
        print(f"Loading model: {model_name}")
        print("This might take a few minutes...")
        
        # Set up device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Configure model loading based on available hardware
        if self.device == "cuda":
            # GPU configuration
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
        else:
            # CPU configuration with memory optimization
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                low_cpu_mem_usage=True,
                torch_dtype=torch.float32
            )
        
        # Create generation pipeline
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=256,  # Reduced for better performance
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            device=0 if self.device == "cuda" else -1  # -1 for CPU
        )
        
        print("Model loaded successfully!")
    
    def format_prompt(self, message):
        """Format messages using the model's chat template."""
        messages = [
            {"role": "system", "content": "You are S1KRR, a fun and chaotic Discord bot that helps users with a touch of humor."}
        ] + self.conversation_history + [{"role": "user", "content": message}]
        
        return self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
    
    def chat(self, message):
        """Generate a response to the user message."""
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Format the prompt with conversation history
        prompt = self.format_prompt(message)
        
        # Generate response
        response = self.pipe(prompt)[0]["generated_text"]
        
        # Extract just the assistant's response from the output
        try:
            # Replace the response splitting with:
            assistant_response = response[len(prompt):].strip()
        except:
            # Fallback if the splitting doesn't work
            assistant_response = response.replace(prompt, "").strip()
        
        # Add to conversation history
        self.conversation_history.append({"role": "assistant", "content": assistant_response})
        
        return assistant_response
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
        return "Conversation history has been reset."


def main():
    """Main function to run the terminal chatbot."""
    print("Welcome to the S1KRR Lightweight Terminal Chatbot!")
    
    # Try to initialize with different models in order of preference
    models_to_try = [
        "microsoft/phi-2",                          # Small but capable model
        "TheBloke/TinyLlama-1.1B-Chat-v1.0-GPTQ",  # Very small model (1.1B)
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0",      # Alternative format
        "Qwen/Qwen2-1.5B-Instruct",
    ]
    
    chatbot = None
    for model in models_to_try:
        try:
            print(f"Attempting to load model: {model}")
            chatbot = LightweightChatbot(model)
            break  # Successfully loaded a model
        except Exception as e:
            print(f"Failed to load {model}: {str(e)}")
            print("Trying another model...\n")
    
    if chatbot is None:
        print("Error: Could not initialize any model. Please check your system resources.")
        sys.exit(1)
    
    print("\nS1KRR is ready! Type 'exit' to quit or 'reset' to clear the conversation history.")
    
    # Main chat loop
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        elif user_input.lower() == "reset":
            print(chatbot.reset_conversation())
            continue
        elif not user_input:
            continue
        
        try:
            # Get response from the model
            response = chatbot.chat(user_input)
            print(f"\nS1KRR: {response}")
        except Exception as e:
            print(f"Error generating response: {e}")
            print("Try asking a simpler question or reset the conversation.")


if __name__ == "__main__":
    main()