import os
import abc
import json
import requests
import google.generativeai as genai
from typing import List, Dict, Any
from dotenv import load_dotenv

# Ensure env vars are loaded even if main.py didn't do it right
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

class LLMProvider(abc.ABC):
    @abc.abstractmethod
    async def generate_content(self, prompt: str) -> str:
        pass

    @abc.abstractmethod
    async def extract_data(self, raw_text: str, prompt_template: str) -> List[Dict[str, Any]]:
        pass

    @abc.abstractmethod
    async def interpret_command(self, user_message: str) -> Dict[str, str] | None:
        pass

class GeminiProvider(LLMProvider):
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
        genai.configure(api_key=api_key)
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.model = genai.GenerativeModel(model_name)

    async def generate_content(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

    async def extract_data(self, raw_text: str, prompt_template: str) -> List[Dict[str, Any]]:
        full_prompt = f"{prompt_template}\n\nDATA:\n{raw_text}"
        response = self.model.generate_content(full_prompt)
        text = response.text
        # Clean up markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text)

    async def interpret_command(self, user_message: str) -> Dict[str, str] | None:
        from prompts import COMMAND_INTERPRETER_PROMPT
        full_prompt = f"{COMMAND_INTERPRETER_PROMPT}\n\nUSER MESSAGE: {user_message}"
        response = self.model.generate_content(full_prompt)
        text = response.text.strip()
        
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        
        if text.lower() == "null":
            return None
            
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

class LocalLLMProvider(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama2" # Default, can be configurable

    async def generate_content(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            print(f"Error calling Local LLM: {e}")
            return "Error generating response."

    async def extract_data(self, raw_text: str, prompt_template: str) -> List[Dict[str, Any]]:
        full_prompt = f"{prompt_template}\n\nDATA:\n{raw_text}\n\nRespond ONLY with the JSON list."
        response_text = await self.generate_content(full_prompt)
        
        # Attempt to clean and parse JSON
        try:
            # Simple heuristic to find the first '[' and last ']'
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start != -1 and end != -1:
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                return []
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from Local LLM: {response_text}")
            return []

    async def interpret_command(self, user_message: str) -> Dict[str, str] | None:
        from prompts import COMMAND_INTERPRETER_PROMPT
        full_prompt = f"{COMMAND_INTERPRETER_PROMPT}\n\nUSER MESSAGE: {user_message}\n\nRespond ONLY with the JSON object or null."
        response_text = await self.generate_content(full_prompt)
        
        try:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = response_text[start:end]
                return json.loads(json_str)
            elif "null" in response_text.lower():
                return None
            else:
                return None
        except json.JSONDecodeError:
            return None

def get_llm_provider() -> LLMProvider:
    llm_type = os.getenv("LLM_TYPE", "CLOUD").upper()
    if llm_type == "LOCAL":
        return LocalLLMProvider()
    return GeminiProvider()
