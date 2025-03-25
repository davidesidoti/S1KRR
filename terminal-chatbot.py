import os
import sys
from sglang.spine.serving import ServingEngine
from sglang.spine.turbo import TurboPrompt

class DeepSeekChatbot:
    def __init__(self, model_path=None):
        """
        Initialize the DeepSeek-V3 chatbot.
        
        Args:
            model_path: Path to the DeepSeek-V3 model. If None, the model will be 
                       downloaded from Hugging Face.
        """
        self.model_path = model_path or "deepseek-ai/DeepSeek-V3"
        
        # Initialize the model
        print(f"Initializing DeepSeek-V3 model from {self.model_path}...")
        print("This may take a few minutes depending on your hardware.")
        
        # Create serving engine with DeepSeek-V3
        self.engine = ServingEngine(
            model=self.model_path,
            tp_size=1,  # Adjust based on your GPU count
            max_tokens=4096,
            dtype="fp8",  # Can be "bf16" if fp8 doesn't work
            gpu_memory_utilization=0.9
        )
        
        print("Model initialized successfully!")
        self.conversation_history = []
        
    def chat(self, message):
        """
        Generate a response for the given message while maintaining conversation history.
        
        Args:
            message: User input message
            
        Returns:
            Model's response
        """
        # Add the user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Format the conversation for DeepSeek-V3
        conversation = []
        for msg in self.conversation_history:
            conversation.append({"role": msg["role"], "content": msg["content"]})
        
        # Create a TurboPrompt with the conversation
        prompt = TurboPrompt(
            "deepseek-v3",
            messages=conversation,
            temperature=0.7,
            max_tokens=1024
        )
        
        # Generate the response
        output = self.engine.generate(prompt)
        response = output.text
        
        # Add the model's response to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
        return "Conversation history has been reset."


def main():
    """Main function to run the terminal chatbot."""
    print("Welcome to the DeepSeek-V3 Terminal Chatbot!")
    print("Loading model, please wait...")
    
    # Initialize the chatbot
    try:
        chatbot = DeepSeekChatbot()
    except Exception as e:
        print(f"Error initializing the model: {e}")
        sys.exit(1)
    
    print("\nDeepSeek-V3 Chatbot is ready! Type 'exit' to quit or 'reset' to clear conversation history.")
    
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
            print(f"\nDeepSeek-V3: {response}")
        except Exception as e:
            print(f"Error generating response: {e}")


if __name__ == "__main__":
    main()
