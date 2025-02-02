# utils/huggingface_client.py
import requests
import json
import re

HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/google/gemma-2-2b-it"

def format_prompt(system_msg, history, current_char):
    prompt = f"""<start_of_turn>system
{system_msg}
<end_of_turn>
"""
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        content = msg["content"].replace("<end_of_turn>", "")
        prompt += f"<start_of_turn>{role}\n{content}<end_of_turn>\n"
    prompt += "<start_of_turn>model\n"
    return prompt

def generate_response(api_key: str, system_message: str, conversation_history: list, character: str):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # Character-specific adjustments
    if "Magic Dragon" in character:
        system_message += "\nInclude a short story (1-2 sentences) in your explanation"
    elif "Super Coder" in character:
        system_message += "\nAlways ask follow-up questions and wait for user answers"
    
    prompt = format_prompt(system_message, conversation_history, character)
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 256,
            "temperature": 0.7,
            "top_p": 0.9,
            "repetition_penalty": 1.2
        }
    }
    
    response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    
    result = json.loads(response.content.decode("utf-8"))
    full_response = result[0]['generated_text']
    
    response_text = full_response.split("<start_of_turn>model\n")[-1]
    clean_response = response_text.split("<end_of_turn>")[0].strip()
    
    concept = re.findall(r'teaching (?:about )?(.*?)[\.\n]', clean_response, re.IGNORECASE)
    if concept:
        clean_response += f"\n\nCurrent concept: {concept[0].title()}"
    
    return clean_response

def generate_practice(api_key: str, concept: str, character: str):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # Adjust the prompt to be beginner friendly if the concept mentions "variable"
    beginner_note = ""
    if "variable" in concept.lower():
        beginner_note = "Make sure the question is extremely beginner-friendly. For example, ask: 'Create a variable named my_name and store your name in it.'"
    
    prompt = f"""<start_of_turn>system
Create a new and unique Python practice question about {concept} that is suitable for children.
The question must be directly related to the current topic. {beginner_note}
Ensure that the question is not a repetition of any previous questions.
Provide:
  - "question": a clear and simple practice prompt,
  - "answer": a flexible answer format where multiple acceptable answers are listed (for example, both "int" and "integer" should be accepted when asking about the data type of 5),
  - "hint": a short hint to help if the user is stuck.
Difficulty: Easy
Format: {{"question": "...", "answer": "...", "hint": "..."}} 
Character style: {character}
<end_of_turn>
<start_of_turn>model\n"""
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 256,
            "temperature": 0.5
        }
    }
    
    try:
        response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = json.loads(response.content.decode("utf-8"))
        practice_text = result[0]['generated_text'].split("<start_of_turn>model\n")[-1]
        
        practice_data = re.search(r'\{.*?\}', practice_text, re.DOTALL)
        if practice_data:
            return eval(practice_data.group(0))
    except:
        return None
