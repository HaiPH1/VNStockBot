# agent.py
from google import genai
from tools import tool_call
from prompt import SYSTEM_PROMPT
from google.genai import types
from vnstock_functions import get_shareholders, get_officers, get_subsidiaries, get_historical_price

client = genai.Client(api_key="llllllllll")
def test_convs(convs):
    if isinstance(convs, str):
        convs = [convs]

    for user_input in convs:
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
            print(f"\nCâu hỏi: {user_input}")
            print("→ Model yêu cầu gọi hàm:", fn.name)
            print("→ Tham số:", fn.args)

            if fn.name == "get_shareholders":
                data = get_shareholders(**fn.args)
                #print("→ Kết quả thực tế:", data)
            elif fn.name == "get_officers":
                data =get_officers(**fn.args)
                #print("→ Kết quả thực tế:", data)
            elif fn.name == "get_subsidiaries":
                data =get_subsidiaries(**fn.args)
                #print("→ Kết quả thực tế:", data)
            elif fn.name == "get_historical_price":
                data =get_historical_price(**fn.args)
                #print("→ Kết quả thực tế:", data)

            followup_prompt = f"Câu hỏi: {user_input}\nKết quả dữ liệu: {data}\nHãy trả lời chi tiết bằng ngôn ngữ tự nhiên."

            final_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[types.Content(role="user", parts=[types.Part(text=followup_prompt)])]
            )

            print("→ Câu trả lời cuối cùng:", final_response.candidates[0].content.parts[0].text)
        else:
            print(f"\nCâu hỏi: {user_input}")
            print("→ Trả lời trực tiếp:", response.text)

if __name__ == "__main__":
    test_convs([
        "Lấy dữ liệu OHLCV 10 ngày gần nhất HPG?"
        " Danh sách cổ đông VCB",
        "Lãnh đạo đang làm việc VCB",
        "Giá từ 2023-10-01 đến 2023-10-31 HPG"
    ])



      