import requests

url = "http://127.0.0.1:8000/query"

payload = {
    "queries": [
        "Danh sách cổ đông lớn của VCB",
        "Danh sách ban lãnh đạo đang làm việc của VCB",
        "Các công ty con thuộc VCB",
        "Lấy dữ liệu OHLCV 10 ngày gần nhất HPG?",
        "Lấy giá đóng của của mã VCB từ đầu tháng 11 theo khung 1d?",
        "Trong các mã BID, TCB và VCB mã nào có giá mở cửa thấp nhất trong 10 ngày qua",
        "Tổng khối lượng giao dịch (volume) của mã VIC trong vòng 1 tuần gần đây",
        "So sánh khối lượng giao dịch của VIC với HPG trong 2 tuần gần đây"
    ]
}

response = requests.post(url, json=payload)
results = response.json()


output_file = "llm_test_results.txt"
with open(output_file, "w", encoding="utf-8") as f:
    for item in results:
        f.write(f"Câu hỏi: {item['question']}\n")
        f.write(f"Trả lời: {item['answer']}\n")
        f.write("-" * 80 + "\n")

print(f" Kết quả đã lưu vào file: {output_file}")
