import google.generativeai as genai
import time
import json
import os
from dotenv import load_dotenv
load_dotenv("GOOGLE_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)
from google.api_core import retry

gemini_retry = retry.Retry(
    initial=2.0,
    maximum=10.0,
    multiplier=1.0,
    deadline=60.0
)

class DermatologistBot:
    def __init__(self):
        system_instruction = "You are an expert dermatologist specializing in skin conditions."
        self.diagnose_model = genai.GenerativeModel("models/gemini-1.5-pro-latest", system_instruction=system_instruction, generation_config={"response_mime_type": "application/json"})
        self.chat_model = genai.GenerativeModel("models/gemini-1.5-pro-latest", system_instruction=system_instruction)
        self.transcript_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        self.messages = [] # Chat history
        self.prompt_diagnose = """\
Your patient has uploaded an additional media to help you diagnose. Analyze the file provided and come up with a possible diagnosis and a treatment plan. 
Provide the analysis in detailed paragraphs and include bullet points where necessary.
Using this JSON schema:
    SkinCondition = {
        "condition_name": str
        "symptoms": str
        "description": str
        "severity": str
        "common_treatments": str
        "recommendations": str
    }
Return a `SkinCondition`
"""
        return
    
    def update_user_info(self, user_info):
        system_instruction = f"""\
You are an expert dermatologist specializing in skin conditions.
You are being the consultant for the patient with following information:
- Age: {user_info['age']}
- Gender: {user_info['gender']}
- Location: {user_info['location']}
- Race: {user_info['race']}
"""
        self.diagnose_model = genai.GenerativeModel("models/gemini-1.5-pro-latest", system_instruction=system_instruction, generation_config={"response_mime_type": "application/json"})
        self.chat_model = genai.GenerativeModel("models/gemini-1.5-pro-latest", system_instruction=system_instruction)
        return 
    
    @gemini_retry
    def generate_response(self, prompt) -> str:
        self.messages.append({'role': 'user', 'parts': [prompt]})
        response = self.chat_model.generate_content(self.messages)
        self.messages.append(response.candidates[0].content)
        return response.text

    @gemini_retry
    def process_file(self, file_path) -> dict:
        
        # upload file
        file = genai.upload_file(path=file_path)

        # verify the API has successfully received the files
        while file.state.name == "PROCESSING":
            time.sleep(1)
            file = genai.get_file(file.name)

        if file.state.name == "FAILED":
            raise ValueError(file.state.name)
        
        # generate response
        prompt = self.prompt_diagnose
        self.messages.append({'role': 'user', 'parts': [file, prompt]})
        response = self.diagnose_model.generate_content(self.messages, request_options={"timeout": 60})
        self.messages.append(response.candidates[0].content)
        return json.loads(response.text)

    @gemini_retry
    def get_transcript(self, mime_type: str, audio_data: bytes) -> str:
        prompt = "Generate a transcript of the speech. If no speech transcript is available, return empty string."
        response = self.transcript_model.generate_content([
            prompt,
            {
                "mime_type": mime_type,
                "data": audio_data
            }
        ])
        return response.text.strip()
