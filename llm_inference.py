# src/llm_inference.py
# Lightweight script using Microsoft Phi-3-mini-4k-instruct (3.8B, fast local inference)

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Fast, small, powerful open model (no gate, ~7GB download)
MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"

print(f"Loading model: {MODEL_ID}")
print("First time: ~7-8 GB download + quick load. Much faster than 7B models!")

try:
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

    # Load model with optimizations
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16,      # Saves memory
        device_map="auto",              # GPU if available, else CPU
        trust_remote_code=True,         # Required for Phi-3
    )

    # Generation pipeline
    generator = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=512,
        temperature=0.8,
        do_sample=True,
        repetition_penalty=1.15,
        top_p=0.95,
    )

    print("Model loaded successfully!\n")

    def generate_response(prompt: str) -> str:
        """Generate response with Phi-3 chat format"""
        # Phi-3 uses specific chat template
        messages = [{"role": "user", "content": prompt}]
        formatted = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        
        sequences = generator(formatted)
        return sequences[0]["generated_text"]

    # Interactive test
    if __name__ == "__main__":
        print("Model ready! Test with red team prompts (type 'quit' to exit)\n")
        while True:
            user_prompt = input("Your prompt: ")
            if user_prompt.lower() in ["quit", "exit"]:
                break
            
            print("\nGenerating...")
            response = generate_response(user_prompt)
            # Clean output
            response = response.split("<|assistant|>")[-1].strip() if "<|assistant|>" in response else response
            print(f"\nResponse: {response}\n")

except Exception as e:
    print(f"Error: {e}")
    print("\nTips:")
    print("- Install trust_remote_code if needed: already in code")
    print("- For even lower memory: We'll add 4-bit later if needed")
