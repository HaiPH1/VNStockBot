import os
import pandas as pd
import requests
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("API key của Google chưa được thiết lập. Vui lòng tạo file .env")

client = genai.Client(api_key=GOOGLE_API_KEY)

AGENT_API_URL = "http://127.0.0.1:8000/query"
EXCEL_FILE_PATH = "tests/AI Intern test questions.xlsx"

EVALUATION_PROMPT_TEMPLATE = """
Bạn là một giám khảo kiểm thử chất lượng cho một AI Agent tài chính.
Nhiệm vụ của bạn là đánh giá xem câu trả lời thực tế (`actual_answer`) từ Agent có đáp ứng đúng yêu cầu của người dùng (`question`) hay không.

QUY TẮC QUAN TRỌNG NHẤT:
- Dữ liệu tài chính (giá cổ phiếu, khối lượng giao dịch, chỉ số SMA/RSI) thay đổi liên tục theo thời gian, chỉ quan tâm dữ liệu có trả ra hay không, không cần xác thực dữ liệu.
- `expected_answer` chỉ là một VÍ DỤ về cấu trúc và loại thông tin đúng tại một thời điểm trong quá khứ.
- **ĐỪNG ĐÁNH FAIL** chỉ vì các con số trong `actual_answer` khác với `expected_answer`.
- **HÃY TẬP TRUNG** vào việc liệu `actual_answer` có đúng loại thông tin, đúng cấu trúc, và trả lời trúng vào câu hỏi của người dùng hay không. Ví dụ: hỏi về SMA thì câu trả lời phải có dữ liệu SMA.
- Dữ liệu mà bot trả về là dữ liệu từ API bên thứ 3, chỉ cần đảm bảo câu trả lời trả ra đúng loại thông tin mà người dùng yêu cầu, việc thừa thiếu thông tin hoặc độ chính xác của thông tin không đánh giá do đất là trách nhiệm của API cung cấp, không phải trách nhiệm của bot.

Dưới đây là dữ liệu cho ca kiểm thử:
-----------------------------------
- **Câu hỏi người dùng (question):** "{question}"
- **Câu trả lời kỳ vọng (expected_answer):** "{expected_answer}"
- **Câu trả lời thực tế (actual_answer):** "{actual_answer}"
-----------------------------------

Dựa vào các quy tắc trên, hãy đưa ra kết luận của bạn.
Câu trả lời của bạn PHẢI bắt đầu bằng một từ duy nhất: `PASS` hoặc `FAIL`, theo sau là một lời giải thích ngắn gọn (tối đa 2 câu).
"""

def call_agent_api(question: str) -> str:
    payload = {"queries": [question]}
    try:
        response = requests.post(AGENT_API_URL, json=payload, timeout=180)
        response.raise_for_status()
        return response.json()[0]["answer"]
    except requests.exceptions.RequestException as e:
        return (
            f"API Error: Unable to connect to Agent. "
            f"Ensure the server is running at {AGENT_API_URL}. Details: {e}"
        )


def evaluate_answer(question, expected_answer, actual_answer) -> (bool, str):
    prompt = EVALUATION_PROMPT_TEMPLATE.format(
        question=question,
        expected_answer=expected_answer,
        actual_answer=actual_answer,
    )
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
        )

        evaluation_text = response.text.strip()
        is_pass = evaluation_text.upper().startswith("PASS")
        return is_pass, evaluation_text

    except Exception as e:
        return False, f"LLM Evaluation Error: {e}"


def run_test_suite():
    print(" STARTING AUTOMATED TEST SUITE ".center(80, "="))

   
    try:
        df = pd.read_excel(EXCEL_FILE_PATH)
        df.dropna(subset=["question"], inplace=True)

        if df.empty:
            print("Warning: No valid test cases found in the Excel file.")
            return

        print(f"Loaded {len(df)} test cases from '{EXCEL_FILE_PATH}'.")
    except FileNotFoundError:
        print(f"Error: File '{EXCEL_FILE_PATH}' not found. Please verify the path.")
        return
    except Exception as e:
        print(f"Error while reading Excel file: {e}")
        return

    pass_count = 0
    test_results = []

    
    for index, row in df.iterrows():
        question = str(row["question"]).strip()
        expected_answer = str(row["expected_answer"]).strip()
        test_case_num = index + 1

        print(f"\n--- Test Case #{test_case_num}/{len(df)} ---")
        print(f"Question: {question}")

        start_time = time.time()
        actual_answer = call_agent_api(question)
        end_time = time.time()

        print(f"Response time: {end_time - start_time:.2f} seconds")
        print("Model Output:", actual_answer)
        print("*" * 10)

        is_pass, justification = evaluate_answer(
            question, expected_answer, actual_answer
        )

        if is_pass:
            pass_count += 1

        print(f"Evaluation: {justification}")

        test_results.append(
            {
                "case": test_case_num,
                "question": question,
                "result": "PASS" if is_pass else "FAIL",
                "justification": justification,
            }
        )

    
    print("\n" + " FINAL SUMMARY REPORT ".center(80, "="))
    total_tests = len(df)
    score = (pass_count / total_tests) * 100

    
    with open("test_results.json", "w") as f_w:
        json.dump(
            {
                "Acurancy": f"{score:.2f}%",  
                "test_results": test_results,
            },
            f_w,
            ensure_ascii=False,
            indent=4,
        )

    print(f"Total test cases: {total_tests}")
    print(f"Passed: {pass_count}")
    print(f"Failed: {total_tests - pass_count}")
    print(f"OVERALL SUCCESS RATE: {score:.2f}%")
    print("=" * 80)


if __name__ == "__main__":
    run_test_suite()
