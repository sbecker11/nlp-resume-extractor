"""
This module extracts resume data from a document and returns it in JSON format using OpenAI's API.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from openai.ChatCompletion import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from src.content_loader import load_docx_data
from src.pydantic_resume import Resume

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-2024-08-06"

RESUME_TEXT = load_docx_data("resume.docx")


messages = [
    ChatCompletionSystemMessageParam(content="You are an expert assistant for taking 'Resume Text' from a document and returning the extracted resume data in JSON format. \nYou extract data from the given 'Resume Text' and return it in a JSON format that conforms to the 'Resume' response_format. \nREMEMBER to return extracted data only from provided 'Resume Text', and format the extracted data in JSON format as defined in the 'Resume' pydantic class"),
    ChatCompletionUserMessageParam(content=f"Resume Text: \n------\n{RESUME_TEXT}\n------")
]

response = client.beta.chat.completions.parse(
    model=MODEL,
    messages=messages,
    response_format=Resume
)

completion = response.choices[0].message['content']
if completion:
    print(completion)
else:
    print("No valid response received.")
    print(response)