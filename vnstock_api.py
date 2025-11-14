import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompt import SYSTEM_PROMPT
from tools import tool_call
from vnstock_functions import get_shareholders, get_officers, get_subsidiaries, get_historical_price

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("API key của Google chưa được thiết lập. Vui lòng tạo file .env")

client = genai.Client(api_key=GOOGLE_API_KEY)
app = FastAPI(title="VNStock Agent API", version="1.0")


class QueryRequest(BaseModel):
    queries: Union[str, List[str]]  


class QueryResponse(BaseModel):
    question: str
    answer: str

def handle_query(user_input: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[types.Content(role="user", parts=[types.Part(text=user_input)])],
        config=types.GenerateContentConfig(
            tools=tool_call,
            system_instruction=SYSTEM_PROMPT, 
        ),
    )

    part = response.candidates[0].content.parts[0]

    
    if hasattr(part, "function_call") and part.function_call:
        fn = part.function_call
        data = None

        if fn.name == "get_shareholders":
            data = get_shareholders(**fn.args)
        elif fn.name == "get_officers":
            data = get_officers(**fn.args)
        elif fn.name == "get_subsidiaries":
            data = get_subsidiaries(**fn.args)
        elif fn.name == "get_historical_price":
            data = get_historical_price(**fn.args)

        
        followup_prompt = f"Câu hỏi: {user_input}\nKết quả dữ liệu: {data}\nHãy trả lời chi tiết bằng ngôn ngữ tự nhiên."
        final_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[types.Content(role="user", parts=[types.Part(text=followup_prompt)])]
        )
        return final_response.candidates[0].content.parts[0].text

    else:
        
        return response.text


@app.post("/query", response_model=List[QueryResponse])
def query_agent(req: QueryRequest):
    if isinstance(req.queries, str):
        queries = [req.queries]
    else:
        queries = req.queries

    results = []
    for q in queries:
        answer = handle_query(q)
        results.append(QueryResponse(question=q, answer=answer))

    return results
